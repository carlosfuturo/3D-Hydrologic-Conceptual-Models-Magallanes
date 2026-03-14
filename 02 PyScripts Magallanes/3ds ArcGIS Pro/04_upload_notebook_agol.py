"""
04_upload_notebook_agol.py
==========================
Sube 02_notebook_viewer.ipynb a AGOL como ítem tipo Notebook.

Uso:
    python 04_upload_notebook_agol.py
"""

import json
from pathlib import Path

import requests
from arcgis.gis import GIS

# ---------------------------------------------------------------------------
PORTAL_URL = "https://idiem.maps.arcgis.com"
USERNAME   = "carlos_hidrofuturo"
FOLDER_ID  = "c6cef0a9df6540f7835f0e54ff3daac4"   # carpeta Magallanes_3D

NOTEBOOK   = Path(__file__).parent / "02_notebook_viewer.ipynb"
TITULO     = "Magallanes 3D - Visor Interactivo"
TAGS       = "Magallanes,3D,Plotly,Hidrología,IDIEM,Notebook"
SNIPPET    = "Visor interactivo de modelos 3D del proyecto hidrogeológico Magallanes (IDIEM)"
# ---------------------------------------------------------------------------

print(f"Conectando a {PORTAL_URL} como {USERNAME} …")
password = input("Contraseña AGOL: ")
gis = GIS(PORTAL_URL, USERNAME, password)
print(f"  Conectado como: {gis.properties.user.username}\n")

token = gis._con.token
add_url = (
    f"{PORTAL_URL}/sharing/rest/content/users/{USERNAME}/{FOLDER_ID}/addItem"
)

print(f"Subiendo '{TITULO}' …")
with open(NOTEBOOK, "rb") as fh:
    resp = requests.post(
        add_url,
        data={
            "title":    TITULO,
            "type":     "Notebook",
            "tags":     TAGS,
            "snippet":  SNIPPET,
            "text":     NOTEBOOK.read_text(encoding="utf-8"),
            "f":        "json",
            "token":    token,
        },
        timeout=60,
    )

result = resp.json()
if not result.get("success"):
    print(f"✗ Error: {result.get('error', result)}")
else:
    item_id = result["id"]

    # Compartir con la organización
    requests.post(
        f"{PORTAL_URL}/sharing/rest/content/users/{USERNAME}/shareItems",
        data={"items": item_id, "org": "true", "f": "json", "token": token},
        timeout=30,
    )

    url_item = f"{PORTAL_URL}/home/item.html?id={item_id}"
    url_open = f"{PORTAL_URL}/home/notebook/notebook.html?id={item_id}"
    print(f"  ✓ Item ID: {item_id}")
    print(f"    URL item:   {url_item}")
    print(f"    Abrir NB:   {url_open}")

    # Guardar en el JSON de resultados
    json_path = Path(__file__).parent / "notas" / "agol_item_urls.json"
    data = {}
    if json_path.exists():
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    data[TITULO] = {
        "item_id":  item_id,
        "url_item": url_item,
        "url_open": url_open,
        "archivo":  NOTEBOOK.name,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n  Guardado en {json_path}")
