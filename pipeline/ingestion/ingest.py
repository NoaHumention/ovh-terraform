import logging
import boto3
from botocore.exceptions import ClientError
import os

# START

# CONFIGURATION
#     source_directory = raw_data/
#     bronze_bucket = ...

# CONNECT
#     get Object Storage credentials
#     create S3-compatible client

# INGEST
#     find all files in source_directory

#     FOR each file:
#         filename = ...
#         bronze_key = ...

#         upload file to bronze_bucket using bronze_key

#         IF upload succeeded:
#             log success
#         ELSE:
#             log error

# END

source_directory = "raw_data/"

# Get bronze bucket name from terraform variable
bronze_bucket = "infra/modules/storage/output.tf"

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


