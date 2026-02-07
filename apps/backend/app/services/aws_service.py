from fastapi import UploadFile
import boto3
from ..core.config import get_settings

settings = get_settings()

class AWS_Service:
    def __init__(self):
        self.s3_client = boto3.client(
            service_name='s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    def upload_to_s3(self, file: UploadFile) -> str:
        """Common S3 upload logic"""
        try:
            self.s3_client.put_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=file.filename,
                Body=file.file
            )
            
            return f"{settings.AWS_BUCKET_URL}{file.filename}"
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
    
    async def delete_from_s3(self, file_url: str):
        """Common S3 delete logic"""
        try:
            key = file_url.split('/')[-1]
            self.s3_client.delete_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=key
            )
        except Exception as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")