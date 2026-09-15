from typing import TypedDict, List, Dict, Any

class AgentGraphState(TypedDict):
    user_query: str                  
    selected_file: str               
    schema_footprint: str            
    retrieved_context: List[str]     
    generated_code: str              
    execution_result: Any            
    error_log: str                   
    retry_counter: int               
    final_insight: str               
