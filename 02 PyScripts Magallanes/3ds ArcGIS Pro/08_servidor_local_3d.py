"""
08_servidor_local_3d.py
=======================
Levanta un servidor HTTP local con página índice para visualizar
los modelos 3D desde cualquier navegador en la misma red.

Uso:
    python 08_servidor_local_3d.py

Luego abrir en el navegador:
    http://localhost:8080
    o desde otra máquina en la misma red:
    http://<tu-ip>:8080
"""

import http.server
import os
import socket
import threading
from pathlib import Path

PORT    = 8080
HTML_DIR = Path(__file__).parent.parent / "Figuras_3D_Leapfrog"

MODELOS = [
    ("Modelo Combinado (3 cuencas)", "3D_Leapfrog_COMBO_3Cuencas.html"),
    ("Cuenca Penitente",             "3D_Leapfrog_Penitente.html"),
    ("Cuenca El Oro",                "3D_Leapfrog_El_Oro.html"),
    ("Cuenca Robalo",                "3D_Leapfrog_Robalo.html"),
]

# Generar index.html en la carpeta de figuras
INDEX = HTML_DIR / "index.html"
li_items = "\n".join(
    f'    <li><a href="{archivo}">{titulo}</a></li>'
    for titulo, archivo in MODELOS
    if (HTML_DIR / archivo).exists()
)
INDEX.write_text(f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Magallanes 3D — Modelos Interactivos</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 700px;
            margin: 60px auto; background: #f5f7fa; }}
    h1   {{ color: #0070c0; border-bottom: 2px solid #0070c0; padding-bottom: 8px; }}
    ul   {{ list-style: none; padding: 0; }}
    li   {{ margin: 14px 0; }}
    a    {{ display: block; background: #fff; border: 1px solid #cce;
            border-radius: 6px; padding: 14px 20px; color: #0070c0;
            text-decoration: none; font-size: 1.1em;
            box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
    a:hover {{ background: #e8f0fe; }}
    .footer {{ color: #999; font-size: .8em; margin-top: 40px; }}
  </style>
</head>
<body>
  <h1>Magallanes — Modelos 3D Interactivos</h1>
  <p>Proyecto hidrogeológico IDIEM · Seleccionar modelo:</p>
  <ul>
{li_items}
  </ul>
  <p class="footer">Generado con 07_mapa_3d_leapfrog.py · IDIEM 2026</p>
</body>
</html>""", encoding="utf-8")

# Servidor
os.chdir(HTML_DIR)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

ip = get_local_ip()
handler = http.server.SimpleHTTPRequestHandler

print("=" * 55)
print("  Magallanes 3D — Servidor de modelos interactivos")
print("=" * 55)
print(f"\n  Abre en tu navegador:")
print(f"    Local:  http://localhost:{PORT}")
print(f"    Red:    http://{ip}:{PORT}")
print(f"\n  Modelos disponibles:")
for titulo, archivo in MODELOS:
    if (HTML_DIR / archivo).exists():
        print(f"    · {titulo}")
print("\n  Ctrl+C para detener el servidor.\n")

with http.server.HTTPServer(("", PORT), handler) as httpd:
    httpd.serve_forever()
