"""
01_upload_htmls_agol.py
=======================
Sube los modelos 3D Plotly (HTML autocontenidos) al portal AGOL
idiem.maps.arcgis.com y guarda los item IDs/URLs en notas/agol_item_urls.json.

Uso:
    python 01_upload_htmls_agol.py

Requisitos:
    pip install arcgis
"""

import json
import os
import shutil
import tempfile
from pathlib import Path

import requests
from arcgis.gis import GIS

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------
PORTAL_URL = "https://idiem.maps.arcgis.com"
USERNAME   = "carlos_hidrofuturo"
FOLDER     = "Magallanes_3D"          # Carpeta en AGOL Content (se crea si no existe)

# Ruta base del proyecto (relativa a este script)
BASE = Path(__file__).parent.parent
HTML_DIR = BASE / "Figuras_3D_Leapfrog"
OUTPUT_JSON = Path(__file__).parent / "notas" / "agol_item_urls.json"

# Modelos a subir: título AGOL → archivo HTML
ARCHIVOS = {
    "Magallanes 3D - Cuenca Penitente":      "3D_Leapfrog_Penitente.html",
    "Magallanes 3D - Cuenca El Oro":         "3D_Leapfrog_El_Oro.html",
    "Magallanes 3D - Cuenca Robalo":         "3D_Leapfrog_Robalo.html",
    "Magallanes 3D - Modelo Combinado":      "3D_Leapfrog_COMBO_3Cuencas.html",
}

TAGS    = "Magallanes,3D,Plotly,Hidrología,IDIEM"
SNIPPET = "Modelo 3D del proyecto hidrogeológico Magallanes (IDIEM)"

# ---------------------------------------------------------------------------
# CONEXIÓN
# ---------------------------------------------------------------------------
print(f"Conectando a {PORTAL_URL} como {USERNAME} …")
password = input("Contraseña AGOL: ")
gis = GIS(PORTAL_URL, USERNAME, password)
print(f"  Conectado como: {gis.properties.user.username}\n")

# Obtener o crear carpeta (API arcgis 3.x)
folder_obj = None
for f in gis.content.folders.list():
    # arcgis 3.x Folder usa .name o .properties["title"]
    folder_name = getattr(f, "name", None) or getattr(f, "title", None)
    if folder_name == FOLDER:
        folder_obj = f
        break

if folder_obj is None:
    folder_obj = gis.content.folders.create(FOLDER)
    print(f"  Carpeta '{FOLDER}' creada.\n")
else:
    print(f"  Carpeta '{FOLDER}' ya existe.\n")

# Obtener el folder ID (GUID) para el REST API
folder_id = getattr(folder_obj, "id", None) or getattr(folder_obj, "folder_id", None)
if folder_id is None:
    # último recurso: inspeccionar propiedades del objeto
    props = getattr(folder_obj, "properties", {}) or {}
    folder_id = props.get("id") or props.get("folderId", "")
print(f"  Folder ID: {folder_id}\n")

# ---------------------------------------------------------------------------
# SUBIDA
# ---------------------------------------------------------------------------
resultados = {}

for titulo, archivo in ARCHIVOS.items():
    ruta = HTML_DIR / archivo
    if not ruta.exists():
        print(f"[OMITIDO] {archivo} — archivo no encontrado en {HTML_DIR}")
        continue

    size_mb = ruta.stat().st_size / 1_048_576
    print(f"Subiendo '{titulo}' ({size_mb:.1f} MB) …")

    try:
        token = gis._con.token

        # AGOL no acepta HTML suelto — empaquetar como ZIP con index.html
        tmp_dir = tempfile.mkdtemp()
        zip_path = Path(tmp_dir) / "app.zip"
        inner_dir = Path(tmp_dir) / "app"
        inner_dir.mkdir()
        shutil.copy(ruta, inner_dir / "index.html")
        shutil.make_archive(str(zip_path.with_suffix("")), "zip", str(inner_dir))

        add_url = (
            f"{PORTAL_URL}/sharing/rest/content/users/{USERNAME}"
            f"/{folder_id}/addItem"
        )
        with open(zip_path, "rb") as fh:
            resp = requests.post(
                add_url,
                data={
                    "title":       titulo,
                    "type":        "Web Mapping Application",
                    "typeKeywords": "JavaScript,Map,Mapping Site",
                    "tags":        TAGS,
                    "snippet":     SNIPPET,
                    "description": (
                        f"Modelo 3D interactivo generado con Plotly para el proyecto "
                        f"hidrogeológico Magallanes. Archivo fuente: {archivo}."
                    ),
                    "f":           "json",
                    "token":       token,
                },
                files={"file": ("app.zip", fh, "application/zip")},
                timeout=120,
            )
        shutil.rmtree(tmp_dir)
        result = resp.json()
        if not result.get("success"):
            raise RuntimeError(result.get("error", result))

        item_id = result["id"]

        # Compartir con la organización
        share_url = (
            f"{PORTAL_URL}/sharing/rest/content/users/{USERNAME}/shareItems"
        )
        requests.post(
            share_url,
            data={"items": item_id, "org": "true", "f": "json", "token": token},
            timeout=30,
        )

        url_app = f"{PORTAL_URL}/home/item.html?id={item_id}"
        resultados[titulo] = {
            "item_id":  item_id,
            "url_data": f"{PORTAL_URL}/sharing/rest/content/items/{item_id}/data",
            "url_item": url_app,
            "archivo":  archivo,
            "size_mb":  round(size_mb, 2),
        }
        print(f"  ✓ Item ID: {item_id}")
        print(f"    URL item:  {url_app}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

# ---------------------------------------------------------------------------
# GUARDAR RESULTADOS
# ---------------------------------------------------------------------------
OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"\nResultados guardados en:\n  {OUTPUT_JSON}")
print(f"\nTotal subidos: {len(resultados)} / {len(ARCHIVOS)}")
