"""
Script 08: Descarga DEM Copernicus GLO-30 (30m) — Región de Magallanes
Proyecto: Análisis de Recursos Hídricos - Cuencas Magallanes (IDIEM/DGA)

Propósito:
  Descarga automática del DEM Copernicus GLO-30 (30m) desde el bucket público
  de AWS para las 3 cuencas de estudio y la región de Magallanes completa.
  Fuente: Copernicus DEM GLO-30 — s3://copernicus-dem-30m/ (acceso público HTTPS)

  Por cada cuenca:
    - Identifica los tiles 1°×1° necesarios (coordenadas WGS84)
    - Descarga los GeoTIFF individuales
    - Fusiona en un mosaico por cuenca (clip al polígono de cuenca)
    - Reproyecta a EPSG:32719 (UTM 19S, sistema local del proyecto)

  También descarga la región completa de Magallanes (bbox regional).

Autor: Especialista Senior en Modelación
Fecha: 11-03-2026
"""

import os
import math
import time
import requests
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.crs import CRS
from pyproj import Transformer
from pathlib import Path
from project_paths import BASE_DIR as BASE, resolve_input

# ─────────────────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────────────────
DEM_SHP = os.path.join(BASE, "01 Etapa 1/Anexos/Anexo E - SIG/05_Raster")
OUT_DIR = os.path.join(BASE, "02 PyScripts Magallanes/DEM_Copernicus_30m")
TILES_D = os.path.join(OUT_DIR, "tiles_raw")
MOSAICS = os.path.join(OUT_DIR, "mosaicos")

for d in [OUT_DIR, TILES_D, MOSAICS]:
    os.makedirs(d, exist_ok=True)

# ─────────────────────────────────────────────────────────
# BBOXES POR CUENCA (UTM 19S / EPSG:32719)
# Los polígonos EZ_DEM_*.shp definen exactamente el límite
# ─────────────────────────────────────────────────────────
CUENCAS = {
    "Penitente": {
        "shp": resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/05_Raster/EZ_DEM_penitente.shp"),
        "bbox_utm": (292472, 4182059, 346639, 4247641),
    },
    "El_Oro": {
        "shp": resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/05_Raster/EZ_DEM_oro.shp"),
        "bbox_utm": (421409, 4083388, 454290, 4145423),
    },
    "Robalo": {
        "shp": resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/05_Raster/EZ_DEM_robalo.shp"),
        "bbox_utm": (581581, 3903801, 587699, 3911061),
    },
}

# Bbox regional Magallanes completa
REGION_MAGALLANES_WGS84 = dict(
    lon_min=-77.0, lon_max=-65.0,
    lat_min=-56.5, lat_max=-50.0,
)

# ─────────────────────────────────────────────────────────
# TRANSFORMER UTM→WGS84
# ─────────────────────────────────────────────────────────
T_utm2wgs = Transformer.from_crs("EPSG:32719", "EPSG:4326", always_xy=True)


def utm_bbox_to_wgs84(xmin, ymin, xmax, ymax, pad_deg=0.05):
    """Convierte bbox UTM 19S a WGS84 con padding opcional."""
    corners = [(xmin, ymin), (xmin, ymax), (xmax, ymin), (xmax, ymax)]
    lons, lats = [], []
    for x, y in corners:
        lo, la = T_utm2wgs.transform(x, y)
        lons.append(lo); lats.append(la)
    return (
        min(lons) - pad_deg, max(lons) + pad_deg,
        min(lats) - pad_deg, max(lats) + pad_deg,
    )


def get_tile_names(lon_min, lon_max, lat_min, lat_max):
    """Retorna lista de tiles Copernicus GLO-30 que cubren el bbox WGS84."""
    tiles = []
    for lat in range(math.floor(lat_min), math.ceil(lat_max)):
        for lon in range(math.floor(lon_min), math.ceil(lon_max)):
            ns = "S" if lat < 0 else "N"
            ew = "W" if lon < 0 else "E"
            # IMPORTANTE: para S, el número es el valor absoluto del piso
            lat_n = abs(lat) if lat < 0 else lat
            lon_n = abs(lon) if lon < 0 else lon
            name = (f"Copernicus_DSM_COG_10_{ns}{lat_n:02d}_00"
                    f"_{ew}{lon_n:03d}_00_DEM")
            tiles.append(name)
    return tiles


# ─────────────────────────────────────────────────────────
# DESCARGA DE TILES
# ─────────────────────────────────────────────────────────
BASE_URL = "https://copernicus-dem-30m.s3.amazonaws.com/{name}/{name}.tif"


def download_tile(tile_name, dest_dir, timeout=120, retries=3):
    """Descarga un tile GLO-30 si no existe ya."""
    out_path = os.path.join(dest_dir, f"{tile_name}.tif")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(f"    [cache] {tile_name}.tif")
        return out_path

    url = BASE_URL.format(name=tile_name)
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, stream=True, timeout=timeout)
            if r.status_code == 200:
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 256):
                        f.write(chunk)
                        downloaded += len(chunk)
                mb = os.path.getsize(out_path) / 1e6
                print(f"    ✓ {tile_name}.tif  ({mb:.1f} MB)")
                return out_path
            elif r.status_code == 404:
                print(f"    ⚠ 404 — tile no existe (agua/sin datos): {tile_name}")
                return None
            else:
                print(f"    ✗ HTTP {r.status_code} — intento {attempt}/{retries}")
        except requests.exceptions.Timeout:
            print(f"    ✗ Timeout — intento {attempt}/{retries}")
        except Exception as e:
            print(f"    ✗ Error: {e} — intento {attempt}/{retries}")
        time.sleep(2 ** attempt)

    return None


# ─────────────────────────────────────────────────────────
# MOSAICO + CLIP + REPROYECCIÓN
# ─────────────────────────────────────────────────────────

def build_mosaic(tile_paths, out_path, clip_shp=None, out_crs="EPSG:32719",
                 out_res=30):
    """
    Fusiona tiles, opcionalmente recorta al polígono y reproyecta.
    """
    valid = [p for p in tile_paths if p and os.path.exists(p)]
    if not valid:
        print("    ⚠ Sin tiles válidos para mosaico.")
        return None

    datasets = [rasterio.open(p) for p in valid]
    mosaic, out_transform = merge(datasets, method="first", nodata=-9999)
    out_meta = datasets[0].meta.copy()
    out_meta.update({
        "driver":    "GTiff",
        "dtype":     "float32",
        "height":    mosaic.shape[1],
        "width":     mosaic.shape[2],
        "transform": out_transform,
        "crs":       datasets[0].crs,
        "nodata":    -9999,
        "compress":  "lzw",
        "tiled":     True,
    })
    for ds in datasets:
        ds.close()

    tmp = out_path.replace(".tif", "_WGS84tmp.tif")
    with rasterio.open(tmp, "w", **out_meta) as dst:
        dst.write(mosaic.astype("float32"))

    # Clip al polígono de cuenca (opcional)
    if clip_shp and os.path.exists(clip_shp):
        gdf = gpd.read_file(clip_shp).to_crs(out_meta["crs"])
        with rasterio.open(tmp) as src:
            out_img, out_t = mask(src, gdf.geometry, crop=True, nodata=-9999)
            out_meta2 = src.meta.copy()
            out_meta2.update({
                "height": out_img.shape[1],
                "width":  out_img.shape[2],
                "transform": out_t
            })
        with rasterio.open(tmp, "w", **out_meta2) as dst2:
            dst2.write(out_img)

    # Reproyectar a UTM 19S
    dst_crs = CRS.from_string(out_crs)
    with rasterio.open(tmp) as src:
        transform_r, width_r, height_r = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds,
            resolution=out_res
        )
        meta_r = src.meta.copy()
        meta_r.update({
            "crs":       dst_crs,
            "transform": transform_r,
            "width":     width_r,
            "height":    height_r,
            "nodata":    -9999,
            "compress":  "lzw",
        })
        with rasterio.open(out_path, "w", **meta_r) as dst_r:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst_r, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform_r,
                    dst_crs=dst_crs,
                    resampling=Resampling.bilinear,
                )

    os.remove(tmp)

    # Stats
    with rasterio.open(out_path) as chk:
        data = chk.read(1)
        valid_data = data[data != -9999]
        print(f"    → Mosaico: {width_r}×{height_r} px | "
              f"Elev. [{valid_data.min():.0f}m – {valid_data.max():.0f}m] | "
              f"CRS: {chk.crs.to_epsg()}")

    return out_path


# ─────────────────────────────────────────────────────────
# DESCARGA REGIONAL MAGALLANES
# ─────────────────────────────────────────────────────────

def download_region_magallanes():
    """Descarga todos los tiles de la región de Magallanes."""
    cfg = REGION_MAGALLANES_WGS84
    tiles = get_tile_names(
        cfg["lon_min"], cfg["lon_max"],
        cfg["lat_min"], cfg["lat_max"]
    )
    print(f"\n  Region Magallanes: {len(tiles)} tiles a descargar")
    print(f"  bbox: lon [{cfg['lon_min']}, {cfg['lon_max']}] | "
          f"lat [{cfg['lat_min']}, {cfg['lat_max']}]")

    paths = []
    for tile in tiles:
        p = download_tile(tile, TILES_D)
        if p:
            paths.append(p)

    if paths:
        out = os.path.join(MOSAICS, "DEM_Cop30_Magallanes_UTM19S.tif")
        print(f"\n  Fusionando {len(paths)} tiles → mosaico regional...")
        build_mosaic(paths, out, clip_shp=None, out_crs="EPSG:32719", out_res=30)
        print(f"  ✓ Mosaico regional: {out}")
    return paths


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("DESCARGA DEM COPERNICUS GLO-30 (30m) — MAGALLANES")
    print("Fuente: s3://copernicus-dem-30m/ (acceso público HTTPS)")
    print("=" * 65)

    # ── Tiles por cuenca ──────────────────────────────────
    for nombre, cfg in CUENCAS.items():
        print(f"\n{'─'*55}")
        print(f"  Cuenca: {nombre}")
        xmin, ymin, xmax, ymax = cfg["bbox_utm"]
        lon_min, lon_max, lat_min, lat_max = utm_bbox_to_wgs84(
            xmin, ymin, xmax, ymax, pad_deg=0.1
        )
        print(f"  WGS84: lon [{lon_min:.3f}, {lon_max:.3f}] | "
              f"lat [{lat_min:.3f}, {lat_max:.3f}]")

        tiles = get_tile_names(lon_min, lon_max, lat_min, lat_max)
        print(f"  Tiles identificados ({len(tiles)}): {tiles}")

        paths = []
        for tile in tiles:
            p = download_tile(tile, TILES_D)
            if p:
                paths.append(p)

        if paths:
            out = os.path.join(MOSAICS, f"DEM_Cop30_{nombre}_UTM19S.tif")
            print(f"  Fusionando {len(paths)} tile(s)...")
            build_mosaic(paths, out,
                         clip_shp=cfg["shp"],
                         out_crs="EPSG:32719",
                         out_res=30)
            print(f"  ✓ DEM cuenca listo: DEM_Cop30_{nombre}_UTM19S.tif")

    # ── Mosaico regional (opcional — ~80–100 tiles, ~2–3 GB) ──
    resp = input("\n¿Descargar mosaico regional de Magallanes completo (~80 tiles)? [s/N]: ")
    if resp.strip().lower() in ("s", "si", "sí", "y", "yes"):
        download_region_magallanes()
    else:
        print("  Descarga regional omitida.")

    print(f"\n{'='*65}")
    print("✓ DESCARGA COMPLETA")
    print(f"\nArchivos GeoTIFF en: {MOSAICS}")
    for f in sorted(os.listdir(MOSAICS)):
        if f.endswith(".tif"):
            size_mb = os.path.getsize(os.path.join(MOSAICS, f)) / 1e6
            print(f"  • {f}  ({size_mb:.1f} MB)")
    print(f"\nTiles brutos en:     {TILES_D}")
    print("\nSIGUIENTE PASO: Ejecutar 07_mapa_3d_leapfrog.py con DEMs reales")
