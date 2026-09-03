"""Cron entry point: checks raw_data/ for new or changed files and, if any
are found, runs the full pipeline (ingest -> process -> curate -> embed).

Meant to be invoked on a schedule (e.g. every 10 minutes by Windows Task
Scheduler) rather than run as a long-lived loop, so each invocation does one
check-and-maybe-run and exits.
"""

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from run_pipeline import run_pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "raw_data"
STATE_DIR = Path(__file__).resolve().parent / ".state"
MANIFEST_PATH = STATE_DIR / "raw_data_manifest.json"
LOG_PATH = STATE_DIR / "watch.log"

STATE_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("watch_and_run")
logger.setLevel(logging.INFO)
# run_pipeline (imported below) also calls logging.basicConfig(), which
# attaches a handler to the root logger. Without this, every message here
# would propagate up and get printed a second time.
logger.propagate = False
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=2)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def scan_raw_data() -> dict:
    """Snapshot of every file in raw_data/: name -> (size, mtime)."""
    if not RAW_DATA_DIR.is_dir():
        return {}

    return {
        f.name: {"size": f.stat().st_size, "mtime": f.stat().st_mtime}
        for f in RAW_DATA_DIR.iterdir()
        if f.is_file()
    }


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {}

    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("Manifest file was corrupt, treating as empty")
        return {}


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def find_changes(previous: dict, current: dict) -> list[str]:
    """Names of files that are new, or whose size/mtime changed."""
    return [
        name
        for name, info in current.items()
        if previous.get(name) != info
    ]


def main() -> None:
    previous_manifest = load_manifest()
    current_manifest = scan_raw_data()

    changed_files = find_changes(previous_manifest, current_manifest)

    if not changed_files:
        logger.info("No new or changed files in raw_data/, skipping pipeline")
        return

    logger.info(
        "Detected %d new/changed file(s) in raw_data/: %s",
        len(changed_files),
        ", ".join(changed_files)
    )

    success = run_pipeline()

    if success:
        save_manifest(current_manifest)
        logger.info("Pipeline succeeded, manifest updated")
    else:
        logger.error(
            "Pipeline failed, manifest NOT updated so the next run retries "
            "these files"
        )


if __name__ == "__main__":
    main()
