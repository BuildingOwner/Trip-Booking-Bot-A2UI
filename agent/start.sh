#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
uvicorn src.main:app --reload --port 8003 --host 0.0.0.0
