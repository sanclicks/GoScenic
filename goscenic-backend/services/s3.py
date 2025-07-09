import os
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError

BUCKET_NAME = os.getenv("AWS_S3_BUCKET", "goscenic-bucket")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def upload_file(file_path: str, key: str) -> str:
    """Upload a file to S3 and return the public URL."""
    try:
        s3_client.upload_file(file_path, BUCKET_NAME, key, ExtraArgs={"ACL": "public-read"})
        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
        return url
    except (BotoCoreError, NoCredentialsError) as e:
        raise RuntimeError(str(e))

