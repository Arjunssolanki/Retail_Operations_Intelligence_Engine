import streamlit as st
import pandas as pd
import os
from s3_manager import S3DataLakeManager
from data_processor import TabularDataProcessor
from vector_store import ChromaStorageEngine
from graph_engine import RetailGraphEngine
from logger_config import get_logger

logger = get_logger("streamlit_app")

st.set_page_config(page_title="Retail Intelligence Engine", layout="wide")

st.markdown("# 🏭 Retail Operations Intelligence Engine")
st.markdown("### Production-Grade Agentic Big Data Pipeline with LangGraph & MLflow")

@st.cache_resource
def initialize_core_services():
    logger.info("Initializing core system service instances.")
    s3 = S3DataLakeManager()
    vector_db = ChromaStorageEngine()
    return s3, vector_db

s3_client, vector_db_client = initialize_core_services()

if "datasets" not in st.session_state:
    st.session_state.datasets = {}
if "index_built" not in st.session_state:
    st.session_state.index_built = False

with st.sidebar:
    st.header("⚙️ Cloud Data Lake Status")
    
    if st.button("📡 Sync & Ingest from AWS S3"):
        with st.spinner("Streaming big data matrices into memory context..."):
            try:
                available_files = s3_client.list_available_datasets()
                
                for file_key in ["products.csv", "customers.csv", "sales.csv"]:
                    if file_key in available_files:
                        df = s3_client.stream_csv_to_dataframe(file_key)
                        st.session_state.datasets[file_key] = df
                st.success("✅ Ingestion Completed! Dataframes held in system memory.")
            except Exception as e:
                st.sidebar.error(f"Ingestion crashed: {e}")
                
    st.markdown("---")
    st.markdown("### Data Inventory Tracking")
    if st.session_state.datasets:
        for name, df in st.session_state.datasets.items():
            st.metric(label=f"📊 {name}", value=f"{df.shape[0]:,} Rows")
    else:
        st.info("No active cloud tables loaded yet.")

if st.session_state.datasets and not st.session_state.index_built:
    st.info("💡 Data lake loaded. Proceed with Vector Index baseline alignment.")
    if st.button("🏗️ Build Hybrid Semantic Vector Space"):
        with st.spinner("Processing relational text mappings into ChromaDB..."):
            success = False
            try:
                if "products.csv" in st.session_state.datasets:
                    prod_docs = TabularDataProcessor.transform_metadata_table(
                        st.session_state.datasets["products.csv"], "product", "Product_ID"
                    )
                    vector_db_client.populate_index(prod_docs)
                    
                if "customers.csv" in st.session_state.datasets:
                    customer_sample_df = st.session_state.datasets["customers.csv"].head(5)
                    cust_docs = TabularDataProcessor.transform_metadata_table(
                        customer_sample_df, "customer", "Customer_ID"
                    )
                    vector_db_client.populate_index(cust_docs)
                    
                st.session_state.index_built = True
                success = True
            except Exception as e:
                st.error(f"Vector setup crashed: {e}")
                
            if success:
                st.rerun()

if st.session_state.index_built:
    st.markdown("---")
    st.markdown("### 💬 Query the Operations Analyst")
    
    sample_queries = [
        "What was the total revenue across all transactions?",
        "Find the top 3 spending customers and tell me which cities they are from",
        "Which product category generated the highest sales revenue?",
        "What is the average rating for transactions paid using UPI?"
    ]
    
    selected_sample = st.selectbox("💡 Try a sample operational query:", [""] + sample_queries)
    user_query = st.text_input("✍️ Or enter a custom business analyst question:", value=selected_sample)
    
    if st.button("🚀 Execute Agent Analysis"):
        if not user_query:
            st.warning("Please specify a query parameter request to evaluate.")
        else:
            with st.spinner("LangGraph Engine executing self-correcting analysis loop..."):
                try:
                    graph_agent = RetailGraphEngine(st.session_state.datasets)
                    
                    final_state = graph_agent.run_monitored_pipeline(user_query)
                    
                    st.subheader("💡 Analytical Insights")
                    st.info(final_state.get("final_insight"))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="🔄 Self-Correction Retries Required", value=final_state.get("retry_counter", 0))
                    with col2:
                        st.success("🎯 Analytics Telemetry Logged to MLflow Dashboard!")
                        
                    with st.expander("🛠️ Execution Code Trace"):
                        st.markdown("**Executed Pandas Data Manipulation Pipeline Code:**")
                        st.code(final_state.get("generated_code"), language="python")
                        st.markdown("**Calculated Raw Context Outputs:**")
                        st.write(final_state.get("execution_result"))
                        
                    if os.path.exists("workflow_flowchart.png"):
                        with st.expander("🎨 View Live System Graph Architecture"):
                            st.image("workflow_flowchart.png")
                            
                except Exception as e:
                    st.error(f"An execution lifecycle fault occurred: {e}")
