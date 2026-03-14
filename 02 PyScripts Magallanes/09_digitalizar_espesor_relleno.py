"""
Script 09 (v2): Digitalización Figura 6-17 — Espesor Relleno Cuaternario
==========================================================================
Proyecto : Análisis de Recursos Hídricos - Cuencas Magallanes (IDIEM/DGA)
Propósito:
  Reproduce el raster "Espesor de la Unidad Hidrogeológica Cuaternaria
  (relleno sedimentario)" de la Figura 6-17.

  Modo imagen (prioritario): convierte color→espesor desde el PNG
  extraído del PDF. Calibración exacta del marco de la figura.

  Modo manual (fallback): ~200 puntos de control actualizados desde
  lectura cuidadosa de la figura con las cuencas de estudio superpuestas.

  Correcciones respecto a v1:
    - Cuenca Penitente: mayormente roca (0 m). Sólo franja E tiene
      relleno ~20–100 m (no 300–400 m como estaba antes).
    - Cuenca El Oro: mezcla valle 40–150 m + afloramientos rocosos.
    - Pampa profunda (300–397 m) sólo E=330k–380k, N=4210k–4248k
      (fuera de las cuencas de estudio).
    - Suavizado gaussiano reforzado para evitar gradientes abruptos.

  Salida:
    DEM_Copernicus_30m/espesor_relleno/EspesorRelleno_Regional.tif
    DEM_Copernicus_30m/espesor_relleno/EspesorRelleno_Penitente.tif
    DEM_Copernicus_30m/espesor_relleno/EspesorRelleno_El_Oro.tif
    input/VALIDACION_espesor_relleno.png

  Cuenca Róbalo (Y≈3 904 000) está fuera del extent → Script 07 usa gaussiano.

Autor : Especialista Senior en Modelación
Fecha : 11-03-2026
"""

import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
from rasterio.mask import mask as rio_mask
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from project_paths import BASE_DIR as BASE, PY_SCRIPTS_DIR as OUT, resolve_input

# ─────────────────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────────────────
IMG_PATH  = resolve_input("02 PyScripts Magallanes/input/Figura6_17_EspesorRelleno.png")
BASIN_SHP = resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/area_estudio_total.shp")
FILL_D    = os.path.join(OUT, "DEM_Copernicus_30m/espesor_relleno")
os.makedirs(FILL_D, exist_ok=True)
os.makedirs(os.path.join(OUT, "input"), exist_ok=True)

# ─────────────────────────────────────────────────────────
# CALIBRACIÓN PIXEL→UTM (extraída del análisis del PDF a 4x zoom)
# Marco del mapa visible en Figura 6-17:
#   col 318  → E = 300 000 m  |  col 2186 → E = 500 000 m
#   row 262  → N = 4 240 000 m|  row 1800 → N = 4 080 000 m
# ─────────────────────────────────────────────────────────
MAP_PIX_LEFT   =  318
MAP_PIX_TOP    =  262
MAP_PIX_RIGHT  = 2186
MAP_PIX_BOTTOM = 1800
MAP_X_LEFT     = 300_000
MAP_X_RIGHT    = 500_000
MAP_Y_TOP      = 4_240_000
MAP_Y_BOTTOM   = 4_080_000

# ─────────────────────────────────────────────────────────────────────────────
# PUNTOS DE CONTROL MANUALES ACTUALIZADOS (UTM 32719)
# Leídos de Fig 6-17 con cuencas de estudio superpuestas.
# Columnas: Easting, Northing, Espesor_m
#
# Reglas aplicadas:
#  - Gris (roca) → 0 m
#  - Blanco (agua/mar) → nodata (excluido de interpolación)
#  - Amarillo (H~60°) → ~1–40 m
#  - Naranja (H~30°)  → ~130–200 m
#  - Rojo    (H~0°)   → ~350–397 m
#  - Penitente interior: roca 0 m, franja E (E>335k): 25–100 m
#  - El Oro: valles 40–150 m, afloramientos rocosos 0 m
# ─────────────────────────────────────────────────────────────────────────────
CONTROL_POINTS = np.array([

    # ── PAMPA NORTE — zona más profunda (fuera de cuencas) ───────────────────
    # Franja N=4235k–4248k, E=330k–370k: rojo intenso 360–397 m
    [330000, 4248000, 290], [340000, 4248000, 355], [350000, 4248000, 385],
    [355000, 4248000, 397], [360000, 4248000, 390], [370000, 4248000, 360],
    [380000, 4248000, 290], [390000, 4248000, 215], [400000, 4248000, 145],

    [330000, 4238000, 310], [340000, 4238000, 370], [350000, 4238000, 395],
    [355000, 4238000, 397], [360000, 4238000, 388], [370000, 4238000, 355],
    [380000, 4238000, 275], [390000, 4238000, 195], [400000, 4238000, 130],
    [410000, 4238000,  75], [420000, 4238000,  40],

    [330000, 4228000, 280], [340000, 4228000, 345], [350000, 4228000, 370],
    [358000, 4228000, 380], [365000, 4228000, 355], [375000, 4228000, 300],
    [385000, 4228000, 235], [395000, 4228000, 160], [405000, 4228000, 100],
    [415000, 4228000,  55], [425000, 4228000,  25],

    [330000, 4218000, 240], [340000, 4218000, 300], [350000, 4218000, 330],
    [360000, 4218000, 315], [370000, 4218000, 270], [380000, 4218000, 205],
    [390000, 4218000, 145], [400000, 4218000,  90], [410000, 4218000,  50],
    [420000, 4218000,  22], [430000, 4218000,  10],

    [325000, 4208000, 185], [335000, 4208000, 235], [345000, 4208000, 260],
    [355000, 4208000, 245], [365000, 4208000, 210], [375000, 4208000, 160],
    [385000, 4208000, 110], [395000, 4208000,  70], [405000, 4208000,  38],
    [415000, 4208000,  15], [425000, 4208000,   5],

    [320000, 4198000, 120], [330000, 4198000, 165], [340000, 4198000, 195],
    [350000, 4198000, 185], [360000, 4198000, 160], [370000, 4198000, 125],
    [380000, 4198000,  86], [390000, 4198000,  52], [400000, 4198000,  28],
    [410000, 4198000,  12],

    [315000, 4188000,  62], [325000, 4188000, 100], [335000, 4188000, 130],
    [345000, 4188000, 135], [355000, 4188000, 115], [365000, 4188000,  85],
    [375000, 4188000,  55], [385000, 4188000,  30], [395000, 4188000,  14],

    [308000, 4178000,  28], [318000, 4178000,  55], [328000, 4178000,  75],
    [338000, 4178000,  82], [348000, 4178000,  72], [358000, 4178000,  52],
    [368000, 4178000,  32], [378000, 4178000,  16],

    [305000, 4168000,  14], [315000, 4168000,  30], [325000, 4168000,  48],
    [335000, 4168000,  58], [345000, 4168000,  52], [355000, 4168000,  36],
    [365000, 4168000,  20], [375000, 4168000,   8],

    # ── CUENCA PENITENTE (E=292k–346k, N=4182k–4248k) ───────────────────────
    # Interior mayormente roca (gris = 0 m). Sólo franja oriental tiene relleno.
    # Zona W-central: bedrock
    [293000, 4190000,  0], [297000, 4205000,  0], [300000, 4218000,  0],
    [303000, 4230000,  5], [300000, 4242000,  5], [295000, 4246000,  0],
    [305000, 4196000,  0], [308000, 4210000,  0], [312000, 4222000,  8],
    [312000, 4234000, 12], [309000, 4244000,  8],
    [318000, 4185000,  0], [320000, 4200000,  5], [320000, 4214000, 12],
    [322000, 4226000, 20], [320000, 4238000, 18],
    [327000, 4184000,  5], [328000, 4196000, 12], [328000, 4210000, 22],
    [328000, 4222000, 32], [327000, 4234000, 28],

    # Franja oriental Penitente: transición yellow → light orange (~25–95 m)
    [334000, 4184000, 22], [336000, 4194000, 38], [337000, 4204000, 55],
    [338000, 4214000, 70], [339000, 4224000, 82], [340000, 4234000, 90],
    [340000, 4244000, 88], [341000, 4246000, 80],
    [343000, 4188000, 28], [344000, 4200000, 48], [344000, 4212000, 65],
    [345000, 4222000, 78], [345000, 4234000, 85], [345000, 4244000, 82],

    # ── CUENCA EL ORO (E=421k–454k, N=4083k–4145k) ──────────────────────────
    # Valles con relleno moderado; afloramientos rocosos en SE (0 m)
    # Borde sur (muy poco relleno)
    [422000, 4083000,  5], [428000, 4087000, 18], [435000, 4085000, 12],
    [442000, 4085000,  8], [449000, 4084000,  5], [453000, 4087000,  8],
    # Franja central
    [423000, 4095000, 28], [429000, 4098000, 48], [435000, 4097000, 35],
    [441000, 4095000, 28], [447000, 4093000, 20], [452000, 4093000, 22],
    [423000, 4106000, 48], [429000, 4110000, 72], [435000, 4108000, 58],
    [440000, 4107000, 42], [446000, 4104000, 35], [451000, 4104000, 38],
    [424000, 4116000, 68], [430000, 4120000, 95], [436000, 4118000, 78],
    [441000, 4116000, 60], [447000, 4113000, 50], [451000, 4113000, 55],
    # Franja norte (más gruesa)
    [424000, 4126000, 88], [430000, 4130000,115], [435000, 4129000, 92],
    [440000, 4127000, 72], [446000, 4124000, 62], [451000, 4122000, 68],
    [424000, 4133000,105], [430000, 4136000,128], [435000, 4135000,105],
    [440000, 4133000, 82], [446000, 4130000, 72], [451000, 4129000, 78],
    [425000, 4140000,100], [430000, 4142000,120], [435000, 4141000, 98],
    [440000, 4139000, 76], [445000, 4137000, 65], [450000, 4136000, 70],
    [452000, 4141000, 62],
    # Afloramiento rocoso SE de El Oro (gris en la figura)
    [445000, 4120000, 25], [449000, 4128000, 38], [452000, 4135000, 52],

    # ── FRANJA TDF CENTRAL (entre cuencas) ──────────────────────────────────
    # E=400k–500k, N=4080k–4210k — zona naranja variable
    [402000, 4088000,  8], [412000, 4088000, 14], [422000, 4088000, 18],
    [432000, 4088000, 22], [442000, 4088000, 15], [452000, 4088000, 10],
    [462000, 4088000,  6], [472000, 4088000,   4], [482000, 4088000,  2],
    [492000, 4088000,  1],

    [402000, 4100000, 14], [412000, 4100000, 24], [422000, 4100000, 34],
    [432000, 4100000, 38], [442000, 4100000, 28], [452000, 4100000, 20],
    [462000, 4100000, 14], [472000, 4100000, 10], [482000, 4100000,  6],
    [492000, 4100000,  3],

    [402000, 4115000, 22], [412000, 4115000, 38], [422000, 4115000, 55],
    [432000, 4115000, 60], [442000, 4115000, 50], [452000, 4115000, 40],
    [462000, 4115000, 28], [472000, 4115000, 20], [482000, 4115000, 12],
    [492000, 4115000,  6],

    [402000, 4130000, 32], [412000, 4130000, 52], [422000, 4130000, 72],
    [432000, 4130000, 82], [442000, 4130000, 72], [452000, 4130000, 60],
    [462000, 4130000, 46], [472000, 4130000, 32], [482000, 4130000, 20],
    [492000, 4130000, 10],

    [402000, 4145000, 42], [412000, 4145000, 65], [422000, 4145000, 90],
    [432000, 4145000,105], [442000, 4145000, 95], [452000, 4145000, 82],
    [462000, 4145000, 68], [472000, 4145000, 52], [482000, 4145000, 35],
    [492000, 4145000, 20],

    [402000, 4158000, 55], [412000, 4158000, 80], [422000, 4158000,108],
    [432000, 4158000,125], [442000, 4158000,120], [452000, 4158000,108],
    [462000, 4158000, 92], [472000, 4158000, 75], [482000, 4158000, 55],
    [492000, 4158000, 35],

    [402000, 4170000, 65], [412000, 4170000, 88], [422000, 4170000,112],
    [432000, 4170000,130], [442000, 4170000,128], [452000, 4170000,118],
    [462000, 4170000,104], [472000, 4170000, 88], [482000, 4170000, 68],
    [492000, 4170000, 45],

    [402000, 4182000, 62], [412000, 4182000, 84], [422000, 4182000,106],
    [432000, 4182000,122], [442000, 4182000,120], [452000, 4182000,110],
    [462000, 4182000, 96], [472000, 4182000, 80], [482000, 4182000, 62],
    [492000, 4182000, 42],

    [402000, 4194000, 52], [412000, 4194000, 72], [422000, 4194000, 92],
    [432000, 4194000,108], [442000, 4194000,108], [452000, 4194000, 98],
    [462000, 4194000, 85], [472000, 4194000, 68], [482000, 4194000, 50],
    [492000, 4194000, 32],

    [402000, 4206000, 38], [412000, 4206000, 55], [422000, 4206000, 74],
    [432000, 4206000, 88], [442000, 4206000, 88], [452000, 4206000, 80],
    [462000, 4206000, 68], [472000, 4206000, 52], [482000, 4206000, 36],
    [492000, 4206000, 20],

    # ── BORDES Y ZONAS DE ROCA (S=0 m) ──────────────────────────────────────
    # Borde W (cordillera patagónica, roca)
    [280000, 4080000, 0], [280000, 4100000, 0], [280000, 4120000, 0],
    [280000, 4140000, 0], [280000, 4160000, 0], [280000, 4180000, 0],
    [280000, 4200000, 0], [280000, 4220000, 0], [280000, 4240000, 0],
    # Borde E (roca TDF oriental)
    [502000, 4080000, 0], [502000, 4100000, 0], [502000, 4120000, 0],
    [502000, 4140000, 0], [502000, 4160000, 0], [502000, 4180000, 0],
    [502000, 4200000, 0], [502000, 4220000, 0],

], dtype=np.float32)


def build_regional_raster(control_pts, regional_tif, resolution=250):
    """
    Interpola puntos de control a raster UTM 32719.
    Aplicamos suavizado gaussiano en DOS pasadas:
      1. sigma=4 en la grilla cruda (elimina discontinuidades locales)
      2. sigma=3 tras el clip (elimina artefactos de borde)
    Esto evita transiciones abruptas tipo "0 m → 80 m en una celda".
    Resolución recomendada: 250 m (σ4 ≈ 1 km de radio de influencia).
    """
    x_min, x_max = 278_000, 525_000
    y_min, y_max = 4_063_000, 4_255_000

    xi = np.arange(x_min, x_max + resolution, resolution)
    yi = np.arange(y_min, y_max + resolution, resolution)
    XX, YY = np.meshgrid(xi, yi)

    xs, ys, vs = control_pts[:, 0], control_pts[:, 1], control_pts[:, 2]

    # Interpolación: cúbica rellena zonas bien cubiertas; nearest cubre bordes
    grid_c = griddata((xs, ys), vs, (XX, YY), method="cubic")
    grid_n = griddata((xs, ys), vs, (XX, YY), method="nearest")
    grid   = np.where(np.isnan(grid_c), grid_n, grid_c)
    grid   = np.clip(grid, 0, 397).astype("float32")

    # Pasada 1: suavizado principal — elimina escalones agresivos
    grid = gaussian_filter(grid, sigma=4)
    grid = np.clip(grid, 0, 397).astype("float32")

    # Pasada 2: suavizado fino — alisa bordes del clip
    grid = gaussian_filter(grid, sigma=2)
    grid = np.clip(grid, 0, 397).astype("float32")

    nodata_val = -9999.0
    data_out   = np.where(grid < 1.0, nodata_val, grid).astype("float32")
    # rasterio from_origin: row 0 = norte → flip (yi va de sur a norte)
    data_write = np.flipud(data_out)

    rows, cols = grid.shape
    transform = from_origin(x_min, y_max + resolution, resolution, resolution)
    meta = {
        "driver": "GTiff", "dtype": "float32",
        "height": rows, "width": cols, "count": 1,
        "crs": CRS.from_epsg(32719),
        "transform": transform, "nodata": nodata_val, "compress": "lzw",
    }
    with rasterio.open(regional_tif, "w", **meta) as dst:
        dst.write(data_write, 1)

    valid = data_out[data_out != nodata_val]
    print(f"  Raster: {cols}×{rows} px @ {resolution} m")
    print(f"  Espesor: {np.min(valid):.0f}–{np.max(valid):.0f} m  "
          f"(media {np.mean(valid):.0f} m)")
    return regional_tif, (XX, YY, grid)


def build_fill_from_image(img_path, regional_tif, resolution=250):
    """
    Conversión automática color→espesor desde imagen PNG.

    Calibración de píxeles (extraída del PDF a 4×zoom = 2449×3169 px):
      col 318  → E=300 000 m  |  col 2186 → E=500 000 m
      row 262  → N=4 240 000 m|  row 1800 → N=4 080 000 m

    Escala de colores de la leyenda (HSV):
      Amarillo H≈60°, S≈1, V≈1 → 1 m
      Rojo     H≈0°,  S≈1, V≈1 → 397 m
      Conversión: depth = 1 + 396 × (60 − H°) / 60   para H ∈ [0°,65°]

    Gris (roca, S<0.20 o no-amarillo/naranja/rojo) → nodata
    Blanco (agua, V>0.97 y S<0.08) → nodata

    Suavizado bicapa (σ=5 + σ=3) para transiciones geológicamente suaves.
    """
    from PIL import Image
    import matplotlib.colors as mcolors

    img  = Image.open(img_path).convert("RGB")
    arr  = np.array(img, dtype=np.float32)
    h_px, w_px = arr.shape[:2]
    print(f"  Imagen: {w_px}×{h_px} px")

    # ── Recortar al marco del mapa ────────────────────────────────────────
    L, T = MAP_PIX_LEFT, MAP_PIX_TOP
    R, B = MAP_PIX_RIGHT, MAP_PIX_BOTTOM
    crop = arr[T:B, L:R, :] / 255.0          # shape (rows_map, cols_map, 3)
    map_h, map_w = crop.shape[:2]
    print(f"  Marco mapa: {map_w}×{map_h} px  "
          f"({MAP_X_LEFT}–{MAP_X_RIGHT} E, {MAP_Y_BOTTOM}–{MAP_Y_TOP} N)")

    # ── Convertir a HSV ────────────────────────────────────────────────────
    hsv = mcolors.rgb_to_hsv(crop)           # H∈[0,1], S∈[0,1], V∈[0,1]
    H_deg = hsv[..., 0] * 360.0
    S     = hsv[..., 1]
    V     = hsv[..., 2]

    # ── Máscara de píxeles sedimento (yellow→orange→red) ──────────────────
    # Excluye gris (roca), blanco (agua/papel), azules/verdes (fondo externo)
    is_sediment = (
        (S > 0.35) &          # suficientemente saturado
        (V > 0.50) &          # no demasiado oscuro
        (H_deg <= 65.0) &     # sólo hues cálidos (yellow–red)
        ~((V > 0.97) & (S < 0.08))   # excluir blanco puro
    )

    # ── Conversión lineal Hue→Espesor ─────────────────────────────────────
    # H=60° → 1m; H=0° → 397m  (amarillo=poco, rojo=mucho)
    depth_raw = np.where(
        is_sediment,
        np.clip(1.0 + 396.0 * (60.0 - np.clip(H_deg, 0.0, 60.0)) / 60.0, 1.0, 397.0),
        np.nan
    ).astype("float32")

    # ── Coordenadas UTM para cada píxel del recorte ───────────────────────
    px_x = np.linspace(MAP_X_LEFT,  MAP_X_RIGHT,  map_w)
    px_y = np.linspace(MAP_Y_TOP,   MAP_Y_BOTTOM, map_h)   # row0=norte
    PX, PY = np.meshgrid(px_x, px_y)

    # ── Submuestreo para griddata (máx 150 000 puntos) ────────────────────
    mask_v = ~np.isnan(depth_raw)
    xs = PX[mask_v]; ys = PY[mask_v]; vs = depth_raw[mask_v]
    n_pts = len(xs)
    step  = max(1, n_pts // 150_000)
    xs, ys, vs = xs[::step], ys[::step], vs[::step]
    print(f"  Puntos sedimento: {n_pts:,} → muestreados {len(xs):,}")

    # ── Grilla raster de salida ───────────────────────────────────────────
    x_min, x_max = MAP_X_LEFT,  MAP_X_RIGHT
    y_min, y_max = MAP_Y_BOTTOM, MAP_Y_TOP
    xi = np.arange(x_min, x_max + resolution, resolution)
    yi = np.arange(y_min, y_max + resolution, resolution)
    XX, YY = np.meshgrid(xi, yi)

    grid = griddata((xs, ys), vs, (XX, YY), method="nearest").astype("float32")

    # ── Máscara de sedimento extendida (para distinguir roca real de NaN) ─
    # Si la mayoría de píxeles fuente en ese pixel de grilla son no-sedimento → 0
    mask_grid = griddata(
        (PX.ravel(), PY.ravel()),
        mask_v.ravel().astype("float32"),
        (XX, YY), method="nearest"
    )
    # En zonas grises (roca) poner 0, no nodata — así el suavizado puede crear
    # transiciones suaves en lugar de bordes abruptos.
    grid = np.where(mask_grid < 0.25, 0.0, grid)
    grid = np.clip(grid, 0.0, 397.0).astype("float32")

    # ── Suavizado bicapa ──────────────────────────────────────────────────
    # Pasada 1 (σ=5): elimina pixelado de la fuente y escalones
    grid = gaussian_filter(grid, sigma=5)
    grid = np.clip(grid, 0.0, 397.0)
    # Pasada 2 (σ=3): suavizado fino
    grid = gaussian_filter(grid, sigma=3)
    grid = np.clip(grid, 0.0, 397.0).astype("float32")

    # ── Escribir GeoTIFF ──────────────────────────────────────────────────
    data_out = np.where(grid < 1.0, -9999.0, grid).astype("float32")
    rows_out, cols_out = grid.shape
    transform = from_origin(x_min, y_max + resolution, resolution, resolution)
    meta = {
        "driver": "GTiff", "dtype": "float32",
        "height": rows_out, "width": cols_out, "count": 1,
        "crs": CRS.from_epsg(32719), "transform": transform,
        "nodata": -9999.0, "compress": "lzw",
    }
    with rasterio.open(regional_tif, "w", **meta) as dst:
        dst.write(data_out, 1)

    valid = data_out[data_out != -9999.0]
    print(f"  Raster (imagen): {cols_out}×{rows_out} px @ {resolution} m  "
          f"— espesor {np.min(valid):.0f}–{np.max(valid):.0f} m "
          f"(media {np.mean(valid):.0f} m)")
    return regional_tif, (XX, YY, grid)


def save_inspect_png(XX, YY, grid, control_pts=None):
    """PNG de validación: raster espesor + cuencas + puntos de control."""
    import matplotlib.pyplot as plt

    gdf = gpd.read_file(BASIN_SHP)
    fig, ax = plt.subplots(figsize=(13, 10), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")

    grid_plot = np.where(grid < 1, np.nan, grid)
    im = ax.pcolormesh(XX, YY, grid_plot, cmap="hot_r",
                       vmin=1, vmax=397, shading="auto", alpha=0.9)
    cb = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cb.set_label("Espesor relleno (m)", color="#c8d8e8")
    plt.setp(cb.ax.yaxis.get_ticklabels(), color="#c8d8e8")

    colors_b = {"RIO PENITENTE": "#00e5ff", "RIO DEL ORO": "#39ff14",
                "RIO ROBALO": "#ff69b4"}
    handles = []
    for _, row in gdf.iterrows():
        c = colors_b.get(row["NOMBRE"], "white")
        x, y = row.geometry.exterior.xy
        line, = ax.plot(x, y, color=c, lw=2.0, label=row["NOMBRE"])
        handles.append(line)

    if control_pts is not None:
        ax.scatter(control_pts[:, 0], control_pts[:, 1],
                   c=control_pts[:, 2], cmap="hot_r", vmin=1, vmax=397,
                   s=45, edgecolors="white", linewidths=0.5, zorder=5,
                   label="Puntos control")
        ttl = ("VALIDACIÓN — Digitalización Manual (puntos de control)\n"
               "Las cuencas deben solapar la zona coloreada")
    else:
        ttl = ("VALIDACIÓN — Conversión desde Imagen PNG\n"
               "Las cuencas deben solapar la zona coloreada")

    ax.set_title(ttl, color="#c8d8e8", fontsize=10)
    ax.legend(fontsize=8, facecolor="#111820", labelcolor="#c8d8e8",
              edgecolor="#2a3a4a")
    for sp in ax.spines.values():
        sp.set_edgecolor("#2a3a4a")
    ax.tick_params(colors="#c8d8e8")
    ax.set_xlabel("UTM Easting (m)", color="#c8d8e8")
    ax.set_ylabel("UTM Northing (m)", color="#c8d8e8")

    out_p = os.path.join(OUT, "input", "VALIDACION_espesor_relleno.png")
    plt.tight_layout()
    plt.savefig(out_p, dpi=130, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  ✓ Validación: {out_p}")


def clip_to_basin(regional_tif, poly, out_path, nombre):
    with rasterio.open(regional_tif) as src:
        out_img, out_t = rio_mask(src, [poly], crop=True, nodata=-9999)
        meta = src.meta.copy()
        meta.update({"height": out_img.shape[1], "width": out_img.shape[2],
                     "transform": out_t, "compress": "lzw"})
    data  = out_img[0]
    valid = data[data != -9999]
    if len(valid) < 5:
        print(f"    ⚠ {nombre}: sin datos (cuenca fuera del extent)")
        return None
    print(f"    {nombre}: {np.min(valid):.0f}–{np.max(valid):.0f} m  "
          f"(media {np.mean(valid):.0f} m  p95 {np.percentile(valid, 95):.0f} m)")
    with rasterio.open(out_path, "w", **meta) as dst:
        dst.write(out_img)
    return out_path


# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("DIGITALIZACIÓN FIGURA 6-17 — ESPESOR RELLENO CUATERNARIO")
    print("=" * 65)

    regional = os.path.join(FILL_D, "EspesorRelleno_Regional.tif")

    if os.path.exists(IMG_PATH):
        print(f"\n[MODO imagen] {os.path.basename(IMG_PATH)}")
        regional, (XX, YY, grid) = build_fill_from_image(IMG_PATH, regional)
        ctrl_plot = None
    else:
        print(f"\n[MODO manual] {len(CONTROL_POINTS)} puntos de control digitalizados")
        print(f"  (Opcional: guarda figura en input/Figura6_17_EspesorRelleno.png)")
        regional, (XX, YY, grid) = build_regional_raster(CONTROL_POINTS, regional)
        ctrl_plot = CONTROL_POINTS

    print(f"  ✓ {os.path.basename(regional)}")

    print("\n[2] Recortando por cuenca...")
    gdf = gpd.read_file(BASIN_SHP)
    for nombre, fname in [
        ("RIO PENITENTE", "EspesorRelleno_Penitente.tif"),
        ("RIO DEL ORO",   "EspesorRelleno_El_Oro.tif"),
    ]:
        poly = gdf.loc[gdf["NOMBRE"] == nombre, "geometry"].iloc[0]
        out  = os.path.join(FILL_D, fname)
        r = clip_to_basin(regional, poly, out, nombre)
        print(f"    ✓ {fname}" if r else f"    ✗ {fname} (sin datos — se usará gaussiano)")

    print("\n  Nota: Cuenca Róbalo (Y≈3 904 000) fuera de Fig 6-17 → gaussiano")

    print("\n[3] Guardando validación...")
    save_inspect_png(XX, YY, grid, ctrl_plot)

    print(f"\n{'='*65}")
    print("✓ Archivos generados:")
    for f in sorted(os.listdir(FILL_D)):
        sz = os.path.getsize(os.path.join(FILL_D, f)) / 1024
        print(f"  {f}  ({sz:.0f} KB)")
    print("\n→ Ejecuta python3 07_mapa_3d_leapfrog.py para actualizar 3D")

