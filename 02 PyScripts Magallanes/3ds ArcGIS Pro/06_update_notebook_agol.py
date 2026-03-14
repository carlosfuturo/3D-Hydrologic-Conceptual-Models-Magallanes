"""
06_update_notebook_agol.py
==========================
Actualiza el contenido del notebook ya existente en AGOL
(item 70f742bf784e4304aa18950c0c0045a6) con la versión local actualizada.

Uso:
    python 06_update_notebook_agol.py
"""

from pathlib import Path
import requests
from arcgis.gis import GIS

PORTAL_URL  = "https://idiem.maps.arcgis.com"
USERNAME    = "carlos_hidrofuturo"
NOTEBOOK_ID = "70f742bf784e4304aa18950c0c0045a6"
NOTEBOOK    = Path(__file__).parent / "02_notebook_viewer.ipynb"

print(f"Conectando a {PORTAL_URL} …")
password = input("Contraseña AGOL: ")
gis = GIS(PORTAL_URL, USERNAME, password)
token = gis._con.token
print(f"  Conectado como: {gis.properties.user.username}\n")

print(f"Actualizando notebook (item {NOTEBOOK_ID}) …")
resp = requests.post(
    f"{PORTAL_URL}/sharing/rest/content/users/{USERNAME}/items/{NOTEBOOK_ID}/update",
    data={
        "text":  NOTEBOOK.read_text(encoding="utf-8"),
        "f":     "json",
        "token": token,
    },
    timeout=60,
)
result = resp.json()
if result.get("success"):
    print(f"  ✓ Notebook actualizado")
    print(f"    URL: {PORTAL_URL}/home/notebook/notebook.html?id={NOTEBOOK_ID}")
else:
    print(f"  ✗ Error: {result.get('error', result)}")
