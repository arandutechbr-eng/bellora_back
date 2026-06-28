#!/usr/bin/env bash
# Render — repo bellora_back (raiz = back/)
set -euo pipefail
cd "$(dirname "$0")/backend"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
