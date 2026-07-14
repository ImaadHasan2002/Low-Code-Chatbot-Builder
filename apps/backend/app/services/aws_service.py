from pathlib import Path
from urllib.parse import unquote, urlparse
from uuid import uuid4

from fastapi import UploadFile

from ..core.config import get_settings

settings = get_settings()
LOCAL_UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
LOCAL_UPLOAD_URL_PATH = "/uploads"


class S3NotConfiguredError(RuntimeError):
    def __init__(self):
        super().__init__(
            "AWS S3 is not configured. Set AWS_ACCESS_KEY_ID, "
            "AWS_SECRET_ACCESS_KEY, AWS_REGION and AWS_BUCKET_NAME in your .env file."
        )


class AWS_Service:
    """S3 wrapper. The boto3 client is created lazily so the app can boot
    without AWS credentials; uploads use local storage when S3 is not set."""

    def __init__(self):
        self._s3_client = None

    @property
    def is_configured(self) -> bool:
        return bool(
            settings.AWS_ACCESS_KEY_ID
            and settings.AWS_SECRET_ACCESS_KEY
            and settings.AWS_BUCKET_NAME
        )

    @property
    def s3_client(self):
        if self._s3_client is None:
            if not self.is_configured:
                raise S3NotConfiguredError()
            import boto3

            self._s3_client = boto3.client(
                service_name="s3",
                region_name=settings.AWS_REGION or None,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
        return self._s3_client

    def upload_to_s3(self, file: UploadFile) -> str:
        """Upload a file to S3 and return its public URL.

        In local/dev setups without S3 credentials, store the file on disk and
        return a backend-served URL so the PDF knowledge-base flow still works.
        """
        if not self.is_configured:
            return self._upload_to_local_storage(file)

        try:
            self.s3_client.put_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=file.filename,
                Body=file.file,
            )
            return f"{settings.AWS_BUCKET_URL}{file.filename}"
        except S3NotConfiguredError:
            raise
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")

    async def delete_from_s3(self, file_url: str):
        """Delete a file from S3 or local fallback storage given its URL."""
        if not self.is_configured or LOCAL_UPLOAD_URL_PATH in urlparse(file_url).path:
            self._delete_from_local_storage(file_url)
            return

        try:
            key = file_url.split("/")[-1]
            self.s3_client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=key)
        except S3NotConfiguredError:
            raise
        except Exception as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")

    def _upload_to_local_storage(self, file: UploadFile) -> str:
        LOCAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        original_name = Path(file.filename or "upload.pdf").name
        safe_name = "".join(
            char if char.isalnum() or char in {".", "-", "_"} else "-"
            for char in original_name
        ).strip(".-") or "upload.pdf"
        key = f"{uuid4().hex}-{safe_name}"
        destination = LOCAL_UPLOAD_DIR / key

        file.file.seek(0)
        with destination.open("wb") as out_file:
            while chunk := file.file.read(1024 * 1024):
                out_file.write(chunk)
        file.file.seek(0)

        return f"{settings.BACKEND_URL.rstrip('/')}{LOCAL_UPLOAD_URL_PATH}/{key}"

    def _delete_from_local_storage(self, file_url: str) -> None:
        parsed = urlparse(file_url)
        key = Path(unquote(parsed.path)).name
        if not key:
            return

        candidate = LOCAL_UPLOAD_DIR / key
        if candidate.exists() and candidate.is_file():
            candidate.unlink()
