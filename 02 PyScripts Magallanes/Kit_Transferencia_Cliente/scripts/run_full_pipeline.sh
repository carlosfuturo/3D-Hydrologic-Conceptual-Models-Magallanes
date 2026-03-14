#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="$(cd "${KIT_DIR}/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv_cliente"
LOG_DIR="${KIT_DIR}/output"
LOG_FILE="${LOG_DIR}/run_full_pipeline_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "${LOG_DIR}"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[run] No existe ${VENV_DIR}. Ejecuta scripts/setup_env.sh primero."
  exit 1
fi

source "${VENV_DIR}/bin/activate"

pushd "${PROJECT_DIR}" >/dev/null

echo "[run] Iniciando pipeline completo" | tee -a "${LOG_FILE}"

declare -a steps=(
  "python 01_extraccion_datos_cuencas.py"
  "python 02_modelo_conceptual_subterraneo.py"
  "python 03_modelo_conceptual_superficial.py"
  "python 04_balance_hidrico_cuencas.py"
  "python 05_texto_observaciones_67.py"
  "python 08_descargar_dem_copernicus.py"
  "python 09_digitalizar_espesor_relleno.py"
  "python 10_pozos_acuifero.py"
  "python 11_mapa_pozos.py"
  "python 12_dataset_estratigrafico_UH.py"
  "python 07_mapa_3d_leapfrog.py"
)

for cmd in "${steps[@]}"; do
  echo "[run] >>> ${cmd}" | tee -a "${LOG_FILE}"
  eval "${cmd}" 2>&1 | tee -a "${LOG_FILE}"
done

echo "[run] Pipeline finalizado sin errores" | tee -a "${LOG_FILE}"
echo "[run] Log: ${LOG_FILE}"

popd >/dev/null
