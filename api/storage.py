import boto3
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

s3_client = boto3.client(
    "s3",
    endpoint_url=os.getenv("NEON_STORAGE_ENDPOINT"),
    aws_access_key_id=os.getenv("NEON_STORAGE_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("NEON_STORAGE_SECRET_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

BUCKET = os.getenv("NEON_STORAGE_BUCKET")


def upload_file(file_bytes: bytes, filename: str, user_id: str) -> str:
    """Upload un PDF dans Neon Storage et retourne son URL."""
    key = f"{user_id}/{filename}"
    
    s3_client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=file_bytes,
        ContentType="application/pdf"
    )
    
    return key


def download_file(key: str) -> bytes:
    """Télécharge un fichier depuis Neon Storage."""
    response = s3_client.get_object(Bucket=BUCKET, Key=key)
    return response["Body"].read()