import json
import logging
import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import boto3
import psycopg2
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from pgvector.psycopg2 import register_vector
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INFRA_DIRECTORY = PROJECT_ROOT / "infra"

load_dotenv(PROJECT_ROOT / ".env")

# Dutch sentence-embedding model: RobBERT (KU Leuven). Runs locally.
# https://huggingface.co/NetherlandsForensicInstitute/robbert-2022-dutch-sentence-transformers
EMBEDDING_MODEL_NAME = "NetherlandsForensicInstitute/robbert-2022-dutch-sentence-transformers"
EMBEDDING_DIMENSIONS = 768


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


def ensure_schema(conn):
    """Create the pgvector extension and the chunks table if they don't exist yet."""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    # The extension must exist before pgvector's type adapter can look up
    # the "vector" type OID, so register it only after creating it.
    register_vector(conn)

    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id     TEXT PRIMARY KEY,
                doc_id       TEXT NOT NULL,
                source_file  TEXT,
                chunk_index  INTEGER,
                text         TEXT NOT NULL,
                embedding    VECTOR({EMBEDDING_DIMENSIONS}) NOT NULL
            );
        """)
    conn.commit()


def get_existing_chunk_ids(conn) -> set[str]:
    """Chunk IDs already embedded, so re-runs skip work that's already done."""
    with conn.cursor() as cur:
        cur.execute("SELECT chunk_id FROM chunks;")
        return {row[0] for row in cur.fetchall()}


def upsert_chunks(conn, rows: list[tuple]) -> None:
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO chunks (chunk_id, doc_id, source_file, chunk_index, text, embedding)
            VALUES %s
            ON CONFLICT (chunk_id) DO UPDATE SET
                doc_id      = EXCLUDED.doc_id,
                source_file = EXCLUDED.source_file,
                chunk_index = EXCLUDED.chunk_index,
                text        = EXCLUDED.text,
                embedding   = EXCLUDED.embedding;
            """,
            rows
        )
    conn.commit()


# Configuration
endpoint_url = os.environ["OVH_S3_ENDPOINT"]
access_key = os.environ["OVH_S3_ACCESS_KEY_EMBEDDING"]
secret_key = os.environ["OVH_S3_SECRET_KEY_EMBEDDING"]

pg_uri = os.environ["PG_VECTOR_URI"]
pg_db = os.environ["PG_VECTOR_DB"]
pg_user = os.environ["PG_VECTOR_USER"]
pg_password = os.environ["PG_VECTOR_PASSWORD"]

storage_names = get_storage_names()
gold_bucket = storage_names["gold"]


# Connect to Object Storage
s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

# Connect to the vector database.
# `cluster_uri` from the vectordb module may come back either as "host:port"
# or as a full "postgresql://host:port" URI depending on the OVH API, so
# handle both.
parsed_uri = urlsplit(pg_uri if "//" in pg_uri else f"//{pg_uri}")
pg_host, pg_port = parsed_uri.hostname, parsed_uri.port

conn = psycopg2.connect(
    host=pg_host,
    port=pg_port,
    dbname=pg_db,
    user=pg_user,
    password=pg_password,
    sslmode="require"
)
ensure_schema(conn)
already_embedded = get_existing_chunk_ids(conn)

# Load the embedding model once, up front.
logging.info("Loading embedding model %s ...", EMBEDDING_MODEL_NAME)
model = SentenceTransformer(EMBEDDING_MODEL_NAME)


# Embed
try:
    response = s3_client.list_objects_v2(Bucket=gold_bucket)
except ClientError as e:
    logging.error("Failed to list objects in Gold: %s", e)
    raise

for obj in response.get("Contents", []):
    object_name = obj["Key"]

    try:
        raw = s3_client.get_object(Bucket=gold_bucket, Key=object_name)
        chunk_records = json.loads(raw["Body"].read())
    except ClientError as e:
        logging.error("Failed to read %s from Gold: %s", object_name, e)
        continue

    new_records = [c for c in chunk_records if c["chunk_id"] not in already_embedded]
    if not new_records:
        logging.info("Skipping %s: all chunks already embedded", object_name)
        continue

    texts = [record["text"] for record in new_records]
    vectors = model.encode(texts, normalize_embeddings=True)

    rows = [
        (
            record["chunk_id"],
            record["doc_id"],
            record["source_file"],
            record["chunk_index"],
            record["text"],
            vector.tolist()
        )
        for record, vector in zip(new_records, vectors)
    ]

    try:
        upsert_chunks(conn, rows)
        already_embedded.update(row[0] for row in rows)

        logging.info(
            "Embedded %d chunks from %s -> vectordb",
            len(rows),
            object_name
        )

    except psycopg2.Error as e:
        logging.error(
            "Failed to upsert chunks from %s into vectordb: %s",
            object_name,
            e
        )
        conn.rollback()

conn.close()
