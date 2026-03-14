"""
05_set_app_urls_agol.py
=======================
Configura el campo URL de cada Web Mapping Application subida a AGOL,
lo que activa el botón "View Application" en la página del ítem.

Uso:
    python 05_set_app_urls_agol.py
"""

import json
from pathlib import Path

import requests
from arcgis.gis import GIS

PORTAL_URL = "https://idiem.maps.arcgis.com"
USERNAME   = "carlos_hidrofuturo"
JSON_PATH  = Path(__file__).parent / "notas" / "agol_item_urls.json"

print(f"Conectando a {PORTAL_URL} como {USERNAME} …")
password = input("Contraseña AGOL: ")
gis = GIS(PORTAL_URL, USERNAME, password)
token = gis._con.token
print(f"  Conectado como: {gis.properties.user.username}\n")

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

for titulo, info in data.items():
    item_id = info.get("item_id")
    if not item_id:
        continue

    # URL que abre directamente el HTML (Plotly 3D)
    app_url = f"{PORTAL_URL}/sharing/rest/content/items/{item_id}/data"

    resp = requests.post(
        f"{PORTAL_URL}/sharing/rest/content/users/{USERNAME}/items/{item_id}/update",
        data={
            "url":   app_url,
            "f":     "json",
            "token": token,
        },
        timeout=30,
    )
    result = resp.json()
    if result.get("success"):
        print(f"✓ {titulo}")
        print(f"    View Application → {app_url}")
        info["url_app"] = app_url
    else:
        print(f"✗ {titulo}: {result.get('error', result)}")

# Actualizar JSON
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"\nJSON actualizado: {JSON_PATH}")
