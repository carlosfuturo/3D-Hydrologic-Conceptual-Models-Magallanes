"""
03_publish_scene_layers.py
==========================
(FASE 2 — requiere ArcGIS Pro instalado localmente)

Publica las capas de datos espaciales como Scene Layers nativos en AGOL,
reemplazando los IFrame con vistas 3D nativas del portal.

REQUISITOS:
    - ArcGIS Pro con licencia activa
    - arcpy disponible en el entorno Python de ArcGIS Pro
    - Conexión al portal idiem.maps.arcgis.com

CAPAS A PUBLICAR:
    dem_penitente  → ElevationLayer  (desde GeoTIFF DEM_Copernicus_30m/)
    dem_el_oro     → ElevationLayer  (desde GeoTIFF DEM_Copernicus_30m/)
    dem_robalo     → ElevationLayer  (desde GeoTIFF DEM_Copernicus_30m/)
    pozos          → FeatureLayer 3D (desde pozos_acuifero.geojson)
    lagunas        → FeatureLayer 3D (desde shapefiles SIG)
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# RUTAS (relativas a este script)
# ---------------------------------------------------------------------------
BASE      = Path(__file__).parent.parent
DEM_DIR   = BASE / "DEM_Copernicus_30m"
SIG_DIR   = BASE.parent / "03 SIG Magallanes"

CAPAS = {
    "dem_penitente": {
        "tipo":    "ElevationLayer",
        "archivo": DEM_DIR / "DEM_Penitente_30m.tif",     # ajustar nombre real
        "titulo":  "Magallanes - DEM Penitente 30m",
    },
    "dem_el_oro": {
        "tipo":    "ElevationLayer",
        "archivo": DEM_DIR / "DEM_ElOro_30m.tif",
        "titulo":  "Magallanes - DEM El Oro 30m",
    },
    "dem_robalo": {
        "tipo":    "ElevationLayer",
        "archivo": DEM_DIR / "DEM_Robalo_30m.tif",
        "titulo":  "Magallanes - DEM Robalo 30m",
    },
    "pozos": {
        "tipo":    "FeatureLayer3D",
        "archivo": BASE / "pozos_acuifero.geojson",
        "titulo":  "Magallanes - Pozos Acuífero 3D",
        "z_field": "nivel_freatico_m",
    },
    "lagunas": {
        "tipo":    "FeatureLayer3D",
        "archivo": SIG_DIR / "Lagunas.shp",               # ajustar si existe
        "titulo":  "Magallanes - Lagunas 3D",
    },
}

# ---------------------------------------------------------------------------
# VERIFICACIÓN DE ARCHIVOS FUENTE
# ---------------------------------------------------------------------------
print("Verificando archivos fuente para Fase 2:\n")
faltantes = []
for nombre, info in CAPAS.items():
    existe = info["archivo"].exists()
    estado = "✓" if existe else "✗ NO ENCONTRADO"
    print(f"  [{estado}] {nombre}")
    print(f"           {info['archivo']}")
    if not existe:
        faltantes.append(nombre)

print()
if faltantes:
    print(f"⚠  Faltan {len(faltantes)} archivos. Completar antes de publicar.")
else:
    print("Todos los archivos fuente presentes.")
    print("Para publicar, ejecutar este script desde el entorno Python de ArcGIS Pro.")

# ---------------------------------------------------------------------------
# PUBLICACIÓN (descomentar cuando arcpy esté disponible)
# ---------------------------------------------------------------------------
# import arcpy
# from arcgis.gis import GIS
#
# PORTAL_URL = "https://idiem.maps.arcgis.com"
# USERNAME   = "carlos_hidrofuturo"
# gis = GIS(PORTAL_URL, USERNAME, input("Contraseña AGOL: "))
#
# for nombre, info in CAPAS.items():
#     if not info["archivo"].exists():
#         continue
#     print(f"Publicando {nombre} como {info['tipo']} …")
#     # Lógica de publicación según tipo de capa
#     # Ver: https://developers.arcgis.com/python/guide/publishing-sd-files-and-web-layers/
