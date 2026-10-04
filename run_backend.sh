#!/usr/bin/env bash
python3 -m uvicorn backend_main:app --reload --host 127.0.0.1 --port 8000
