#!/usr/bin/env bash
set -e
python3 -m venv venv || true
source venv/bin/activate || true
pip install -r requirements.txt || true
python app.py