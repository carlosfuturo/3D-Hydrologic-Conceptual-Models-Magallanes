"""
07_make_public_agol.py
======================
Hace públicos los 4 modelos 3D (acceso sin login) y genera una
página índice HTML local con links directos a cada modelo.

Uso:
    python 07_make_public_agol.py
"""

import json
from pathlib import Path

import requests
from arcgis.gis import GIS

PORTAL_URL = "https://idiem.maps.arcgis.com"
USERNAME   = "carlos_hidrofuturo"
JSON_PATH  = Path(__file__).parent / "notas" / "agol_item_urls.json"
INDEX_OUT  = Path(__file__).parent / "notas" / "index_modelos_3d.html"

print(f"Conectando a {PORTAL_URL} …")
password = input("Contraseña AGOL: ")
gis = GIS(PORTAL_URL, USERNAME, password)
token = gis._con.token
print(f"  Conectado: {gis.properties.user.username}\n")

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

links = []
for titulo, info in data.items():
    item_id = info.get("item_id")
    if not item_id:
        continue

    # Compartir con Everyone (público)
    resp = requests.post(
        f"{PORTAL_URL}/sharing/rest/content/users/{USERNAME}/shareItems",
        data={
            "items":    item_id,
            "everyone": "true",
            "org":      "true",
            "f":        "json",
            "token":    token,
        },
        timeout=30,
    )
    result = resp.json()
    results_list = result.get("results", [{}])
    ok = results_list[0].get("success") if results_list else False

    if ok:
        url_data = f"{PORTAL_URL}/sharing/rest/content/items/{item_id}/data"
        info["url_public"] = url_data
        print(f"✓ Público: {titulo}")
        links.append((titulo, url_data))
    else:
        print(f"✗ Error en {titulo}: {result}")

# Actualizar JSON
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Generar página índice HTML
li_items = "\n".join(
    f'    <li><a href="{url}" target="_blank">{titulo}</a></li>'
    for titulo, url in links
)
html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Magallanes 3D — Modelos Interactivos</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 700px; margin: 60px auto; }}
    h1   {{ color: #0070c0; }}
    li   {{ margin: 12px 0; font-size: 1.1em; }}
    a    {{ color: #0070c0; }}
  </style>
</head>
<body>
  <h1>Magallanes — Modelos 3D Interactivos</h1>
  <p>Proyecto hidrogeológico IDIEM. Haz clic en cada modelo para abrirlo:</p>
  <ul>
{li_items}
  </ul>
  <p style="color:gray;font-size:0.85em">Generado el 2026-03-13 · Portal: {PORTAL_URL}</p>
</body>
</html>"""

INDEX_OUT.write_text(html, encoding="utf-8")
print(f"\nPágina índice generada:\n  {INDEX_OUT}")
print("\nComparte ese HTML o los links directos con el cliente DGA.")
