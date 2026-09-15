import mlflow
import os
from config import MLFLOW_EXPERIMENT_NAME

def verify_mlflow_setup():
    print("⏳ Connecting to local MLflow registry...")
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    
    with mlflow.start_run(run_name="MLflow_Sanity_Check") as run:
        print(f"✅ Active Run Initialized! ID: {run.info.run_id}")
        
        # Log System Attributes
        mlflow.log_param("infrastructure_status", "Active")
        mlflow.log_param("target_model", "gemini-2.5-flash")
        
        # Log Performance Metrics
        mlflow.log_metric("mock_latency_seconds", 0.452)
        mlflow.log_metric("mock_retry_count", 0)
        
        # Create a Mock Artifact File
        mock_artifact = "sample_test_trace.txt"
        with open(mock_artifact, "w") as f:
            f.write("System online. Tabular MLOps schema checks passing.")
            
        mlflow.log_artifact(mock_artifact)
        os.remove(mock_artifact)
        
    print("🎉 Smoke test successful! MLflow tracking is fully operational.")

if __name__ == "__main__":
    verify_mlflow_setup()
