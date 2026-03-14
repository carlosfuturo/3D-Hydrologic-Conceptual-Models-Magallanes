#!/usr/bin/env bash
set -euo pipefail

# Genera paquetes de transferencia para cliente:
# - Core: codigo, configuracion, docs y salidas principales
# - Full: incluye ademas insumos pesados (DEM y otros)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="$(cd "${KIT_DIR}/.." && pwd)"
OUT_DIR="${KIT_DIR}/output/delivery_$(date +%Y%m%d_%H%M%S)"

mkdir -p "${OUT_DIR}"

PROJECT_NAME="Magallanes_Obs6_Obs7"
CORE_ZIP="${OUT_DIR}/${PROJECT_NAME}_CORE.zip"
FULL_ZIP="${OUT_DIR}/${PROJECT_NAME}_FULL.zip"

pushd "${PROJECT_DIR}" >/dev/null

# Exclusiones globales
EXCLUDES=(
  "*/.git/*"
  "*/.venv/*"
  "*/.venv_cliente/*"
  "*/__pycache__/*"
  "*/.DS_Store"
  "*/Kit_Transferencia_Cliente/output/*"
)

# Paquete CORE
zip -r "${CORE_ZIP}" \
  "01_extraccion_datos_cuencas.py" \
  "02_modelo_conceptual_subterraneo.py" \
  "03_modelo_conceptual_superficial.py" \
  "04_balance_hidrico_cuencas.py" \
  "05_texto_observaciones_67.py" \
  "07_mapa_3d_leapfrog.py" \
  "08_descargar_dem_copernicus.py" \
  "09_digitalizar_espesor_relleno.py" \
  "10_pozos_acuifero.py" \
  "11_mapa_pozos.py" \
  "12_dataset_estratigrafico_UH.py" \
  "datos_cuencas.json" \
  "pozos_acuifero.csv" \
  "pozos_acuifero.geojson" \
  "dataset_estratigrafico_UH.csv" \
  "Figuras_3D_Leapfrog" \
  "Figuras_Obs6_ModeloSubterraneo" \
  "Figuras_Obs7_ModeloSuperficial" \
  "Figuras_Obs6_Obs7_Balance" \
  "Texto_Correcciones_Obs67" \
  "3ds ArcGIS Pro" \
  "Kit_Transferencia_Cliente" \
  -x "${EXCLUDES[@]}"

# Paquete FULL (todo 02 PyScripts Magallanes excepto exclusiones)
zip -r "${FULL_ZIP}" . \
  -x "${EXCLUDES[@]}"

# Checksums de paquetes
if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "${CORE_ZIP}" > "${OUT_DIR}/sha256_core.txt"
  shasum -a 256 "${FULL_ZIP}" > "${OUT_DIR}/sha256_full.txt"
fi

popd >/dev/null

echo "[package] OK"
echo "[package] Carpeta salida: ${OUT_DIR}"
echo "[package] Core: ${CORE_ZIP}"
echo "[package] Full: ${FULL_ZIP}"
