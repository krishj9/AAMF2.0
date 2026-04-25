#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"

MODE="${1:-local}"
PORT="${PORT:-8000}"

if [[ "${MODE}" != "local" && "${MODE}" != "aws" ]]; then
  echo "Usage: $0 [local|aws]" >&2
  exit 1
fi

export DYNAMODB_MODE="${MODE}"
if [[ "${MODE}" == "local" ]]; then
  export DYNAMODB_ENDPOINT_URL="${DYNAMODB_ENDPOINT_URL:-http://localhost:55000}"
else
  unset DYNAMODB_ENDPOINT_URL || true
fi

cd "${BACKEND_DIR}"
exec uv run uvicorn app.main:app --reload --host 0.0.0.0 --port "${PORT}"
