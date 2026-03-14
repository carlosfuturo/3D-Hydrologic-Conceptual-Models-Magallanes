"""
Script 07: Mapa 3D estilo Leapfrog — DEM Copernicus 30m + Espesor Relleno Cuaternario
Proyecto: Análisis de Recursos Hídricos - Cuencas Magallanes (IDIEM/DGA)

Propósito:
  - Visualización 3D interactiva estilo Leapfrog (fondo oscuro, superficies
    semitransparentes, paleta geológica) para las 3 cuencas de estudio.
  - Terreno desde DEM Copernicus GLO-30 (30m) REAL descargado por Script 08.
    Fallback: terreno sintético si los GeoTIFF no están disponibles.
  - Capa de espesor del relleno cuaternario (acuífero libre) digitalizada
    desde Figura 75 del Informe: "Espesor del relleno cuaternario en los
    modelos PEGH Vertientes del Atlántico y Tierra del Fuego".
  - Exporta archivo HTML interactivo (Plotly) y PNG estático por cuenca.

Autor: Especialista Senior en Modelación
Fecha: 11-03-2026
"""

import os, json
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask as rio_mask
from scipy.ndimage import gaussian_filter, zoom, map_coordinates, distance_transform_edt
from scipy.interpolate import griddata
from scipy.spatial import cKDTree
from shapely.geometry import Point
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from project_paths import BASE_DIR as BASE, PY_SCRIPTS_DIR as OUT, resolve_input

# ─────────────────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────────────────
DEM_D      = os.path.join(BASE, "01 Etapa 1/Anexos/Anexo E - SIG/05_Raster")
SIG_D      = os.path.join(BASE, "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/Carta_base")
COP_D      = os.path.join(OUT,  "DEM_Copernicus_30m/mosaicos")   # DEMs reales
FILL_DIG_D = os.path.join(OUT,  "DEM_Copernicus_30m/espesor_relleno")  # Script 09 output
BASIN_SHP  = resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/area_estudio_total.shp")
HYDRO_SHP_D = os.path.join(BASE, "01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC")
BOT_SIG_D  = os.path.join(BASE, "03 SIG Magallanes")  # propsBOT_*_Proj.shp (Bottom1 en m.s.n.m.)
LAGUNAS_SHP = resolve_input("03 SIG Magallanes/Lagunas.shp")
WELLS_CSV  = resolve_input("02 PyScripts Magallanes/pozos_acuifero.csv")  # Script 10 output
OF_HIDRICA_XLSX = resolve_input("02 PyScripts Magallanes/data_set_oferta_hidrica.xlsx")  # Oferta hídrica
FIG_D  = os.path.join(OUT,  "Figuras_3D_Leapfrog")
os.makedirs(FIG_D, exist_ok=True)

# ─────────────────────────────────────────────────────────
# PARÁMETROS POR CUENCA
# ─────────────────────────────────────────────────────────
# Espesor relleno cuaternario digitalizado de Figura 75 PEGH
# (zmin_fill → margen cuenca | zmax_fill → centro valle)
CUENCAS_CFG = {
    "Penitente": {
        "dem_shp":       "EZ_DEM_penitente.shp",
        "dem_cop":       "DEM_Cop30_Penitente_UTM19S.tif",  # Copernicus real
        "basin_nombre":  "RIO PENITENTE",
        "fill_tif":      "EspesorRelleno_Penitente.tif",    # Script 09
        "elev_min":      118.0,
        "elev_max":     1103.0,
        "elev_mean":     407.0,
        "fill_center":   180.0,
        "fill_edge":      15.0,
        "fill_sigma":     0.38,
        "color_terrain":  "deep",
        "title": "Cuenca Río Penitente",
        "label": "Penitente",
        "grid_n":         80,
        "river_shp":      "red_hidro_penitente.shp",
        "bot_shp":        "propsBOT_Vertientes_Proj.shp",  # Bottom1 m.s.n.m.
        "bot_buffer":     2400,  # m — captures model cells near basin boundary
        "well_cuenca":    "Penitente",
        "gauge_row":      0,         # row index in Oferta_Superficial sheet
        "gw_col":         "Cuenca Penitente (m3_s)",
    },
    "El_Oro": {
        "dem_shp":       "EZ_DEM_oro.shp",
        "dem_cop":       "DEM_Cop30_El_Oro_UTM19S.tif",
        "basin_nombre":  "RIO DEL ORO",
        "fill_tif":      "EspesorRelleno_El_Oro.tif",       # Script 09
        "elev_min":        0.0,
        "elev_max":      578.0,
        "elev_mean":     248.0,
        "fill_center":    65.0,
        "fill_edge":       8.0,
        "fill_sigma":     0.30,
        "color_terrain":  "deep",
        "title": "Cuenca Río El Oro",
        "label": "El Oro",
        "grid_n":         70,
        "river_shp":      "red_hidro_oro.shp",
        "bot_shp":        "propsBOT_Fuego_Proj.shp",      # Bottom1 m.s.n.m.
        "bot_buffer":     1200,  # m — captures model cells near basin boundary
        "well_cuenca":    "Oro",
        "gauge_row":      1,         # row index in Oferta_Superficial sheet
        "gw_col":         "Cuenca Oro (m3_s)",
    },
    "Robalo": {
        "dem_shp":       "EZ_DEM_robalo.shp",
        "dem_cop":       "DEM_Cop30_Robalo_UTM19S.tif",
        "basin_nombre":  "RIO ROBALO",
        "fill_tif":      None,  # basin outside Fig 6-17 extent → gaussian
        "elev_min":        0.0,
        "elev_max":     1000.0,
        "elev_mean":     485.0,
        "fill_center":    12.0,
        "fill_edge":       0.5,
        "fill_sigma":     0.25,
        "color_terrain":  "deep",
        "title": "Cuenca Río Róbalo",
        "label": "Róbalo",
        "grid_n":         55,
        "river_shp":      "red_hidro_robalo.shp",
        "well_cuenca":    "Robalo",
        "gauge_row":      2,         # row index in Oferta_Superficial sheet
    },
}

# ─────────────────────────────────────────────────────────
# LEAPFROG THEME
# ─────────────────────────────────────────────────────────
LF_BG    = "#1a3a5c"   # fondo principal — azul marino medio
LF_PAPER = "#0f2540"   # fondo paper — azul marino oscuro
LF_AXIS  = "#3a6a9a"   # líneas ejes — azul medio
LF_FONT  = "#e8f0f8"   # texto — blanco azulado

def leapfrog_scene(title, z_range):
    """Retorna el dict de escena 3D con estilo Leapfrog."""
    return dict(
        bgcolor=LF_BG,
        xaxis=dict(title="E (m)", gridcolor=LF_AXIS, zerolinecolor=LF_AXIS,
                   backgroundcolor=LF_BG, color=LF_FONT, showspikes=False),
        yaxis=dict(title="N (m)", gridcolor=LF_AXIS, zerolinecolor=LF_AXIS,
                   backgroundcolor=LF_BG, color=LF_FONT, showspikes=False),
        zaxis=dict(title="Z (m.s.n.m.)", range=z_range,
                   gridcolor=LF_AXIS, zerolinecolor=LF_AXIS,
                   backgroundcolor=LF_BG, color=LF_FONT, showspikes=False),
        camera=dict(eye=dict(x=1.5, y=-1.8, z=0.9)),
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=0.35),
        annotations=[dict(text=title, x=0.5, y=1.05, xref="paper",
                          yref="paper", showarrow=False,
                          font=dict(color=LF_FONT, size=12))]
    )

# ─────────────────────────────────────────────────────────
# GENERACIÓN DE TERRAIN + FILL GRID
# ─────────────────────────────────────────────────────────

def build_terrain_and_fill(cfg):
    """
    Construye dos grids numpy desde el DEM Copernicus GLO-30 real (30m).
    Fallback a terreno sintético si el GeoTIFF no está disponible.
      terrain_z : elevación del terreno (m)
      fill_z    : base del relleno = terrain_z - fill_thickness
      fill_t    : espesor del relleno (m)
    """
    gdf_basin = gpd.read_file(BASIN_SHP)
    poly = gdf_basin.loc[gdf_basin["NOMBRE"] == cfg["basin_nombre"], "geometry"].iloc[0]
    xmin, ymin, xmax, ymax = poly.bounds

    # ── Intentar leer DEM Copernicus real ──────────────────
    cop_path = resolve_input(os.path.join("02 PyScripts Magallanes", "DEM_Copernicus_30m", "mosaicos", cfg["dem_cop"]))
    if os.path.exists(cop_path):
        with rasterio.open(cop_path) as src:
            out_img, out_transform = rio_mask(src, [poly], crop=True, nodata=-9999)
            elev_raw = out_img[0].astype("float32")
            elev_raw[elev_raw == -9999] = np.nan
            elev_raw = np.flipud(elev_raw)  # rasterio row-0=north → flip for linspace(ymin,ymax)
        rows, cols = elev_raw.shape
        N = cfg["grid_n"]
        # Downsample a grid_n×grid_n para rendimiento en Plotly
        zoom_r = N / max(rows, cols)
        elev_m = zoom(elev_raw, zoom_r, order=1, prefilter=False)
        # Propagar NaN tras zoom
        nan_mask_zoom = zoom(
            np.where(np.isnan(elev_raw), 0.0, 1.0).astype("float32"),
            zoom_r, order=0
        )
        elev_m[nan_mask_zoom < 0.5] = np.nan
        xi = np.linspace(xmin, xmax, elev_m.shape[1])
        yi = np.linspace(ymin, ymax, elev_m.shape[0])
        XX, YY = np.meshgrid(xi, yi)
        # Actualizar stats desde datos reales
        valid = elev_m[~np.isnan(elev_m)]
        cfg["elev_min"]  = float(np.nanmin(valid))
        cfg["elev_max"]  = float(np.nanmax(valid))
        cfg["elev_mean"] = float(np.nanmean(valid))
        print(f"    [DEM real] {cfg['label']}: {elev_m.shape} px | "
              f"{cfg['elev_min']:.0f}–{cfg['elev_max']:.0f} m")
    else:
        # ── Fallback: terreno sintético ─────────────────────
        print(f"    [DEM sintético] {cfg['label']} (GeoTIFF no encontrado)")
        N = cfg["grid_n"]
        xi = np.linspace(xmin, xmax, N)
        yi = np.linspace(ymin, ymax, N)
        XX, YY = np.meshgrid(xi, yi)
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        rx = (xmax - xmin) / 2
        ry = (ymax - ymin) / 2
        dist_norm = np.sqrt(((XX - cx) / rx)**2 + ((YY - cy) / ry)**2)
        dist_norm = np.clip(dist_norm, 0, 1)
        e_min  = cfg["elev_min"]
        e_max  = cfg["elev_max"]
        e_mean = cfg["elev_mean"]
        rng = np.random.default_rng(42)
        noise = gaussian_filter(
            rng.standard_normal((N, N)) * (e_max - e_min) * 0.08, sigma=3
        )
        elev = e_mean + (e_max - e_mean) * dist_norm**1.6 + noise
        pts = [Point(x, y) for x, y in zip(XX.ravel(), YY.ravel())]
        mask_basin = np.array([poly.contains(p) for p in pts]).reshape(N, N)
        elev_m = np.where(mask_basin, np.clip(elev, e_min, e_max), np.nan)

    # ── Espesor relleno cuaternario ─────────────────────────
    # Prioridad: raster digitalizado de Fig 6-17 (Script 09) → gaussian fallback
    fill_path = resolve_input(os.path.join("02 PyScripts Magallanes", "DEM_Copernicus_30m", "espesor_relleno", cfg["fill_tif"])) if cfg.get("fill_tif") else ""
    if fill_path and os.path.exists(fill_path):
        with rasterio.open(fill_path) as src:
            fi, _ = rio_mask(src, [poly], crop=True, nodata=-9999)
            fill_raw = fi[0].astype("float32")
            fill_raw[fill_raw == -9999] = np.nan
            fill_raw = np.flipud(fill_raw)
        fr, fc = fill_raw.shape
        # Weighted bilinear zoom: resample both fill values and a validity weight
        # map on the same DEM grid.  Cells with no TIF data nearby remain 0 — this
        # prevents spreading fill values onto mountainsides that have no sediment.
        dst_r, dst_c = elev_m.shape
        _fn = np.where(np.isnan(fill_raw), 0.0, fill_raw).astype("float32")
        _fw = (~np.isnan(fill_raw)).astype("float32")
        fill_zoom_n = zoom(_fn, (dst_r / fr, dst_c / fc), order=1, prefilter=False)
        fill_zoom_w = zoom(_fw, (dst_r / fr, dst_c / fc), order=1, prefilter=False)
        with np.errstate(invalid="ignore", divide="ignore"):
            # Only assign fill where ≥20 % of the resample kernel came from valid pixels.
            # Lower values (0.05) spread the gaussian-blurred halo from script 09 well
            # outside the genuine sediment zone, putting fill on hillsides / wrong side.
            fill_t = np.where(fill_zoom_w > 0.20,
                              fill_zoom_n / fill_zoom_w, 0.0).astype("float32")
        fill_t = np.clip(fill_t, 0.0, None)
        valid_f = fill_t[~np.isnan(elev_m)]
        cfg["fill_center"] = float(np.nanpercentile(valid_f, 95))
        print(f"    [Fill real] {cfg['label']}: "
              f"{np.nanmin(valid_f):.0f}–{np.nanmax(valid_f):.0f} m "
              f"(p95={cfg['fill_center']:.0f} m)")
    else:
        # ── Gaussian fallback ─────────────────────────────────
        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2
        rx = (xmax - xmin) / 2
        ry = (ymax - ymin) / 2
        dist_norm = np.sqrt(((XX - cx) / rx)**2 + ((YY - cy) / ry)**2)
        dist_norm = np.clip(dist_norm, 0, 1)
        fill_raw = cfg["fill_edge"] + (cfg["fill_center"] - cfg["fill_edge"]) * np.exp(
            -dist_norm**2 / (2 * cfg["fill_sigma"]**2)
        )
        valley_mask = (elev_m < cfg["elev_mean"] * 1.05) & ~np.isnan(elev_m)
        fill_t = np.where(valley_mask, fill_raw, cfg["fill_edge"] * 0.3)
        fill_t = gaussian_filter(fill_t.astype("float32"), sigma=1.5)
        print(f"    [Fill gaussiano] {cfg['label']}")
    fill_t = np.where(~np.isnan(elev_m), fill_t, np.nan)

    # ── Override with real bottom elevations from BOT shapefile (Bottom1 m.s.n.m.) ──
    bot_shp_path = resolve_input(os.path.join("03 SIG Magallanes", cfg["bot_shp"])) if cfg.get("bot_shp") else ""
    if bot_shp_path and os.path.exists(bot_shp_path):
        gdf_bot = gpd.read_file(bot_shp_path)
        buf_m   = cfg.get("bot_buffer", 0)
        clip_poly = poly.buffer(buf_m) if buf_m > 0 else poly
        gdf_clip = gdf_bot[gdf_bot.geometry.intersects(clip_poly)].copy()
        if len(gdf_clip) > 0:
            pts_x = np.array([g.x for g in gdf_clip.geometry])
            pts_y = np.array([g.y for g in gdf_clip.geometry])
            pts_z = gdf_clip["Bottom1"].values.astype("float64")
            pts_xy = np.column_stack([pts_x, pts_y])
            grid_xy = np.column_stack([XX.ravel(), YY.ravel()])
            # Linear interpolation only — NaN outside convex hull of data points.
            # No nearest-neighbour fallback: areas with no BOT data (rock) stay NaN.
            fill_base_raw = griddata(pts_xy, pts_z, grid_xy, method="linear").reshape(XX.shape)

            # Mask cells farther than 1.5x the model grid spacing from any real point.
            # This removes the large empty triangles that griddata creates when point
            # density drops (sparse areas have no aquifer — just rock).
            _spacing = float(np.median(np.diff(np.sort(np.unique(pts_x)))))
            _max_dist = _spacing * 1.5
            _tree     = cKDTree(pts_xy)
            _dist, _  = _tree.query(grid_xy, k=1, workers=-1)
            _too_far  = _dist.reshape(XX.shape) > _max_dist
            fill_base_raw[_too_far] = np.nan
            print(f"      grid spacing={_spacing:.0f} m | max_dist={_max_dist:.0f} m")
            # Recompute thickness from real bottom; NaN where no data
            fill_t = np.where(
                ~np.isnan(elev_m) & ~np.isnan(fill_base_raw),
                np.clip(elev_m - fill_base_raw, 0.0, None),
                np.nan,
            )
            # Show bottom only where data exists and thickness > 0
            fill_base = np.where(
                ~np.isnan(fill_base_raw),
                fill_base_raw, np.nan,
            )
            valid_ft = fill_t[~np.isnan(fill_t) & (fill_t > 0)]
            cfg["fill_center"] = (
                float(np.nanpercentile(valid_ft, 90)) if len(valid_ft) > 0
                else cfg["fill_center"]
            )
            print(f"    [Bottom1 shp] {cfg['label']}: fondo "
                  f"{np.nanmin(fill_base_raw):.0f}–{np.nanmax(fill_base_raw):.0f} m.s.n.m. | "
                  f"celdas con dato: {(~np.isnan(fill_base_raw)).sum()} / {fill_base_raw.size}")
        else:
            # Fallback: no points inside basin
            fill_base = np.where(
                ~np.isnan(elev_m) & (fill_t > 20.0), elev_m - fill_t, np.nan)
    else:
        # No BOT shapefile — compute from digitised fill thickness (>20 m threshold)
        fill_base = np.where(
            ~np.isnan(elev_m) & (fill_t > 20.0),
            elev_m - fill_t, np.nan)

    return XX, YY, elev_m, fill_base, fill_t, poly, (xmin, xmax, ymin, ymax)


# ─────────────────────────────────────────────────────────
# COLORES GEOLÓGICOS (estilo Leapfrog)
# ─────────────────────────────────────────────────────────

# Uníad cuaternaria (DEM top): amarillo vivo
DEM_COLOR   = "#f0e030"
DEM_CS      = [[0, DEM_COLOR], [1, DEM_COLOR]]

# Base acuífero (base roca): azul vivo — visible sobre fondo oscuro
BASE_COLOR  = "#00b0ff"
BASE_CS     = [[0, BASE_COLOR], [1, BASE_COLOR]]

# Paredes del bloque: gradiente azul vivo (base) → café/ocre (medio) → amarillo (tope)
WALL_CS = [
    [0.00, "#00b0ff"],   # base → azul vivo (roca/acuífero)
    [0.40, "#4fc3f7"],   # inferior → azul claro
    [0.70, "#b06020"],   # medio → café/ocre (sedimento)
    [1.00, "#f0e030"],   # tope → amarillo (DEM)
]

# Mantener alias para no romper referencias residuales
TERRAIN_CS = DEM_CS
AQUIFER_CS = BASE_CS


# ─────────────────────────────────────────────────────────
# HELPER: paredes laterales del bloque acuífero
# ─────────────────────────────────────────────────────────

def _add_block_walls(fig, Xn, Yn, ZZ, fill_base, fill_t, fill_cmax,
                    cs, cmin, cmax, row=None, col=None):
    """Rellena el volumen entre DEM y base acuífero añadiendo 4 paredes
    verticales en los bordes N/S/E/W de la cuadrícula, coloreadas por elevación."""
    extra = dict(row=row, col=col) if row is not None else {}
    for axis, idx in [("row", 0), ("row", -1), ("col", 0), ("col", -1)]:
        if axis == "row":
            xe  = Xn[idx, :];  ye  = Yn[idx, :]
            zt  = ZZ[idx, :];  zb  = fill_base[idx, :];  ft = fill_t[idx, :]
        else:
            xe  = Xn[:, idx];  ye  = Yn[:, idx]
            zt  = ZZ[:, idx];  zb  = fill_base[:, idx];  ft = fill_t[:, idx]

        # superficie de 2 filas: fila 0 = base acuífero, fila 1 = DEM
        Xw = np.array([xe, xe])
        Yw = np.array([ye, ye])
        Zw = np.array([zb, zt])
        # color = elevación (misma escala que DEM)
        Cw = Zw

        fig.add_trace(go.Surface(
            x=Xw, y=Yw, z=Zw,
            colorscale=WALL_CS,
            cmin=cmin, cmax=cmax,
            surfacecolor=Cw,
            opacity=1.0,
            showscale=False,
            showlegend=False,
            name="Pared bloque",
            hovertemplate="Elev: %{z:.0f} m<extra>Pared</extra>",
            lighting=dict(ambient=0.6, diffuse=0.75, roughness=0.30, specular=0.45),
        ), **extra)


def _drape_river_coords(gdf_rivers, XX, YY, ZZ, xc, yc, z_offset=25):
    """Builds x/y/z/hover lists (with None separators) for all river segments
    draped on the DEM surface. One Scatter3d trace covers all rivers.
    Returns (xs, ys, zs, hover_texts)."""
    xi_1d = XX[0, :]
    yi_1d = YY[:, 0]
    valid = ZZ[~np.isnan(ZZ)]
    zfill  = float(np.min(valid)) if len(valid) > 0 else 0.0
    ZZ_filled = np.where(np.isnan(ZZ), zfill, ZZ)
    xs, ys, zs, hs = [], [], [], []
    nombre_col = "NOMBRE" if "NOMBRE" in gdf_rivers.columns else None
    for idx, row in gdf_rivers.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        nombre = str(row[nombre_col]) if nombre_col and pd.notna(row[nombre_col]) else ""
        hover_val = f"<b>{nombre}</b>" if nombre else "s/n"
        lines = list(geom.geoms) if geom.geom_type == "MultiLineString" else [geom]
        for line in lines:
            coords = np.array(line.coords)
            step = max(1, len(coords) // 300)
            coords = coords[::step]
            x_seg = (coords[:, 0] - xc) / 1000
            y_seg = (coords[:, 1] - yc) / 1000
            col_f = np.clip(
                (coords[:, 0] - xi_1d[0]) / (xi_1d[-1] - xi_1d[0]) * (len(xi_1d) - 1),
                0, len(xi_1d) - 1)
            row_f = np.clip(
                (coords[:, 1] - yi_1d[0]) / (yi_1d[-1] - yi_1d[0]) * (len(yi_1d) - 1),
                0, len(yi_1d) - 1)
            z_seg = map_coordinates(ZZ_filled, [row_f, col_f], order=1, mode="nearest") + z_offset
            xs.extend(x_seg.tolist() + [None])
            ys.extend(y_seg.tolist() + [None])
            zs.extend(z_seg.tolist() + [None])
            hs.extend([hover_val] * len(x_seg) + [None])
    return xs, ys, zs, hs


# ─────────────────────────────────────────────────────────
# POZOS DE BOMBEO (pozos_acuifero.csv — subterranea==True)
# ─────────────────────────────────────────────────────────

def _build_well_traces(cfg, XX, YY, ZZ, xc, yc, showlegend=True):
    """Returns a list of Scatter3d traces representing pumping wells.

    Each well is drawn as:
      - A diamond marker sitting 15 m above the local DEM surface.
      - A vertical green line from the DEM surface down to the well bottom
        (surface − prof_m) when prof_m is known.

    Parameters
    ----------
    cfg       : basin config dict (must have key 'well_cuenca')
    XX, YY, ZZ: terrain grid arrays (m, UTM 19S)
    xc, yc    : basin centre coordinates (m) — same used for km-relative axes
    showlegend: whether the marker trace appears in the figure legend
    """
    cuenca_name = cfg.get("well_cuenca", "")
    if not cuenca_name or not os.path.exists(WELLS_CSV):
        return []

    df = pd.read_csv(WELLS_CSV)
    df_w = df[
        (df["cuenca"] == cuenca_name) & (df["subterranea"] == True)
    ].dropna(subset=["E_wgs84", "N_wgs84"]).reset_index(drop=True)

    if len(df_w) == 0:
        return []

    # ── Sample DEM at each well location ──────────────────
    xi_1d = XX[0, :]
    yi_1d = YY[:, 0]
    if np.any(np.isnan(ZZ)):
        _i, _j = distance_transform_edt(np.isnan(ZZ), return_distances=False, return_indices=True)
        ZZ_f = ZZ[_i, _j]
    else:
        ZZ_f = ZZ.copy()

    wx = df_w["E_wgs84"].values.astype("float64")
    wy = df_w["N_wgs84"].values.astype("float64")
    col_f = np.clip(
        (wx - xi_1d[0]) / (xi_1d[-1] - xi_1d[0]) * (len(xi_1d) - 1), 0, len(xi_1d) - 1
    )
    row_f = np.clip(
        (wy - yi_1d[0]) / (yi_1d[-1] - yi_1d[0]) * (len(yi_1d) - 1), 0, len(yi_1d) - 1
    )
    z_surf = map_coordinates(ZZ_f.astype("float32"), [row_f, col_f], order=1, mode="nearest")

    # Convert to km-relative
    wx_r = (wx - xc) / 1000
    wy_r = (wy - yc) / 1000
    z_head = z_surf + 15.0   # 15 m above terrain — clearly visible above DEM surface

    # ── Hover labels ──────────────────────────────────────
    hover_text = []
    for _, row in df_w.iterrows():
        q_str = f"{row['caudal_ls']:.2f} l/s" if pd.notna(row.get("caudal_ls")) else "s/d"
        p_str = f"{row['prof_m']:.0f} m" if pd.notna(row.get("prof_m")) else "s/d"
        hover_text.append(
            f"<b>{row['codigo']}</b><br>"
            f"Caudal: {q_str}<br>"
            f"Prof: {p_str}<br>"
            f"Z terreno: {z_surf[_]:.0f} m"
        )

    traces = []

    # ── 1. Well-head markers ──────────────────────────────
    traces.append(go.Scatter3d(
        x=wx_r, y=wy_r, z=z_head,
        mode="markers",
        marker=dict(
            symbol="diamond",
            size=7,
            color="#00e676",
            line=dict(color="#000000", width=1),
        ),
        name="Pozos de bombeo",
        hovertext=hover_text,
        hovertemplate="%{hovertext}<extra></extra>",
        showlegend=showlegend,
    ))

    # ── 2. Vertical bore lines (only where prof_m known) ──
    mask_depth = df_w["prof_m"].notna().values
    if mask_depth.any():
        prof = np.where(mask_depth, df_w["prof_m"].fillna(0).values, 0.0)
        xs_b, ys_b, zs_b = [], [], []
        for i in range(len(df_w)):
            if mask_depth[i]:
                xs_b += [wx_r[i], wx_r[i], None]
                ys_b += [wy_r[i], wy_r[i], None]
                zs_b += [z_surf[i], z_surf[i] - prof[i], None]
        traces.append(go.Scatter3d(
            x=xs_b, y=ys_b, z=zs_b,
            mode="lines",
            line=dict(color="#00e676", width=3),
            name="Sondaje pozos",
            showlegend=False,
            hoverinfo="skip",
        ))

    return traces


# ─────────────────────────────────────────────────────────
# ESTACIONES FLUVIOMÉTRICAS (data_set_oferta_hidrica.xlsx — Oferta_Superficial)
# ─────────────────────────────────────────────────────────

def _build_gauge_traces(cfg, XX, YY, ZZ, xc, yc, showlegend=True):
    """Returns Scatter3d traces for the streamflow gauge of the basin.

    Each gauge is drawn as:
      - A blue circle marker at 20 m above terrain.
      - A short vertical pole from the terrain surface up to the marker.
    Hover tooltip shows station name, code, and full flow statistics.
    """
    gauge_row = cfg.get("gauge_row", None)
    if gauge_row is None or not os.path.exists(OF_HIDRICA_XLSX):
        return []

    df = pd.read_excel(OF_HIDRICA_XLSX, sheet_name="Oferta_Superficial")
    if gauge_row >= len(df):
        return []
    row = df.iloc[gauge_row]

    wx = float(row["ESTE_84"])
    wy = float(row["NORTE_84"])

    # ── Sample DEM at gauge location ──────────────────────
    xi_1d = XX[0, :]
    yi_1d = YY[:, 0]
    if np.any(np.isnan(ZZ)):
        _i, _j = distance_transform_edt(np.isnan(ZZ), return_distances=False, return_indices=True)
        ZZ_f = ZZ[_i, _j]
    else:
        ZZ_f = ZZ.copy()
    col_f = np.array([np.clip(
        (wx - xi_1d[0]) / (xi_1d[-1] - xi_1d[0]) * (len(xi_1d) - 1), 0, len(xi_1d) - 1)])
    row_f = np.array([np.clip(
        (wy - yi_1d[0]) / (yi_1d[-1] - yi_1d[0]) * (len(yi_1d) - 1), 0, len(yi_1d) - 1)])
    z_surf = float(map_coordinates(ZZ_f.astype("float32"), [row_f, col_f], order=1, mode="nearest")[0])

    wx_r = (wx - xc) / 1000
    wy_r = (wy - yc) / 1000
    z_head = z_surf + 20.0

    hover = (
        f"<b>{row['NOMBRE']}</b><br>"
        f"Código BNA: {row['COD_BNA']}<br>"
        f"Caudal medio: {row['Caudal_medio_m3s']:.2f} m³/s<br>"
        f"Q10: {row['Q10_m3s']:.2f} m³/s<br>"
        f"Q50: {row['Q50_m3s']:.2f} m³/s<br>"
        f"Q85: {row['Q85_m3s']:.2f} m³/s<br>"
        f"Q95: {row['Q95_m3s']:.2f} m³/s"
    )

    return [
        go.Scatter3d(
            x=[wx_r], y=[wy_r], z=[z_head],
            mode="markers",
            marker=dict(symbol="circle", size=10, color="#29b6f6",
                        line=dict(color="#000000", width=1)),
            name="Estación fluviométrica",
            hovertext=[hover],
            hovertemplate="%{hovertext}<extra></extra>",
            showlegend=showlegend,
        ),
        go.Scatter3d(
            x=[wx_r, wx_r, None], y=[wy_r, wy_r, None], z=[z_surf, z_head, None],
            mode="lines",
            line=dict(color="#29b6f6", width=4),
            name="Estación (poste)",
            showlegend=False,
            hoverinfo="skip",
        ),
    ]


# ─────────────────────────────────────────────────────────
# LAGUNAS (Lagunas.shp — polígonos)
# ─────────────────────────────────────────────────────────

def _build_laguna_traces(poly, XX, YY, ZZ, xc, yc, showlegend=True):
    """Returns Surface + Scatter3d outline traces for lakes that intersect the basin.

    A local 50-m resolution grid is built for each laguna so the fill is dense
    regardless of the coarse DEM grid spacing.  z_lake = max DEM inside the
    polygon + 8 m so it always sits visibly above the terrain surface.
    """
    from matplotlib.path import Path as _MplPath

    if not os.path.exists(LAGUNAS_SHP):
        return []

    gdf_lag = gpd.read_file(LAGUNAS_SHP)
    gdf_lag = gdf_lag[gdf_lag.intersects(poly)].reset_index(drop=True)
    if len(gdf_lag) == 0:
        return []

    xi_1d = XX[0, :]
    yi_1d = YY[:, 0]
    if np.any(np.isnan(ZZ)):
        _i, _j = distance_transform_edt(np.isnan(ZZ), return_distances=False, return_indices=True)
        ZZ_f = ZZ[_i, _j]
    else:
        ZZ_f = ZZ.copy()

    traces = []
    legend_shown = False

    for _, row in gdf_lag.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        nombre = str(row["NOMBRE"]) if pd.notna(row.get("NOMBRE")) else "Laguna s/n"

        # ── Build a local fine grid (50 m resolution) for this laguna ─────────
        bx_min, by_min, bx_max, by_max = geom.bounds
        step_m = 50
        lag_x = np.arange(bx_min, bx_max + step_m, step_m)
        lag_y = np.arange(by_min, by_max + step_m, step_m)
        if len(lag_x) < 2:
            lag_x = np.linspace(bx_min, bx_max, 10)
        if len(lag_y) < 2:
            lag_y = np.linspace(by_min, by_max, 10)
        LX, LY = np.meshgrid(lag_x, lag_y)

        # ── Rasterise polygon on the fine grid ────────────────────────────────
        path = _MplPath(np.array(geom.exterior.coords))
        mask = path.contains_points(np.column_stack([LX.ravel(), LY.ravel()])).reshape(LX.shape)
        if not mask.any():
            continue

        # ── Sample DEM at fine-grid points and set lake surface above terrain ─
        col_f = np.clip(
            (LX.ravel() - xi_1d[0]) / (xi_1d[-1] - xi_1d[0]) * (len(xi_1d) - 1),
            0, len(xi_1d) - 1)
        row_f_arr = np.clip(
            (LY.ravel() - yi_1d[0]) / (yi_1d[-1] - yi_1d[0]) * (len(yi_1d) - 1),
            0, len(yi_1d) - 1)
        z_dem = map_coordinates(ZZ_f.astype("float32"), [row_f_arr, col_f],
                                order=1, mode="nearest").reshape(LX.shape)
        # Use max DEM inside polygon + offset so lake floats above the terrain mesh
        z_lake = float(np.nanmax(z_dem[mask])) + 8

        Lx_rel = (LX - xc) / 1000
        Ly_rel = (LY - yc) / 1000
        Z_surf = np.where(mask, z_lake, np.nan)

        _sl = showlegend and not legend_shown
        legend_shown = True

        traces.append(go.Surface(
            x=Lx_rel, y=Ly_rel, z=Z_surf,
            colorscale=[[0, "#64b5f6"], [1, "#64b5f6"]],
            showscale=False,
            opacity=0.90,
            name="Lagunas",
            showlegend=_sl,
            hovertemplate=f"<b>{nombre}</b><br>Elev: {z_lake:.0f} m<extra>Laguna</extra>",
            lighting=dict(ambient=1.0, diffuse=0.0, roughness=0.0, specular=0.0),
            cmin=z_lake, cmax=z_lake,
        ))

        # Closed outline border 5 m above the lake surface
        ext = np.array(geom.exterior.coords)
        step = max(1, len(ext) // 300)
        ext = ext[::step]
        x_out = np.append((ext[:, 0] - xc) / 1000, (ext[0, 0] - xc) / 1000)
        y_out = np.append((ext[:, 1] - yc) / 1000, (ext[0, 1] - yc) / 1000)
        z_out = np.full(len(x_out), z_lake + 5)
        traces.append(go.Scatter3d(
            x=x_out, y=y_out, z=z_out,
            mode="lines",
            line=dict(color="#0288d1", width=2),
            name="Lagunas (borde)",
            showlegend=False,
            hoverinfo="skip",
        ))

    return traces


# ─────────────────────────────────────────────────────────
# HELPERS DE EJES UTM
# ─────────────────────────────────────────────────────────

def _utm_ticks(center_m, lo_m, hi_m, step_km=None):
    """Return (tickvals, ticktext) for a Plotly 3D axis.

    tickvals are in relative-km space (coord - center)/1000;
    ticktext shows the actual UTM coordinate in metres.
    """
    range_km = (hi_m - lo_m) / 1000
    if step_km is None:
        if range_km <= 15:
            step_km = 2
        elif range_km <= 30:
            step_km = 5
        elif range_km <= 60:
            step_km = 10
        else:
            step_km = 20
    lo_utmkm = lo_m / 1000
    hi_utmkm = hi_m / 1000
    lo_tick = np.ceil(lo_utmkm / step_km) * step_km
    hi_tick = np.floor(hi_utmkm / step_km) * step_km
    actual_km = np.arange(lo_tick, hi_tick + 1e-6, step_km)
    relative = actual_km - center_m / 1000
    return relative.tolist(), [f"{v*1000:.0f}" for v in actual_km]


# ─────────────────────────────────────────────────────────
# CONSTRUIR FIGURA POR CUENCA
# ─────────────────────────────────────────────────────────

def build_figure_single(name, cfg):
    XX, YY, ZZ, fill_base, fill_t, poly, bbox = build_terrain_and_fill(cfg)
    xmin, xmax, ymin, ymax = bbox

    # Centrar coordenadas (más fácil de leer en ejes)
    xc = (xmin + xmax) / 2
    yc = (ymin + ymax) / 2
    Xn = (XX - xc) / 1000   # km relativo
    Yn = (YY - yc) / 1000

    # Tick values showing real UTM km on axes
    _tv_e, _tt_e = _utm_ticks(xc, xmin, xmax)
    _tv_n, _tt_n = _utm_ticks(yc, ymin, ymax)

    z_range = [cfg["elev_min"] - cfg["fill_center"] * 1.5, cfg["elev_max"] * 1.05]

    # Rangos exactos derivados de los arrays reales
    dem_zmin  = float(np.nanmin(ZZ))
    dem_zmax  = float(np.nanmax(ZZ))
    with np.errstate(all="ignore"):
        base_zmin = float(np.nanmin(fill_base)) if not np.all(np.isnan(fill_base)) else dem_zmin - cfg["fill_center"]
        base_zmax = float(np.nanmax(fill_base)) if not np.all(np.isnan(fill_base)) else dem_zmin
    # Extend z_range downward to always show the real aquifer bottom
    z_range[0] = min(z_range[0], base_zmin - 20)

    fig = go.Figure()

    # ── 1. DEM — sólido, color plano amarillo ─────────────────────
    fig.add_trace(go.Surface(
        x=Xn, y=Yn, z=ZZ,
        colorscale=DEM_CS,
        cmin=dem_zmin, cmax=dem_zmax,
        opacity=1.0,
        name="Terreno (DEM)",
        showscale=False,
        hovertemplate="E: %{x:.2f} km<br>N: %{y:.2f} km<br>Elev DEM: %{z:.0f} m<extra>Terreno</extra>",
        lighting=dict(ambient=0.65, diffuse=0.75, roughness=0.40,
                      specular=0.30, fresnel=0.05),
        lightposition=dict(x=2000, y=2000, z=5000),
    ))

    # ── 2. Base acuífero (Bottom1 m.s.n.m. o DEM − espesor), color plano rojo ──
    _base_name = ("Base acuífero (Bottom1 m.s.n.m.)" if cfg.get("bot_shp")
                  else "Base acuífero (DEM − espesor)")
    fig.add_trace(go.Surface(
        x=Xn, y=Yn, z=fill_base,
        colorscale=BASE_CS,
        cmin=base_zmin, cmax=base_zmax,
        opacity=1.0,
        name=_base_name,
        showscale=False,
        hovertemplate=("Base elev: %{z:.0f} m<br>"
                       "Espesor relleno: %{customdata:.1f} m<extra>Base acuífero</extra>"),
        customdata=fill_t,
        lighting=dict(ambient=1.0, diffuse=0.0, roughness=0.0, specular=0.0),
    ))

    # ── 3. Paredes del bloque — rellenan el volumen entre DEM y base acuífero ──
    _add_block_walls(fig, Xn, Yn, ZZ, fill_base, fill_t, cfg["fill_center"],
                     TERRAIN_CS, base_zmin, dem_zmax)

    # ── 4. Contorno de la cuenca (línea 3D drapeada sobre terreno) ──
    ext_coords = np.array(poly.exterior.coords)
    # Muestrear cada 20 puntos para no saturar
    step = max(1, len(ext_coords) // 200)
    ext_s = ext_coords[::step]
    x_line = (ext_s[:, 0] - xc) / 1000
    y_line = (ext_s[:, 1] - yc) / 1000
    # Drapear línea sobre el terreno real: muestrear ZZ en cada vértice
    xi_1d = XX[0, :]          # coordenadas X del grid (1D)
    yi_1d = YY[:, 0]          # coordenadas Y del grid (1D)
    col_frac = (ext_s[:, 0] - xi_1d[0]) / (xi_1d[-1] - xi_1d[0]) * (len(xi_1d) - 1)
    row_frac = (ext_s[:, 1] - yi_1d[0]) / (yi_1d[-1] - yi_1d[0]) * (len(yi_1d) - 1)
    # Nearest-valid fill so boundary doesn't dive to elev_min where DEM is nodata
    if np.any(np.isnan(ZZ)):
        _i, _j = distance_transform_edt(np.isnan(ZZ), return_distances=False, return_indices=True)
        ZZ_filled = ZZ[_i, _j]
    else:
        ZZ_filled = ZZ
    z_sampled = map_coordinates(ZZ_filled.astype("float32"), [row_frac, col_frac], order=1, mode="nearest")
    z_line = z_sampled + 40   # 40 m sobre el terreno para visibilidad

    fig.add_trace(go.Scatter3d(
        x=x_line, y=y_line, z=z_line,
        mode="lines",
        line=dict(color="#00e5ff", width=3),
        name="Límite cuenca",
        showlegend=True,
        hoverinfo="skip",
    ))

    # ── 5. Red hidrológica drapeada sobre terreno ──────────
    river_shp = resolve_input(os.path.join("01 Etapa 1", "Anexos", "Anexo E - SIG", "04_Geodatabases", "PERHC", cfg.get("river_shp", "")))
    if cfg.get("river_shp") and os.path.exists(river_shp):
        gdf_r = gpd.read_file(river_shp)
        rx, ry, rz, rh = _drape_river_coords(gdf_r, XX, YY, ZZ, xc, yc, z_offset=25)
        fig.add_trace(go.Scatter3d(
            x=rx, y=ry, z=rz,
            mode="lines",
            line=dict(color="#1a6aff", width=2),
            name="Red hidrológica",
            text=rh,
            hovertemplate="%{text}<extra>Red hidrológica</extra>",
        ))

    # ── 6. Lagunas ──────────────────────────────────────
    for tr in _build_laguna_traces(poly, XX, YY, ZZ, xc, yc, showlegend=True):
        fig.add_trace(tr)

    # ── 7. Pozos de bombeo ────────────────────────────────
    for tr in _build_well_traces(cfg, XX, YY, ZZ, xc, yc, showlegend=True):
        fig.add_trace(tr)

    # ── 8. Estación fluviométrica ─────────────────────────
    for tr in _build_gauge_traces(cfg, XX, YY, ZZ, xc, yc, showlegend=True):
        fig.add_trace(tr)

    # ── 9. Tabla oferta subterránea (Penitente y El Oro) ──
    _gw_col = cfg.get("gw_col", "")
    _has_gw_table = bool(_gw_col) and os.path.exists(OF_HIDRICA_XLSX)
    if _has_gw_table:
        df_gw = pd.read_excel(OF_HIDRICA_XLSX, sheet_name="Oferta_Subterránea")
        fig.add_trace(go.Table(
            domain=dict(x=[0.05, 0.55], y=[0.01, 0.22]),
            header=dict(
                values=["<b>Componente recarga</b>", f"<b>Caudal (m³/s) — {cfg['label']}</b>"],
                fill_color="#1a2a3a",
                font=dict(color=LF_FONT, size=11, family="Arial"),
                align=["left", "right"],
                line_color=LF_AXIS,
            ),
            cells=dict(
                values=[df_gw["Entradas"].tolist(), df_gw[_gw_col].round(4).tolist()],
                fill_color="#0f2540",
                font=dict(color=LF_FONT, size=10, family="Arial"),
                align=["left", "right"],
                line_color=LF_AXIS,
            ),
        ))

    # ── Layout Leapfrog ──────────────────────────────────
    if cfg.get("bot_shp"):
        fill_note = (
            f"Base acuífero interpolada desde: {cfg['bot_shp']} — campo Bottom1 (m.s.n.m.). "
            f"Puntos que intersectan la cuenca {cfg['label']}. "
            f"Espesor máximo (p90): {cfg['fill_center']:.0f} m"
        )
    else:
        fill_note = (
            f"Espesor relleno digitalizado de: Figura 75 — Espesor del relleno cuaternario "
            f"(acuífero libre) en los modelos PEGH Vertientes del Atlántico y Tierra del Fuego "
            f"(DGA, 2021). Máx. {cfg['fill_center']:.0f} m en valle | Mín. {cfg['fill_edge']:.0f} m en bordes"
        )

    # Build scene dict — raise domain when GW table occupies the lower 24%
    _scene = dict(
        bgcolor=LF_BG,
        xaxis=dict(title="E (m)", gridcolor=LF_AXIS,
                   zerolinecolor=LF_AXIS, backgroundcolor=LF_BG,
                   color=LF_FONT, showspikes=False,
                   tickvals=_tv_e, ticktext=_tt_e),
        yaxis=dict(title="N (m)", gridcolor=LF_AXIS,
                   zerolinecolor=LF_AXIS, backgroundcolor=LF_BG,
                   color=LF_FONT, showspikes=False,
                   tickvals=_tv_n, ticktext=_tt_n),
        zaxis=dict(title="Elevación (m)", range=z_range,
                   gridcolor=LF_AXIS, zerolinecolor=LF_AXIS,
                   backgroundcolor=LF_BG, color=LF_FONT, showspikes=False),
        camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=-0.15),
            eye=dict(x=1.4, y=-1.7, z=1.1),
        ),
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=0.85),
    )
    if _has_gw_table:
        _scene["domain"] = dict(x=[0, 1], y=[0.25, 1.0])

    _anns = [dict(
        text=fill_note,
        x=0.5, y=-0.01,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(color="#8899aa", size=7.5),
        align="center",
    )]
    if _has_gw_table:
        _anns.append(dict(
            text="<b>Oferta Subterránea — Entradas al acuífero</b>",
            x=0.30, y=0.235,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(color=LF_FONT, size=10, family="Arial"),
            align="center",
        ))

    # ── Proxy legend traces (Surface traces don't render legend swatches) ──
    # Only for Surface layers — Scatter3d traces already show in legend on their own
    for _leg_name, _leg_color in [
        ("Terreno (DEM)",  DEM_COLOR),
        ("Base acuífero",  BASE_COLOR),
    ]:
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode="lines",
            line=dict(color=_leg_color, width=6),
            name=_leg_name,
            showlegend=True,
            hoverinfo="skip",
        ))

    fig.update_layout(
        title=dict(
            text=cfg["title"],
            font=dict(family="Arial", size=15, color=LF_FONT),
            x=0.5, y=0.97
        ),
        paper_bgcolor=LF_PAPER,
        plot_bgcolor=LF_BG,
        font=dict(family="Arial", color=LF_FONT),
        scene=_scene,
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(15,37,64,0.90)",
            bordercolor=LF_AXIS, borderwidth=1,
            font=dict(color=LF_FONT, size=11),
        ),
        margin=dict(l=0, r=120, t=60, b=5),
        annotations=_anns,
        width=1100, height=950 if _has_gw_table else 750,
    )

    return fig


# ─────────────────────────────────────────────────────────
# FIGURA COMBINADA — 3 cuencas en subplot 1×3
# ─────────────────────────────────────────────────────────

def build_combined_figure():
    """Genera una figura HTML con las 3 cuencas en columnas."""
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{"type": "scene"}, {"type": "scene"}, {"type": "scene"}]],
        horizontal_spacing=0.02,
    )

    for col_idx, (name, cfg) in enumerate(CUENCAS_CFG.items(), start=1):
        print(f"  Procesando {name}...")
        XX, YY, ZZ, fill_base, fill_t, poly, bbox = build_terrain_and_fill(cfg)
        xmin, xmax, ymin, ymax = bbox
        xc = (xmin + xmax) / 2
        yc = (ymin + ymax) / 2
        Xn = (XX - xc) / 1000
        Yn = (YY - yc) / 1000

        # Tick values showing real UTM km on axes
        _tv_e, _tt_e = _utm_ticks(xc, xmin, xmax)
        _tv_n, _tt_n = _utm_ticks(yc, ymin, ymax)

        scene_k = f"scene{col_idx}" if col_idx > 1 else "scene"

        # ── DEM — color plano amarillo ──
        dem_zmin  = float(np.nanmin(ZZ))
        dem_zmax  = float(np.nanmax(ZZ))
        with np.errstate(all="ignore"):
            base_zmin = float(np.nanmin(fill_base)) if not np.all(np.isnan(fill_base)) else dem_zmin - cfg["fill_center"]
            base_zmax = float(np.nanmax(fill_base)) if not np.all(np.isnan(fill_base)) else dem_zmin
        fig.add_trace(go.Surface(
            x=Xn, y=Yn, z=ZZ,
            colorscale=DEM_CS,
            cmin=dem_zmin, cmax=dem_zmax,
            opacity=1.0,
            name=f"DEM — {cfg['label']}",
            showscale=False,
            lighting=dict(ambient=0.65, diffuse=0.75, roughness=0.40, specular=0.30),
            showlegend=False,
        ), row=1, col=col_idx)

        # ── Base acuífero — color plano rojo ──
        fig.add_trace(go.Surface(
            x=Xn, y=Yn, z=fill_base,
            colorscale=BASE_CS,
            cmin=base_zmin, cmax=base_zmax,
            opacity=1.0,
            name=f"Base acuífero — {cfg['label']}",
            showscale=False,
            hovertemplate=("Base elev: %{z:.0f} m<br>"
                           "Espesor: %{customdata:.1f} m<extra>Base acuífero</extra>"),
            customdata=fill_t,
            lighting=dict(ambient=1.0, diffuse=0.0, roughness=0.0, specular=0.0),
            showlegend=False,
        ), row=1, col=col_idx)

        # Paredes del bloque
        _add_block_walls(fig, Xn, Yn, ZZ, fill_base, fill_t,
                         cfg["fill_center"], TERRAIN_CS, base_zmin, dem_zmax,
                         row=1, col=col_idx)

        # Contorno cuenca — drapeado sobre DEM
        ext_coords = np.array(poly.exterior.coords)
        step = max(1, len(ext_coords) // 150)
        ext_s = ext_coords[::step]
        x_l = (ext_s[:, 0] - xc) / 1000
        y_l = (ext_s[:, 1] - yc) / 1000
        xi_1d_c = XX[0, :]; yi_1d_c = YY[:, 0]
        if np.any(np.isnan(ZZ)):
            _ic, _jc = distance_transform_edt(np.isnan(ZZ), return_distances=False, return_indices=True)
            ZZ_f_c = ZZ[_ic, _jc]
        else:
            ZZ_f_c = ZZ.copy()
        col_frac_c = np.clip(
            (ext_s[:, 0] - xi_1d_c[0]) / (xi_1d_c[-1] - xi_1d_c[0]) * (len(xi_1d_c) - 1),
            0, len(xi_1d_c) - 1)
        row_frac_c = np.clip(
            (ext_s[:, 1] - yi_1d_c[0]) / (yi_1d_c[-1] - yi_1d_c[0]) * (len(yi_1d_c) - 1),
            0, len(yi_1d_c) - 1)
        z_l = map_coordinates(ZZ_f_c, [row_frac_c, col_frac_c], order=1, mode="nearest") + 40

        fig.add_trace(go.Scatter3d(
            x=x_l, y=y_l, z=z_l,
            mode="lines",
            line=dict(color="#00e5ff", width=2),
            name=f"Límite — {cfg['label']}",
            showlegend=False,
        ), row=1, col=col_idx)

        # Red hidrológica drapeada sobre terreno
        river_shp = resolve_input(os.path.join("01 Etapa 1", "Anexos", "Anexo E - SIG", "04_Geodatabases", "PERHC", cfg.get("river_shp", "")))
        if cfg.get("river_shp") and os.path.exists(river_shp):
            gdf_r = gpd.read_file(river_shp)
            rx, ry, rz, rh = _drape_river_coords(gdf_r, XX, YY, ZZ, xc, yc, z_offset=25)
            fig.add_trace(go.Scatter3d(
                x=rx, y=ry, z=rz,
                mode="lines",
                line=dict(color="#1a6aff", width=2),
                name=f"Ríos — {cfg['label']}",
                showlegend=False,
                text=rh,
                hovertemplate="%{text}<extra>Red hidrológica</extra>",
            ), row=1, col=col_idx)

        # Pozos de bombeo
        for tr in _build_well_traces(cfg, XX, YY, ZZ, xc, yc, showlegend=False):
            fig.add_trace(tr, row=1, col=col_idx)

        # Estación fluviométrica
        for tr in _build_gauge_traces(cfg, XX, YY, ZZ, xc, yc, showlegend=False):
            fig.add_trace(tr, row=1, col=col_idx)

        # Lagunas
        for tr in _build_laguna_traces(poly, XX, YY, ZZ, xc, yc, showlegend=False):
            fig.add_trace(tr, row=1, col=col_idx)

        # Configurar escena
        dem_zmn = float(np.nanmin(ZZ))
        with np.errstate(all="ignore"):
            base_zmn = (float(np.nanmin(fill_base))
                        if not np.all(np.isnan(fill_base))
                        else dem_zmn - cfg["fill_center"])
        z_range = [min(cfg["elev_min"] - cfg["fill_center"] * 1.5, base_zmn - 20),
                   cfg["elev_max"] * 1.05]
        # Explicit x domains for make_subplots(1,3,horizontal_spacing=0.02)
        _col_x = {1: [0.00, 0.32], 2: [0.34, 0.66], 3: [0.68, 1.00]}
        fig.update_layout(**{scene_k: dict(
            bgcolor=LF_BG,
            domain=dict(x=_col_x[col_idx], y=[0.25, 0.97]),
            xaxis=dict(title="E (m)", gridcolor=LF_AXIS, backgroundcolor=LF_BG,
                       color=LF_FONT, showspikes=False,
                       tickvals=_tv_e, ticktext=_tt_e,
                       tickfont=dict(size=8)),
            yaxis=dict(title="N (m)", gridcolor=LF_AXIS, backgroundcolor=LF_BG,
                       color=LF_FONT, showspikes=False,
                       tickvals=_tv_n, ticktext=_tt_n,
                       tickfont=dict(size=8)),
            zaxis=dict(title="Z (m)", range=z_range, gridcolor=LF_AXIS,
                       backgroundcolor=LF_BG, color=LF_FONT, showspikes=False),
            camera=dict(eye=dict(x=1.5, y=-1.9, z=0.85)),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=0.50),
        )})

    # ── Oferta subterránea — tables below Penitente and El Oro ─────
    if os.path.exists(OF_HIDRICA_XLSX):
        df_gw = pd.read_excel(OF_HIDRICA_XLSX, sheet_name="Oferta_Subterránea")
        for _gw_col, _tbl_x, _lbl in [
            ("Cuenca Penitente (m3_s)", [0.01, 0.31], "Penitente"),
            ("Cuenca Oro (m3_s)",       [0.35, 0.65], "El Oro"),
        ]:
            fig.add_trace(go.Table(
                domain=dict(x=_tbl_x, y=[0.01, 0.21]),
                header=dict(
                    values=["<b>Componente recarga</b>",
                            f"<b>Caudal (m\u00b3/s) \u2014 {_lbl}</b>"],
                    fill_color="#1a2a3a",
                    font=dict(color=LF_FONT, size=10, family="Arial"),
                    align=["left", "right"],
                    line_color=LF_AXIS,
                ),
                cells=dict(
                    values=[df_gw["Entradas"].tolist(),
                            df_gw[_gw_col].round(4).tolist()],
                    fill_color="#0f2540",
                    font=dict(color=LF_FONT, size=10, family="Arial"),
                    align=["left", "right"],
                    line_color=LF_AXIS,
                ),
            ))

    fig.update_layout(
        title=dict(
            text="<b>MODELO 3D INTERACTIVO \u2014 ESPESOR RELLENO CUATERNARIO</b>",
            font=dict(family="Arial", size=14, color=LF_FONT),
            x=0.5, y=0.99,
        ),
        paper_bgcolor=LF_PAPER,
        font=dict(family="Arial", color=LF_FONT),
        margin=dict(l=0, r=100, t=110, b=10),
        width=1600, height=900,
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
        annotations=[
            # ── Basin titles — one per scene column ──────────────────
            dict(text="<b>R\u00edo Penitente</b>",
                 x=0.155, y=1.07, xref="paper", yref="paper", showarrow=False,
                 font=dict(family="Arial", size=12, color=LF_FONT), align="center"),
            dict(text="<b>R\u00edo El Oro</b>",
                 x=0.500, y=1.07, xref="paper", yref="paper", showarrow=False,
                 font=dict(family="Arial", size=12, color=LF_FONT), align="center"),
            dict(text="<b>R\u00edo R\u00f3balo</b>",
                 x=0.845, y=1.07, xref="paper", yref="paper", showarrow=False,
                 font=dict(family="Arial", size=12, color=LF_FONT), align="center"),
            # ── GW table titles ───────────────────────────────────────
            dict(text="<b>Oferta Subterr\u00e1nea \u2014 Entradas al acu\u00edfero</b>",
                 x=0.160, y=0.228, xref="paper", yref="paper", showarrow=False,
                 font=dict(family="Arial", size=9.5, color=LF_FONT), align="center"),
            dict(text="<b>Oferta Subterr\u00e1nea \u2014 Entradas al acu\u00edfero</b>",
                 x=0.500, y=0.228, xref="paper", yref="paper", showarrow=False,
                 font=dict(family="Arial", size=9.5, color=LF_FONT), align="center"),
            # ── Legend box — below Róbalo ─────────────────────────────
            dict(
                text=(
                    "<b>Leyenda</b><br>"
                    "<span style='color:#f0e030'>\u25ac</span> Terreno (DEM)<br>"
                    "<span style='color:#00b0ff'>\u25ac</span> Base acu\u00edfero<br>"
                    "<span style='color:#00e5ff'>\u25ac</span> L\u00edmite cuenca<br>"
                    "<span style='color:#1a6aff'>\u25ac</span> Red hidrol\u00f3gica<br>"
                    "<span style='color:#64b5f6'>\u25a0</span> Lagunas<br>"
                    "<span style='color:#00e676'>\u25c6</span> Pozos de bombeo<br>"
                    "<span style='color:#29b6f6'>\u25cf</span> Estaci\u00f3n fluviom\u00e9trica"
                ),
                x=0.840, y=0.21, xref="paper", yref="paper",
                showarrow=False, align="left",
                bgcolor="rgba(15,37,64,0.92)",
                bordercolor=LF_AXIS, borderwidth=1, borderpad=8,
                font=dict(family="Arial", size=12, color=LF_FONT),
            ),
            # ── Footer ───────────────────────────────────────────────
            dict(
                text=(
                    "\u25b2 Terreno (DEM Copernicus GLO-30, EPSG:32719) &nbsp;|\u00a0"
                    "\u25c6 Base acu\u00edfero: Penitente=propsBOT_Vertientes_Proj | El Oro=propsBOT_Fuego_Proj (Bottom1 m.s.n.m.) | R\u00f3balo=espesor Fig. 75 PEGH &nbsp;|\u00a0"
                    "\u2500\u2500 L\u00edmite cuenca &nbsp;|\u00a0 Paleta: Leapfrog / MDSA"
                ),
                x=0.5, y=-0.005, xref="paper", yref="paper",
                showarrow=False, font=dict(color="#6677aa", size=7.5), align="center",
            ),
        ],
    )

    return fig
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*65)
    print("MAPA 3D ESTILO LEAPFROG — CUENCAS MAGALLANES")
    print("DEM + Espesor Relleno Cuaternario (Figura 75 PEGH)")
    print("="*65)

    # ── Figuras individuales ──────────────────────────────
    for name, cfg in CUENCAS_CFG.items():
        print(f"\n  Generando figura individual: {cfg['label']}...")
        fig = build_figure_single(name, cfg)
        ruta_html = os.path.join(FIG_D, f"3D_Leapfrog_{name}.html")
        ruta_png  = os.path.join(FIG_D, f"3D_Leapfrog_{name}.png")
        fig.write_html(ruta_html, include_plotlyjs="cdn", full_html=True,
                       config={"displayModeBar": True,
                               "modeBarButtonsToAdd": ["resetCameraDefault3d"]})
        print(f"  ✓ HTML: {os.path.basename(ruta_html)}")

        # PNG estático (requiere kaleido)
        try:
            fig.write_image(ruta_png, width=1100, height=750, scale=1.5)
            print(f"  ✓ PNG:  {os.path.basename(ruta_png)}")
        except Exception as e:
            print(f"  ⚠ PNG no generado (kaleido no instalado): {e}")

    # ── Figura combinada ─────────────────────────────────
    print("\n  Generando figura combinada (3 cuencas)...")
    fig_combo = build_combined_figure()
    ruta_combo = os.path.join(FIG_D, "3D_Leapfrog_COMBO_3Cuencas.html")
    fig_combo.write_html(ruta_combo, include_plotlyjs="cdn", full_html=True,
                         config={"displayModeBar": True})
    print(f"  ✓ HTML combinado: {os.path.basename(ruta_combo)}")

    print(f"\n{'='*65}")
    print(f"✓ Archivos en: {FIG_D}")
    print("\n  Abrir en navegador para visualización 3D interactiva:")
    for f in os.listdir(FIG_D):
        if f.endswith(".html"):
            print(f"    • {f}")
