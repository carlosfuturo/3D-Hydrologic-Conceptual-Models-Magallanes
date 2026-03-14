from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR_PATH = Path(os.environ.get("MAGALLANES_BASE_DIR", SCRIPT_DIR.parent)).resolve()
PY_SCRIPTS_DIR_PATH = BASE_DIR_PATH / "02 PyScripts Magallanes"
EDITABLE_INPUTS_DIR_PATH = Path(
    os.environ.get("MAGALLANES_EDITABLE_INPUTS_DIR", BASE_DIR_PATH / "Editable_Inputs")
).resolve()

BASE_DIR = str(BASE_DIR_PATH)
PY_SCRIPTS_DIR = str(PY_SCRIPTS_DIR_PATH)
EDITABLE_INPUTS_DIR = str(EDITABLE_INPUTS_DIR_PATH)

INPUT_CATALOG = [
    {"category": "perhc", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/area_estudio_total.shp"},
    {"category": "perhc", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/cuenca_rio_penitente.shp"},
    {"category": "perhc", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/cuenca_rio_del_oro.shp"},
    {"category": "perhc", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/cuenca_rio_robalo.shp"},
    {"category": "perhc", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/red_hidro_penitente.shp"},
    {"category": "perhc", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/red_hidro_oro.shp"},
    {"category": "perhc", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/red_hidro_robalo.shp"},
    {"category": "perhc", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/hidro_masas_lacustres.shp"},
    {"category": "raster", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/05_Raster/EZ_DEM_penitente.shp"},
    {"category": "raster", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/05_Raster/EZ_DEM_oro.shp"},
    {"category": "raster", "relative_path": "01 Etapa 1/Anexos/Anexo E - SIG/05_Raster/EZ_DEM_robalo.shp"},
    {"category": "sig3d", "relative_path": "03 SIG Magallanes/Lagunas.shp"},
    {"category": "sig3d", "relative_path": "03 SIG Magallanes/propsBOT_Vertientes_Proj.shp"},
    {"category": "sig3d", "relative_path": "03 SIG Magallanes/propsBOT_Fuego_Proj.shp"},
    {"category": "pozos", "relative_path": "01 Etapa 1/Antecedentes/Pozos/Consolidado Pozos/Derechos_de_Agua.xlsx"},
    {"category": "pozos", "relative_path": "01 Etapa 1/Antecedentes/Pozos/DDAA_subte.xlsx"},
    {"category": "pozos", "relative_path": "01 Etapa 1/Antecedentes/Pozos/pozo_nuevo.shp"},
    {"category": "pozos", "relative_path": "01 Etapa 1/Antecedentes/MEE/Rio_Oro.csv"},
    {"category": "datasets", "relative_path": "02 PyScripts Magallanes/data_set_oferta_hidrica.xlsx"},
    {"category": "datasets", "relative_path": "02 PyScripts Magallanes/datos_cuencas.json"},
    {"category": "datasets", "relative_path": "02 PyScripts Magallanes/pozos_acuifero.csv"},
    {"category": "datasets", "relative_path": "02 PyScripts Magallanes/pozos_acuifero.geojson"},
    {"category": "dem", "relative_path": "02 PyScripts Magallanes/DEM_Copernicus_30m/mosaicos/DEM_Cop30_Penitente_UTM19S.tif"},
    {"category": "dem", "relative_path": "02 PyScripts Magallanes/DEM_Copernicus_30m/mosaicos/DEM_Cop30_El_Oro_UTM19S.tif"},
    {"category": "dem", "relative_path": "02 PyScripts Magallanes/DEM_Copernicus_30m/mosaicos/DEM_Cop30_Robalo_UTM19S.tif"},
    {"category": "dem", "relative_path": "02 PyScripts Magallanes/DEM_Copernicus_30m/espesor_relleno/EspesorRelleno_Regional.tif"},
    {"category": "dem", "relative_path": "02 PyScripts Magallanes/DEM_Copernicus_30m/espesor_relleno/EspesorRelleno_Penitente.tif"},
    {"category": "dem", "relative_path": "02 PyScripts Magallanes/DEM_Copernicus_30m/espesor_relleno/EspesorRelleno_El_Oro.tif"},
    {"category": "dem", "relative_path": "02 PyScripts Magallanes/input/Figura6_17_EspesorRelleno.png"},
]


def _as_relative_path(path: str | os.PathLike[str]) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(BASE_DIR_PATH)
        except ValueError:
            return candidate
    return candidate


def resolve_input(path: str | os.PathLike[str]) -> str:
    rel = _as_relative_path(path)
    if rel.is_absolute():
        return str(rel)
    override = EDITABLE_INPUTS_DIR_PATH / rel
    if override.exists():
        return str(override)
    return str(BASE_DIR_PATH / rel)


def editable_target(path: str | os.PathLike[str]) -> Path:
    rel = _as_relative_path(path)
    if rel.is_absolute():
        raise ValueError(f"No se puede derivar target editable para ruta externa: {path}")
    return EDITABLE_INPUTS_DIR_PATH / rel


def ensure_editable_root() -> Path:
    EDITABLE_INPUTS_DIR_PATH.mkdir(parents=True, exist_ok=True)
    return EDITABLE_INPUTS_DIR_PATH


def iter_catalog() -> Iterable[dict[str, str]]:
    return INPUT_CATALOG


def write_catalog_csv(dest: str | os.PathLike[str]) -> None:
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with dest_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "relative_path"])
        writer.writeheader()
        writer.writerows(INPUT_CATALOG)
