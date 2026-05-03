#!/usr/bin/env bash
# Build Angular, write S3 app-config (API Gateway base URL + API token), sync to the frontend bucket.
# Usage: ./infra/scripts/publish_frontend.sh <api_base_url> <s3_bucket_name> [api_token]
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend"
DIST_DIR="${FRONTEND_DIR}/dist/frontend/browser"

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <api_base_url> <s3_bucket_name> [api_token]" >&2
  exit 1
fi

API_BASE="$1"
BUCKET="$2"
API_TOKEN="${3:-}"

if [[ -z "${API_BASE// }" ]]; then
  echo "api_base_url is empty." >&2
  exit 1
fi

if [[ ! "${API_BASE}" =~ ^https?:// ]]; then
  echo "api_base_url must start with http:// or https://. Got: ${API_BASE}" >&2
  exit 1
fi

if [[ -z "${BUCKET// }" ]]; then
  echo "s3_bucket_name is empty." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not on PATH." >&2
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI is not on PATH." >&2
  exit 1
fi

pushd "${FRONTEND_DIR}" >/dev/null
npm ci
npm run build
popd >/dev/null

if [[ ! -d "${DIST_DIR}" ]]; then
  echo "Expected build output at ${DIST_DIR} but it is missing." >&2
  exit 1
fi

# Write app-config.js with API base URL and optional token
printf "window.assetManagementConfig = {\n  apiBaseUrl: '%s',\n  apiToken: '%s'\n};\n" \
  "${API_BASE}" "${API_TOKEN}" > "${DIST_DIR}/app-config.js"

aws s3 sync "${DIST_DIR}/" "s3://${BUCKET}/" --delete
echo "Uploaded frontend to s3://${BUCKET}/"
