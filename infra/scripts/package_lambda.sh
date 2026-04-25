#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="${ROOT_DIR}/infra/build"
UV_BIN="${UV_BIN:-$(command -v uv || true)}"
PYTHON_VERSION="${PYTHON_VERSION:-3.13}"
LAMBDA_BUILD_IMAGE="${LAMBDA_BUILD_IMAGE:-public.ecr.aws/sam/build-python3.13}"
USE_DOCKER="${USE_DOCKER:-auto}"

package_service() {
  local name="$1"
  local service_dir="$2"
  local build_path="${BUILD_DIR}/${name}"
  local zip_path="${BUILD_DIR}/${name}.zip"

  rm -rf "${build_path}" "${zip_path}"
  mkdir -p "${build_path}"

  if should_use_docker; then
    docker run --rm \
      --platform linux/amd64 \
      -v "${ROOT_DIR}:/asset-management" \
      -w "/asset-management" \
      "${LAMBDA_BUILD_IMAGE}" \
      bash -lc "python -m pip install --upgrade --target '/asset-management/infra/build/${name}' '/asset-management/${service_dir}' >/dev/null"
  elif [[ -n "${UV_BIN}" ]]; then
    "${UV_BIN}" pip install \
      --python "${PYTHON_VERSION}" \
      --target "${build_path}" \
      "${ROOT_DIR}/${service_dir}" >/dev/null
  else
    python3 -m pip install \
      --upgrade \
      --target "${build_path}" \
      "${ROOT_DIR}/${service_dir}" >/dev/null
  fi

  (cd "${build_path}" && zip -qr "${zip_path}" .)
  echo "Wrote ${zip_path}"
}

should_use_docker() {
  if [[ "${USE_DOCKER}" == "false" ]]; then
    return 1
  fi
  if [[ "${USE_DOCKER}" == "true" ]]; then
    return 0
  fi
  command -v docker >/dev/null 2>&1
}

mkdir -p "${BUILD_DIR}"
package_service "backend" "backend"
package_service "research-agent" "remote-agents/research-agent"
package_service "sentiment-mcp" "mcp-servers/sentiment"
