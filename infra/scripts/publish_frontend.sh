#!/usr/bin/env bash
# Build Angular, write S3 app-config (API Gateway base URL), sync to the frontend bucket.
# Usage: ./infra/scripts/publish_frontend.sh <api_base_url> <s3_bucket_name>
# Example: ./infra/scripts/publish_frontend.sh "$(terraform -chdir=infra/terraform/environments/dev output -raw api_base_url)" "$(terraform -chdir=infra/terraform/environments/dev output -raw frontend_bucket_name)"
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend"
DIST_DIR="${FRONTEND_DIR}/dist/frontend/browser"

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <api_base_url> <s3_bucket_name>" >&2
  exit 1
fi

API_BASE="$1"
BUCKET="$2"

if [[ -z "${API_BASE// }" ]]; then
  echo "api_base_url is empty. Pass your API Gateway base URL (e.g. terraform output -raw api_base_url)." >&2
  exit 1
fi

if [[ ! "${API_BASE}" =~ ^https?:// ]]; then
  echo "api_base_url must start with http:// or https://. Got: ${API_BASE}" >&2
  exit 1
fi

if [[ -z "${BUCKET// }" ]]; then
  echo "s3_bucket_name is empty. Pass your frontend bucket (e.g. terraform output -raw frontend_bucket_name)." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not on PATH; install Node.js/npm to build the frontend." >&2
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI is not on PATH; install it to upload to S3." >&2
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

printf "window.assetManagementConfig = {\n  apiBaseUrl: '%s'\n};\n" "${API_BASE}" > "${DIST_DIR}/app-config.js"

aws s3 sync "${DIST_DIR}/" "s3://${BUCKET}/" --delete
echo "Uploaded frontend to s3://${BUCKET}/"
