#!/bin/bash
# Launcher for the Windows Task Scheduler entry: runs watch_and_run.py
# inside WSL, where terraform and the project's venv actually live.
set -e
cd "$(dirname "${BASH_SOURCE[0]}")/.."
.venv/bin/python3 pipeline/watch_and_run.py
