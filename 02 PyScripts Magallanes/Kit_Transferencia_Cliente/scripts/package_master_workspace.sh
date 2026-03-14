#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="$(cd "${KIT_DIR}/.." && pwd)"
ROOT_DIR="$(cd "${PROJECT_DIR}/.." && pwd)"
ROOT_PARENT="$(dirname "${ROOT_DIR}")"
ROOT_NAME="$(basename "${ROOT_DIR}")"
OUT_DIR="${KIT_DIR}/output/master_$(date +%Y%m%d_%H%M%S)"
MASTER_ZIP="${OUT_DIR}/${ROOT_NAME}_MASTER.zip"

mkdir -p "${OUT_DIR}"

pushd "${ROOT_PARENT}" >/dev/null
zip -r "${MASTER_ZIP}" "${ROOT_NAME}" \
  -x "${ROOT_NAME}/.git/*" \
     "${ROOT_NAME}/.venv/*" \
     "${ROOT_NAME}/**/.venv/*" \
     "${ROOT_NAME}/**/.venv_cliente/*" \
     "${ROOT_NAME}/**/__pycache__/*" \
     "${ROOT_NAME}/**/.DS_Store" \
     "${ROOT_NAME}/02 PyScripts Magallanes/Kit_Transferencia_Cliente/output/*"
popd >/dev/null

if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "${MASTER_ZIP}" > "${OUT_DIR}/sha256_master.txt"
fi

echo "[master] OK: ${MASTER_ZIP}"
