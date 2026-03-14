# 3D Hydrologic Conceptual Models - Magallanes

Python and GIS workflow to resolve DGA Observations No. 6 and No. 7 for Magallanes basins, including:

- Basin-specific conceptual groundwater models (Obs. 6)
- Basin-specific conceptual surface-water models (Obs. 7)
- Comparative hydrologic balance
- Interactive 3D visual products (Leapfrog-style)
- Client transfer kit for reproducible delivery

## Study Scope

Basins covered:

- Rio Penitente
- Rio El Oro
- Rio Robalo

Main technical references and planning are documented in:

- 02 PyScripts Magallanes/PLAN_TRABAJO_OBS6_OBS7.md

## Repository Structure

Top-level folders:

- 00 DGA Bases: contractual and base documentation
- 00 IDIEM Tecnicos: technical annexes
- 01 Etapa 1: original study inputs and large source datasets
- 02 PyScripts Magallanes: Python workflow, generated figures, transfer kit
- 03 SIG Magallanes: SIG layers used in the conceptual models
- Editable_Inputs: optional override inputs for client-side edits

## Core Python Workflow

Main scripts are located in:

- 02 PyScripts Magallanes

Recommended execution order:

```bash
cd "02 PyScripts Magallanes"
python3 01_extraccion_datos_cuencas.py
python3 02_modelo_conceptual_subterraneo.py
python3 03_modelo_conceptual_superficial.py
python3 04_balance_hidrico_cuencas.py
python3 05_texto_observaciones_67.py
python3 08_descargar_dem_copernicus.py
python3 09_digitalizar_espesor_relleno.py
python3 10_pozos_acuifero.py
python3 11_mapa_pozos.py
python3 12_dataset_estratigrafico_UH.py
python3 07_mapa_3d_leapfrog.py
```

## 3D Viewer (ArcGIS Pro)

ArcGIS Pro support is included in:

- 02 PyScripts Magallanes/3ds ArcGIS Pro

Implemented approach:

- HTML models loaded as base64 data URIs
- JavaScript select element for model switching inside notebook iframe
- No Python widget callbacks required in ArcGIS Pro notebook runtime

Notebook entry point:

- 02 PyScripts Magallanes/3ds ArcGIS Pro/02_notebook_viewer.ipynb

## Transfer and Reproducibility Kit

Client handover toolkit:

- 02 PyScripts Magallanes/Kit_Transferencia_Cliente

Includes:

- environment setup scripts
- smoke test and full pipeline runners
- manifest/checksum generation
- delivery packaging scripts
- operational and troubleshooting documentation

## Tracked Figure Outputs

The repository tracks key final figure folders:

- 02 PyScripts Magallanes/Figuras_3D_Leapfrog
- 02 PyScripts Magallanes/Figuras_Obs6_ModeloSubterraneo

Other heavy/generated data remains excluded through .gitignore by design.

## Environment

Primary environment used in development:

- Python 3.9+
- geopandas, shapely, rasterio, scipy, numpy, pandas
- matplotlib, networkx, plotly, folium
- pyproj, pyshp, openpyxl, pyyaml

Quick setup (project virtual environment):

```bash
cd "/Users/carlosfloresarenas/Documents/Proyectos/Flores/IDIEM/01 Magallanes"
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
```

Or use the client kit setup script:

```bash
cd "02 PyScripts Magallanes/Kit_Transferencia_Cliente"
bash scripts/setup_env.sh
bash scripts/run_smoke_test.sh
```

## Current Status

- Obs. 6/7 technical workflow implemented and validated
- transfer packaging and checksums generated
- repository synchronized to GitHub (main)

## License and Data Notes

This repository contains project-specific materials for professional hydrologic studies. Verify contractual permissions before redistribution of source datasets and annex documentation.
