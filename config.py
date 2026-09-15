import os
from dotenv import load_dotenv

load_dotenv()

# Native Google GenAI Parameters (Updated to the latest version target)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL = "gemini-3.6-flash"  # <-- FIX: Swapped to the latest live version

# AWS S3 Data Lake Configurations
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "retail-operations-intelligence-engine-lake")

# Database & MLOps Tracking Properties
DB_DIR = "./chroma_db"
COLLECTION_NAME = "retail_intelligence_space"
LOG_FILE = "./logs/pipeline.log"
MLFLOW_EXPERIMENT_NAME = "Retail_Operations_Agentic_Pipeline"
