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


def load_all_chunks(s3_client, bucket: str) -> list[dict]:
    """Load every chunk record from every object in the Gold bucket."""
    all_chunks = []

    try:
        response = s3_client.list_objects_v2(Bucket=bucket)
    except ClientError as e:
        logging.error("Failed to list objects in Gold: %s", e)
        raise

    for obj in response.get("Contents", []):
        object_name = obj["Key"]

        try:
            raw = s3_client.get_object(Bucket=bucket, Key=object_name)
            chunks = json.loads(raw["Body"].read())
            all_chunks.extend(chunks)
        except ClientError as e:
            logging.error("Failed to read %s from Gold: %s", object_name, e)
            continue

    return all_chunks


def keyword_search(chunks: list[dict], query: str, top_k: int = 5) -> list[dict]:
    """
    Naive placeholder retriever: ranks chunks by keyword overlap.
    Replace with real vector similarity search once embeddings exist
    (e.g. cosine similarity against each chunk's embedding vector,
    or a proper vector DB like pgvector/Qdrant/Weaviate).
    """
    query_terms = set(query.lower().split())

    scored = []
    for chunk in chunks:
        text_terms = set(chunk["text"].lower().split())
        score = len(query_terms & text_terms)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


# Configuration
endpoint_url = os.environ["OVH_S3_ENDPOINT"]
access_key = os.environ["OVH_S3_ACCESS_KEY_ANALYTICS"]
secret_key = os.environ["OVH_S3_SECRET_KEY_ANALYTICS"]

storage_names = get_storage_names()
gold_bucket = storage_names["gold"]


# Connect
s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)


if __name__ == "__main__":
    chunks = load_all_chunks(s3_client, gold_bucket)
    logging.info("Loaded %d chunks from Gold", len(chunks))

    query = input("Enter your query: ")
    results = keyword_search(chunks, query)

    if not results:
        print("No matching chunks found.")

    for result in results:
        print(f"\n--- {result['chunk_id']} (source: {result['source_file']}) ---")
        print(result["text"][:300])