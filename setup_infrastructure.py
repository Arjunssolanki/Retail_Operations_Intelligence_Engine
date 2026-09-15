import boto3
from botocore.exceptions import ClientError
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, S3_BUCKET_NAME
from logger_config import get_logger

logger = get_logger("setup_infrastructure")

def verify_s3_data_lake():
    logger.info(f"Verifying access to AWS S3 bucket: '{S3_BUCKET_NAME}'")
    
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )
    
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        logger.info(f"Successfully verified ownership and access to bucket: '{S3_BUCKET_NAME}'")
        print(f"✅ Connection successful! Bucket '{S3_BUCKET_NAME}' is ready.")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            logger.error(f"Bucket '{S3_BUCKET_NAME}' was not found in region {AWS_DEFAULT_REGION}.")
            print(f"❌ Error: Bucket '{S3_BUCKET_NAME}' does not exist. Please check the name or complete creation in the AWS Console.")
        elif error_code == '403':
            logger.critical("Invalid AWS credentials or insufficient permissions to access this bucket.")
            print("❌ Error: Access Denied. Check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY inside your .env file.")
        else:
            logger.critical(f"Unexpected infrastructure verification failure: {str(e)}")
            print(f"❌ Error connecting to AWS: {e}")

if __name__ == "__main__":
    verify_s3_data_lake()
