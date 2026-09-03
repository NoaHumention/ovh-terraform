"""Runs the full bronze -> silver -> gold -> vectordb pipeline, in order.

Each stage is a standalone script (pipeline/ingestion/ingest.py, etc.), run
as a subprocess so that a failure in one stage stops the rest of the run
rather than leaving things half-updated.
"""

import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parents[1]

STAGES = [
    "pipeline.ingestion.ingest",
    "pipeline.processing.process",
    "pipeline.curation.curate",
    "pipeline.embedding.embed",
]


def run_pipeline() -> bool:
    """Run every stage in order. Returns True if all stages succeeded."""
    for stage in STAGES:
        logging.info("Running stage: %s", stage)

        result = subprocess.run(
            [sys.executable, "-m", stage],
            cwd=PROJECT_ROOT
        )

        if result.returncode != 0:
            logging.error(
                "Stage %s failed with exit code %d, stopping pipeline",
                stage,
                result.returncode
            )
            return False

    logging.info("Pipeline finished successfully")
    return True


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
