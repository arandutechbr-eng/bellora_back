#!/usr/bin/env bash
# Fallback se rootDir não estiver configurado (monorepo na raiz)
set -e
cd back/backend
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
