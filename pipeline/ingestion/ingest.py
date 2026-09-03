import json
import logging
import os
import subprocess
from pathlib import Path

import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INFRA_DIRECTORY = PROJECT_ROOT / "infra"
SOURCE_DIRECTORY = PROJECT_ROOT / "raw_data"

load_dotenv(PROJECT_ROOT / ".env")


def get_storage_names():
    result = subprocess.run(
        ["terraform", "output", "-json", "storage_names"],
        cwd=INFRA_DIRECTORY,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logging.error("Terraform command failed:")
        logging.error(result.stderr)
        raise RuntimeError("Could not retrieve Terraform storage names")

    return json.loads(result.stdout)


# Configuration
endpoint_url = os.environ["OVH_S3_ENDPOINT"]
access_key = os.environ["OVH_S3_ACCESS_KEY_INGESTION"]
secret_key = os.environ["OVH_S3_SECRET_KEY_INGESTION"]

storage_names = get_storage_names()
bronze_bucket = storage_names["bronze"]


# Connect
s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)


# Ingest
for file_path in SOURCE_DIRECTORY.iterdir():

    if not file_path.is_file():
        continue

    object_name = file_path.name

    try:
        s3_client.upload_file(
            str(file_path),
            bronze_bucket,
            object_name
        )

        logging.info(
            "Uploaded %s to Bronze",
            file_path
        )

    except ClientError as e:
        logging.error(
            "Failed to upload %s: %s",
            file_path,
            e
        )