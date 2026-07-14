import logging
import boto3
from botocore.exceptions import ClientError
import os


def upload_file_to_s3(s3_client, file, bucket):
    """Upload a file to an S3 bucket

    :param s3_client: S3 client
    :param file: File to upload (FastAPI UploadFile object)
    :param bucket: Bucket to upload to
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    # if object_name is None:
    #     object_name = os.path.basename(file.name)
    print(f"Uploading file to S3: {file.filename}")

    try:
        # Use put_object() instead of upload_file() since we have file content
        response = s3_client.put_object(
            Bucket=bucket,
            Key=file.filename,
            Body=file.file
        )
        return response['ResponseMetadata']['HTTPStatusCode'] == 200
    except ClientError as e:
        logging.error(e)
        return False