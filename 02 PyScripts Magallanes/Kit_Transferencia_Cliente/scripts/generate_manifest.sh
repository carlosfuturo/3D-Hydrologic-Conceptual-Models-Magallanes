#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="$(cd "${KIT_DIR}/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv_cliente"

if [[ -d "${VENV_DIR}" ]]; then
  source "${VENV_DIR}/bin/activate"
fi

python "${SCRIPT_DIR}/generate_manifest.py"
