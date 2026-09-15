import boto3
import pandas as pd
from io import StringIO
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, S3_BUCKET_NAME
from logger_config import get_logger

logger = get_logger("s3_manager")

class S3DataLakeManager:
    def __init__(self):
        logger.info("Initializing connection to AWS S3 Storage Space.")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION
        )
        self.bucket_name = S3_BUCKET_NAME

    def list_available_datasets(self) -> list:
        logger.info(f"Scanning files stored inside cloud bucket: '{self.bucket_name}'")
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if "Contents" in response:
                files = [obj["Key"] for obj in response["Contents"] if obj["Key"].endswith(".csv")]
                logger.info(f"Discovered {len(files)} target CSV datasets in cloud environment.")
                return files
            logger.warning("No files found inside the targeted S3 bucket context.")
            return []
        except Exception as err:
            logger.error(f"Failed to query S3 catalog metadata: {str(err)}")
            return []

    def stream_csv_to_dataframe(self, file_key: str) -> pd.DataFrame:
        logger.info(f"Streaming dataset stream target: {file_key}")
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            csv_content = response["Body"].read().decode("utf-8")
            df = pd.read_csv(StringIO(csv_content))
            logger.info(f"Stream successful. Cached dataframe matrix shape: {df.shape}")
            return df
        except Exception as err:
            logger.error(f"Critical block during memory ingestion of data target: {str(err)}")
            raise err
