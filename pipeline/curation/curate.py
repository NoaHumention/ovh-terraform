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

load_dotenv(PROJECT_ROOT / ".env")

CHUNK_SIZE = 800      # characters per chunk (tune for your embedding model)
CHUNK_OVERLAP = 100   # characters of overlap between consecutive chunks


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


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks of roughly chunk_size characters."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


# Configuration
endpoint_url = os.environ["OVH_S3_ENDPOINT"]
access_key = os.environ["OVH_S3_ACCESS_KEY_CURATION"]
secret_key = os.environ["OVH_S3_SECRET_KEY_CURATION"]

storage_names = get_storage_names()
silver_bucket = storage_names["silver"]
gold_bucket = storage_names["gold"]


# Connect
s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)


# Curate
try:
    response = s3_client.list_objects_v2(Bucket=silver_bucket)
except ClientError as e:
    logging.error("Failed to list objects in Silver: %s", e)
    raise

for obj in response.get("Contents", []):
    object_name = obj["Key"]

    try:
        raw = s3_client.get_object(Bucket=silver_bucket, Key=object_name)
        record = json.loads(raw["Body"].read())
    except ClientError as e:
        logging.error("Failed to read %s from Silver: %s", object_name, e)
        continue

    text = record.get("text", "")
    if not text:
        logging.error("Skipping %s: no text content", object_name)
        continue

    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

    doc_id = Path(object_name).stem

    gold_records = [
        {
            "doc_id": doc_id,
            "chunk_id": f"{doc_id}_{i}",
            "source_file": record.get("source_file"),
            "chunk_index": i,
            "text": chunk
            # embedding vectors would be generated and attached here,
            # e.g. chunk["embedding"] = embed_model.encode(chunk["text"])
        }
        for i, chunk in enumerate(chunks)
    ]

    gold_object_name = f"{doc_id}_chunks.json"
    json_bytes = json.dumps(gold_records, ensure_ascii=False).encode("utf-8")

    try:
        s3_client.put_object(
            Bucket=gold_bucket,
            Key=gold_object_name,
            Body=json_bytes,
            ContentType="application/json"
        )

        logging.info(
            "Curated %s into %d chunks -> Gold as %s",
            object_name,
            len(gold_records),
            gold_object_name
        )

    except ClientError as e:
        logging.error(
            "Failed to upload %s to Gold: %s",
            gold_object_name,
            e
        )