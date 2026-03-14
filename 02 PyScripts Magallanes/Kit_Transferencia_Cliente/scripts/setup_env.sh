#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="$(cd "${KIT_DIR}/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv_cliente"

echo "[setup] Proyecto: ${PROJECT_DIR}"

echo "[setup] Creando entorno virtual en ${VENV_DIR}"
python3 -m venv "${VENV_DIR}"

source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r "${KIT_DIR}/requirements_cliente.txt"

if [[ ! -f "${KIT_DIR}/config/project_config.yaml" ]]; then
  cp "${KIT_DIR}/config/project_config.example.yaml" "${KIT_DIR}/config/project_config.yaml"
  echo "[setup] Se creo config/project_config.yaml desde plantilla."
fi

if [[ ! -f "${KIT_DIR}/config/.env" && -f "${KIT_DIR}/config/.env.example" ]]; then
  cp "${KIT_DIR}/config/.env.example" "${KIT_DIR}/config/.env"
  echo "[setup] Se creo config/.env desde plantilla."
fi

echo "[setup] Entorno listo. Activar con: source \"${VENV_DIR}/bin/activate\""
