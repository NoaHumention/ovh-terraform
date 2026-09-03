import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from pypdf import PdfReader


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INFRA_DIRECTORY = PROJECT_ROOT / "infra"

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


def extract_text(local_path: Path) -> str:
    """Extract raw text from a downloaded file, based on its extension."""
    suffix = local_path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(str(local_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    if suffix in (".txt", ".md", ".csv"):
        return local_path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError(f"Unsupported file type: {suffix}")


def clean_text(raw_text: str) -> str:
    """Basic cleanup: collapse whitespace, drop empty lines."""
    lines = [line.strip() for line in raw_text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


# Configuration
endpoint_url = os.environ["OVH_S3_ENDPOINT"]
access_key = os.environ["OVH_S3_ACCESS_KEY_PROCESSING"]
secret_key = os.environ["OVH_S3_SECRET_KEY_PROCESSING"]

storage_names = get_storage_names()
bronze_bucket = storage_names["bronze"]
silver_bucket = storage_names["silver"]


# Connect
s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)


# Process
try:
    response = s3_client.list_objects_v2(Bucket=bronze_bucket)
except ClientError as e:
    logging.error("Failed to list objects in Bronze: %s", e)
    raise

for obj in response.get("Contents", []):
    object_name = obj["Key"]

    with tempfile.TemporaryDirectory() as tmp_dir:
        local_path = Path(tmp_dir) / object_name

        try:
            s3_client.download_file(bronze_bucket, object_name, str(local_path))
        except ClientError as e:
            logging.error("Failed to download %s from Bronze: %s", object_name, e)
            continue

        try:
            raw_text = extract_text(local_path)
            cleaned = clean_text(raw_text)
        except ValueError as e:
            logging.error("Skipping %s: %s", object_name, e)
            continue

        record = {
            "source_file": object_name,
            "text": cleaned,
            "char_count": len(cleaned)
        }

        silver_object_name = f"{local_path.stem}.json"
        json_bytes = json.dumps(record, ensure_ascii=False).encode("utf-8")

        try:
            s3_client.put_object(
                Bucket=silver_bucket,
                Key=silver_object_name,
                Body=json_bytes,
                ContentType="application/json"
            )

            logging.info(
                "Processed %s to Silver as %s",
                object_name,
                silver_object_name
            )

        except ClientError as e:
            logging.error(
                "Failed to upload %s to Silver: %s",
                silver_object_name,
                e
            )