#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_DIR="$(cd "${KIT_DIR}/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv_cliente"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[smoke] No existe ${VENV_DIR}. Ejecuta scripts/setup_env.sh primero."
  exit 1
fi

source "${VENV_DIR}/bin/activate"

echo "[smoke] Verificando imports Python..."
python - <<'PY'
mods = [
    "numpy", "pandas", "geopandas", "shapely", "rasterio", "scipy",
    "matplotlib", "networkx", "plotly", "folium", "pyproj", "shapefile", "yaml"
]
missing = []
for m in mods:
    try:
        __import__(m)
    except Exception as exc:
        missing.append((m, str(exc)))

if missing:
    for m, e in missing:
        print(f"[smoke][ERROR] import {m}: {e}")
    raise SystemExit(2)

print("[smoke] Imports OK")
PY

echo "[smoke] Verificando archivos criticos..."
required=(
  "${PROJECT_DIR}/01_extraccion_datos_cuencas.py"
  "${PROJECT_DIR}/02_modelo_conceptual_subterraneo.py"
  "${PROJECT_DIR}/03_modelo_conceptual_superficial.py"
  "${PROJECT_DIR}/04_balance_hidrico_cuencas.py"
  "${PROJECT_DIR}/05_texto_observaciones_67.py"
  "${PROJECT_DIR}/07_mapa_3d_leapfrog.py"
  "${PROJECT_DIR}/08_descargar_dem_copernicus.py"
  "${PROJECT_DIR}/09_digitalizar_espesor_relleno.py"
  "${PROJECT_DIR}/10_pozos_acuifero.py"
  "${PROJECT_DIR}/11_mapa_pozos.py"
  "${PROJECT_DIR}/12_dataset_estratigrafico_UH.py"
  "${PROJECT_DIR}/datos_cuencas.json"
  "${PROJECT_DIR}/pozos_acuifero.csv"
)

for f in "${required[@]}"; do
  if [[ ! -e "${f}" ]]; then
    echo "[smoke][ERROR] Falta archivo: ${f}"
    exit 3
  fi
done

echo "[smoke] OK - ambiente y estructura validados"
