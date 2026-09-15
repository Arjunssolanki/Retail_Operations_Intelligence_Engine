import torch
import torch.nn as nn
import os
import time
import pandas as pd
import mlflow
from typing import Dict, Any, Literal
from google import genai
from google.genai import types
from langgraph.graph import StateGraph, START, END
from graph_state import AgentGraphState
from vector_store import ChromaStorageEngine
from config import GEMINI_API_KEY, LLM_MODEL, MLFLOW_EXPERIMENT_NAME
from logger_config import get_logger

logger = get_logger("graph_engine")

class RetailGraphEngine:
    def __init__(self, data_cache: Dict[str, pd.DataFrame]):
        logger.info("Initializing LangGraph engine structure with Native Google GenAI client.")
        
        if not GEMINI_API_KEY:
            logger.critical("CRITICAL: GEMINI_API_KEY was not found inside your .env file!")
            raise ValueError("Missing GEMINI_API_KEY in .env configuration.")
            
        self.datasets = data_cache
        self.vector_engine = ChromaStorageEngine()
        
        # Initialize the official native Google GenAI connection client
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
        self.workflow = self._compile_agent_graph()

    def _compile_agent_graph(self) -> StateGraph:
        builder = StateGraph(AgentGraphState)
        
        builder.add_node("context_retriever", self.node_retrieve_context)
        builder.add_node("code_generator", self.node_generate_code)
        builder.add_node("sandbox_executor", self.node_execute_sandbox)
        builder.add_node("insight_summarizer", self.node_summarize_insight)
        
        builder.add_edge(START, "context_retriever")
        builder.add_edge("context_retriever", "code_generator")
        builder.add_edge("code_generator", "sandbox_executor")
        
        builder.add_conditional_edges(
            "sandbox_executor",
            self.router_execution_check,
            {
                "retry": "code_generator",
                "proceed": "insight_summarizer"
            }
        )
        builder.add_edge("insight_summarizer", END)
        
        return builder.compile()

    def run_monitored_pipeline(self, query: str) -> Dict[str, Any]:
        initial_state: AgentGraphState = {
            "user_query": query,
            "selected_file": "multi-table-lake",
            "schema_footprint": "",
            "retrieved_context": [],
            "generated_code": "",
            "execution_result": None,
            "error_log": "",
            "retry_counter": 0,
            "final_insight": ""
        }
        
        run_name = f"Query_Run_{int(time.time())}"
        with mlflow.start_run(run_name=run_name) as run:
            logger.info(f"MLflow Run started: {run.info.run_id}")
            
            mlflow.log_param("user_query", query)
            mlflow.log_param("llm_model", LLM_MODEL)
            
            start_time = time.time()
            final_state = self.workflow.invoke(initial_state)
            latency = time.time() - start_time
            
            mlflow.log_metric("total_latency_seconds", round(latency, 3))
            mlflow.log_metric("sandbox_retry_count", final_state.get("retry_counter", 0))
            
            code_log_path = "generated_analysis_pipeline.py"
            with open(code_log_path, "w") as f:
                f.write(final_state.get("generated_code", "# No code built"))
            mlflow.log_artifact(code_log_path)
            
            try:
                self.export_graph_flowchart()
                if os.path.exists("workflow_flowchart.png"):
                    mlflow.log_artifact("workflow_flowchart.png")
            except Exception as e:
                logger.warning(f"Failed to compile flowchart artifact: {e}")
                
            return final_state

    def node_retrieve_context(self, state: AgentGraphState) -> Dict[str, Any]:
        logger.info(f"Retrieving entity contexts for query: '{state['user_query']}'")
        found_docs = self.vector_engine.semantic_search(state["user_query"], n_results=3)
        flat_docs = [item for sublist in found_docs for item in sublist]
        return {"retrieved_context": flat_docs, "retry_counter": 0, "error_log": ""}

    def node_generate_code(self, state: AgentGraphState) -> Dict[str, Any]:
        logger.info("Generating data processing script options via Native Gemini SDK.")
        
        schema_summary = []
        for name, df in self.datasets.items():
            schema_summary.append(f"Table: '{name}' | Columns: {df.columns.tolist()} | Dimensions: {df.shape}")
        schema_str = "\n".join(schema_summary)
        
        error_context = ""
        if state.get("error_log"):
            error_context = f"\n⚠️ PREVIOUS CODE CRASHED WITH ERROR:\n{state['error_log']}\nFix the logic!"

        system_prompt = (
            "You are an expert Data Analyst AI. Write clean Python code using pandas to query dataframes.\n"
            "AVAILABLE DATAFRAMES:\n"
            f"{schema_str}\n\n"
            "CRITICAL PROTOCOLS:\n"
            "- Return ONLY valid Python code blocks wrapped inside ```python and ```.\n"
            "- Calculate the target value and assign it to a local variable named `result`.\n"
            "- If multiple dataframes are needed, join them on their common keys (e.g., Customer_ID or Product_ID).\n"
            "- Do not import os, sys, or subprocess."
        )
        
        response = self.client.models.generate_content(
            model=LLM_MODEL,
            contents=f"Context:\n{state['retrieved_context']}{error_context}\n\nQuestion: {state['user_query']}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0
            )
        )
        
        raw_code = response.text
        code = raw_code.split("```python")[-1].split("```")[0].strip() if "```python" in raw_code else raw_code.strip()
        return {"generated_code": code}

    def node_execute_sandbox(self, state: AgentGraphState) -> Dict[str, Any]:
        logger.info("Starting safe local code sandbox verification layout.")
        sandbox_env = {name: df for name, df in self.datasets.items()}
        
        try:
            exec(state["generated_code"], {}, sandbox_env)
            res = sandbox_env.get("result", "No explicit variable 'result' captured.")
            return {"execution_result": res, "error_log": ""}
        except Exception as err:
            logger.error(f"Sandbox runtime execution failed: {str(err)}")
            return {"error_log": str(err), "retry_counter": state.get("retry_counter", 0) + 1}

    def router_execution_check(self, state: AgentGraphState) -> Literal["retry", "proceed"]:
        if state.get("error_log") and state.get("retry_counter", 0) < 3:
            return "retry"
        return "proceed"

    def node_summarize_insight(self, state: AgentGraphState) -> Dict[str, Any]:
        logger.info("Synthesizing final business analysis metrics overview via Native Gemini Client.")
        
        if state.get("error_log"):
            return {"final_insight": f"Analysis halted after multiple execution attempts. Error trace: {state['error_log']}"}
            
        prompt = (
            f"Provide a professional business summary based on this computation:\n"
            f"User Question: {state['user_query']}\n"
            f"Calculated Metric Output: {state['execution_result']}\n\n"
            f"Write a crisp, corporate summary explaining the core takeaway from this finding."
        )
        
        response = self.client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        return {"final_insight": response.text}

    def export_graph_flowchart(self, output_path: str = "workflow_flowchart.png"):
        try:
            from langchain_core.runnables.graph import CurveStyle
            png_bytes = self.workflow.get_graph().draw_mermaid_png(curve_style=CurveStyle.BASIS)
            with open(output_path, "wb") as f:
                f.write(png_bytes)
            logger.info(f"Exported graph visual image using Mermaid engine: {output_path}")
        except Exception as e:
            logger.warning(f"Visual export skipped: {e}")
