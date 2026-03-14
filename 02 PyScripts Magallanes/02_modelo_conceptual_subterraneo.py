"""
Script 02: Modelo Conceptual Subterráneo Preliminar — Por Cuenca
Proyecto: Análisis de Recursos Hídricos - Cuencas Magallanes (IDIEM/DGA)
Propósito: Generar diagramas conceptuales 3D del sistema de aguas subterráneas
           para cada cuenca de estudio por separado (sección transversal + perfil
           hidrogeológico), incluyendo esquematización de balance hídrico subterráneo.
           Resolución Observación DGA N°6 (Sección 5.1.1 del Informe Etapa 1)
Bases DGA: "El modelo conceptual deberá compilarse de forma gráfica en 3D
           en un software apropiado" (Letra F, Etapa I)
Autor: Especialista Senior en Modelación
Fecha: 11-03-2026
Software: Python 3 / matplotlib / numpy (código abierto, entregable a DGA)
"""

import json, os, textwrap
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.gridspec as gridspec
from matplotlib.colors import LightSource
from project_paths import BASE_DIR, PY_SCRIPTS_DIR, resolve_input
try:
    import rasterio
    from rasterio.mask import mask as rio_mask
    import geopandas as gpd
    from scipy.ndimage import zoom as ndimage_zoom
    from scipy.interpolate import griddata, RegularGridInterpolator
    from scipy.spatial import cKDTree
    from shapely.ops import unary_union
    _HAS_GEO = True
except ImportError:
    _HAS_GEO = False

# -------------------------------------------------------------------
# RUTAS
# -------------------------------------------------------------------
OUT_DIR  = PY_SCRIPTS_DIR
JSON_PATH = resolve_input("02 PyScripts Magallanes/datos_cuencas.json")
FIG_DIR  = os.path.join(OUT_DIR, "Figuras_Obs6_ModeloSubterraneo")
os.makedirs(FIG_DIR, exist_ok=True)

# Rutas para datos reales (DEM Copernicus + BOT shapefile + red hidrológica)
BASIN_SHP_02  = resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/area_estudio_total.shp")

# Configuración por cuenca para carga de datos reales
CUENCAS_REAL_CFG = {
    "Penitente": {
        "basin_nombre": "RIO PENITENTE",
        "dem_cop":       "DEM_Cop30_Penitente_UTM19S.tif",
        "bot_shp":       "propsBOT_Vertientes_Proj.shp",
        "bot_buffer":    2400,
        "river_shp":     "red_hidro_penitente.shp",
    },
    "El Oro": {
        "basin_nombre": "RIO DEL ORO",
        "dem_cop":       "DEM_Cop30_El_Oro_UTM19S.tif",
        "bot_shp":       "propsBOT_Fuego_Proj.shp",
        "bot_buffer":    1200,
        "river_shp":     "red_hidro_oro.shp",
    },
    "Robalo": {
        "basin_nombre": "RIO ROBALO",
        "dem_cop":       "DEM_Cop30_Robalo_UTM19S.tif",
        "bot_shp":       None,
        "river_shp":     "red_hidro_robalo.shp",
    },
}

# Cargar datos
with open(JSON_PATH, encoding="utf-8") as f:
    CUENCAS = json.load(f)

# -------------------------------------------------------------------
# CONFIGURACIÓN VISUAL CORPORATIVA DGA/IDIEM
# -------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "figure.facecolor": "white",
    "axes.facecolor": "#F8F8F5",
    "grid.alpha": 0.3,
})

# Paleta de colores geológicos estándar
COLORES = {
    "topografia": "#7B9E6B",     # verde terreno
    "cuaternario": "#E8D5A3",    # amarillo ocre - relleno cuaternario (acuífero)
    "acuifero_sat": "#A8C8E8",   # azul claro - zona saturada
    "NF": "#4A90D9",             # azul oscuro - nivel freático
    "sustrato": "#8B7355",       # café - roca base / sustrato
    "roca_fisurada": "#9B8EA0",  # gris morado - roca fisurada
    "glaciar": "#E8F4FD",        # blanco azulado - hielo/glaciar
    "rio": "#2E86AB",            # azul río
    "lluvia": "#1565C0",         # azul oscuro lluvia
    "recarga": "#27AE60",        # verde recarga
    "descarga": "#E74C3C",       # rojo descarga
    "bombeo": "#F39C12",         # naranja bombeo/extracción
    "ladera": "#A0A0A0",         # gris ladera
    "texto_hidro": "#1A237E",    # azul texto hidrológico
}

DGA_BLUE = "#003087"
IDIEM_RED = "#C41230"

# -------------------------------------------------------------------
# PARÁMETROS GEOLÓGICOS POR CUENCA (para sección transversal)
# -------------------------------------------------------------------

PARAMS_GEOL = {
    "Penitente": {
        "titulo": "Cuenca del Río Penitente",
        "tipo_cuenca": "Valle de Pampa Patagónica",
        "perfil_ladera": [0, 200, 600, 1400, 1400, 600, 200, 0],
        "x_perfil": [0, 1, 3, 8, 17, 22, 24, 25],  # km desde salida
        "ancho_valle_km": 5.0,
        "topo_valle": 10,         # elev. base del valle (m.s.n.m.)
        "espesor_q": 15,          # espesor medio cuaternario (m)
        "espesor_q_centro": 25,   # espesor máximo en eje
        "prof_nf": 4,             # prof. nivel freático (m)
        "litologias": [
            ("Relleno Cuat.\n(Gravas/Arenas glaciofl.)", "#E8D5A3"),
            ("Sustrato - Fm. Loreto\n(Lutitas Eocenas)", "#8B7355"),
        ],
        "unidades_hidrogeo": [
            {"nombre": "UH Cuaternaria (Acuífero libre)", "color": "#A8C8E8",
             "permeab": "Alta (10-50 m/d)", "espesor": "5-25 m"},
            {"nombre": "UH Sustrato Sedim. (Acuitardo)",
             "color": "#C8B89A", "permeab": "Baja (<0.1 m/d)", "espesor": ">200 m"},
        ],
        "zona_recarga": "Sector cordillerano y laderas\n(infiltración directa PP)",
        "zona_descarga": "Río Penitente (base flow)\ny SHAC Penitente",
        "flujo_dir": "E → O (hacia Estrecho Magallanes)",
        "PP_recarga": 10,     # mm/año de recarga
        "hay_glaciar": False,
        "notas_especiales": "Cuenca semi-árida: recarga muy limitada (~8% PP)\nDemanda ganadera predominante",
    },
    "El Oro": {
        "titulo": "Cuenca del Río El Oro",
        "tipo_cuenca": "Valle Cordillerano — Tierra del Fuego",
        "perfil_ladera": [0, 100, 400, 800, 800, 400, 100, 0],
        "x_perfil": [0, 1, 2, 5, 20, 23, 24, 25],
        "ancho_valle_km": 3.0,
        "topo_valle": 20,
        "espesor_q": 18,
        "espesor_q_centro": 30,
        "prof_nf": 2,
        "litologias": [
            ("Relleno Cuat.\n(Gravas/Til glaciofl. TF)", "#E8D5A3"),
            ("Fm. Latorre/Tobífera\n(Roca metamórfica/volcánica)", "#9B8EA0"),
        ],
        "unidades_hidrogeo": [
            {"nombre": "UH Cuaternaria (Acuífero libre)", "color": "#A8C8E8",
             "permeab": "Alta (8-80 m/d)", "espesor": "5-30 m"},
            {"nombre": "UH Sustrato Metamórfico (Acuifugo)",
             "color": "#B0A0B8", "permeab": "Muy baja (<0.01 m/d)", "espesor": ">500 m"},
        ],
        "zona_recarga": "Laderas boscosas + porción\nglacial remanente (N de cuenca)",
        "zona_descarga": "Río El Oro (base flow significativo)\ny SHAC Río Oro (Bahía San Felipe)",
        "flujo_dir": "N → S (hacia Bahía San Felipe)",
        "PP_recarga": 108,
        "hay_glaciar": True,
        "notas_especiales": "PP alta (900 mm/año): recarga significativa (~12%)\nPresencia glaciar remanente en cotas > 600 m",
    },
    "Robalo": {
        "titulo": "Cuenca del Río Róbalo",
        "tipo_cuenca": "Cuenca Torrencial de Montaña — Isla Navarino",
        "perfil_ladera": [50, 150, 300, 510, 510, 300, 150, 50],
        "x_perfil": [0, 0.5, 1.5, 2.5, 3, 4, 4.5, 5],
        "ancho_valle_km": 1.5,
        "topo_valle": 50,
        "espesor_q": 2,
        "espesor_q_centro": 5,
        "prof_nf": 0.5,
        "litologias": [
            ("Regolito/Till delgado\n(< 5 m espesor)", "#DDD0B8"),
            ("Batolito Hornos-Moreno\n(Granito/Granodiorita Paleozoico)", "#967B8A"),
        ],
        "unidades_hidrogeo": [
            {"nombre": "UH Roca Fisurada (Acuífero limitado)", "color": "#C8B8D0",
             "permeab": "Muy baja (0.1-5 m/d)", "espesor": "variable (fisuras)"},
            {"nombre": "UH Granito Masivo (Acuifugo)",
             "color": "#8B7090", "permeab": "Prácticamente nula", "espesor": ">1000 m"},
        ],
        "zona_recarga": "Toda la cuenca (lluvia directa\ne infiltración en fracturas)",
        "zona_descarga": "Río Róbalo → Abastecimiento\nAgua Potable Puerto Williams",
        "flujo_dir": "NO → SE (hacia Canal Beagle)",
        "PP_recarga": 35,
        "hay_glaciar": False,
        "notas_especiales": "Cuenca crítica: único SSPP de Puerto Williams\nAcuífero muy limitado: dominancia de escorrentía directa\nPendiente media 38% → tiempo respuesta muy rápido",
    },
}

# -------------------------------------------------------------------
# CARGA DE DATOS REALES (DEM + BOT + PERFIL LONGITUDINAL)
# -------------------------------------------------------------------

def _cargar_datos_reales(nombre_cuenca):
    """
    Carga DEM Copernicus real + base acuífero (BOT shapefile) para una cuenca.
    Retorna dict con grids 2D y perfil longitudinal, o None si no disponible.
    """
    if not _HAS_GEO:
        return None
    rcfg = CUENCAS_REAL_CFG.get(nombre_cuenca)
    if not rcfg:
        return None
    try:
        gdf_basin = gpd.read_file(BASIN_SHP_02)
        sel = gdf_basin.loc[gdf_basin["NOMBRE"] == rcfg["basin_nombre"], "geometry"]
        if sel.empty:
            return None
        poly = sel.iloc[0]
    except Exception:
        return None

    xmin, ymin, xmax, ymax = poly.bounds
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2

    # ── DEM Copernicus ─────────────────────────────────────────────
    cop_path = resolve_input(os.path.join("02 PyScripts Magallanes", "DEM_Copernicus_30m", "mosaicos", rcfg["dem_cop"]))
    if not os.path.exists(cop_path):
        return None
    try:
        with rasterio.open(cop_path) as src:
            out_img, _ = rio_mask(src, [poly], crop=True, nodata=-9999)
            elev_raw = out_img[0].astype("float32")
            elev_raw[elev_raw == -9999] = np.nan
            elev_raw = np.flipud(elev_raw)
        N = 45
        zf = N / max(elev_raw.shape)
        elev_m = ndimage_zoom(elev_raw, zf, order=1, prefilter=False)
        wt = ndimage_zoom((~np.isnan(elev_raw)).astype("float32"), zf, order=0)
        elev_m[wt < 0.5] = np.nan
    except Exception:
        return None

    nr, nc = elev_m.shape
    xi = np.linspace(xmin, xmax, nc)
    yi = np.linspace(ymin, ymax, nr)
    XX, YY = np.meshgrid(xi, yi)
    XX_km = (XX - cx) / 1000
    YY_km = (YY - cy) / 1000

    # ── Base acuífero (BOT shapefile) ──────────────────────────────
    Z_bot = None
    bot_path = resolve_input(os.path.join("03 SIG Magallanes", rcfg["bot_shp"])) if rcfg.get("bot_shp") else ""
    if bot_path and os.path.exists(bot_path):
        try:
            gdf_bot = gpd.read_file(bot_path)
            buf = rcfg.get("bot_buffer", 0)
            clip_poly = poly.buffer(buf) if buf else poly
            gdf_clip = gdf_bot[gdf_bot.geometry.intersects(clip_poly)]
            if len(gdf_clip) > 0:
                pts_x = np.array([g.x for g in gdf_clip.geometry])
                pts_y = np.array([g.y for g in gdf_clip.geometry])
                pts_z = gdf_clip["Bottom1"].values.astype("float64")
                pts_xy = np.column_stack([pts_x, pts_y])
                grid_xy = np.column_stack([XX.ravel(), YY.ravel()])
                bot_raw = griddata(pts_xy, pts_z, grid_xy,
                                   method="linear").reshape(nr, nc)
                _sp = float(np.median(np.diff(np.sort(np.unique(pts_x)))))
                _tree = cKDTree(pts_xy)
                _d, _ = _tree.query(grid_xy, k=1, workers=-1)
                bot_raw[_d.reshape(nr, nc) > _sp * 1.5] = np.nan
                # Clip: base no puede superar el terreno
                bot_raw = np.where(
                    ~np.isnan(elev_m) & ~np.isnan(bot_raw),
                    np.minimum(bot_raw, elev_m - 0.5),
                    np.nan,
                )
                Z_bot = bot_raw
        except Exception:
            Z_bot = None

    # ── Perfil longitudinal (cauce principal) ──────────────────────
    lp = None
    river_p = resolve_input(os.path.join("01 Etapa 1", "Anexos", "Anexo E - SIG", "04_Geodatabases", "PERHC", rcfg["river_shp"])) if rcfg.get("river_shp") else ""
    if river_p and os.path.exists(river_p):
        try:
            gdf_r = gpd.read_file(river_p)
            geom = unary_union(gdf_r.geometry)
            if geom.geom_type == "MultiLineString":
                main_line = max(geom.geoms, key=lambda l: l.length)
            elif geom.geom_type == "LineString":
                main_line = geom
            else:
                main_line = None
            if main_line is not None:
                N_p = 80
                pts_r = [main_line.interpolate(t, normalized=True)
                         for t in np.linspace(0, 1, N_p)]
                rrx = np.array([pt.x for pt in pts_r])
                rry = np.array([pt.y for pt in pts_r])
                rgi_z = RegularGridInterpolator(
                    (yi, xi), np.nan_to_num(elev_m, nan=-9999.0),
                    method="linear", bounds_error=False, fill_value=-9999.0,
                )
                lp_z = rgi_z(np.column_stack([rry, rrx]))
                lp_z[lp_z < -999.0] = np.nan
                # Orientar upstream → downstream (elevación decreciente)
                valid_lp = ~np.isnan(lp_z)
                if valid_lp.sum() > 4:
                    first_v = np.where(valid_lp)[0][0]
                    last_v  = np.where(valid_lp)[0][-1]
                    if lp_z[first_v] < lp_z[last_v]:
                        lp_z = lp_z[::-1]; rrx = rrx[::-1]; rry = rry[::-1]
                lp_b = None
                if Z_bot is not None:
                    rgi_b = RegularGridInterpolator(
                        (yi, xi), np.nan_to_num(Z_bot, nan=-9999.0),
                        method="linear", bounds_error=False, fill_value=-9999.0,
                    )
                    lp_b = rgi_b(np.column_stack([rry, rrx]))
                    lp_b[lp_b < -999.0] = np.nan
                dist = np.concatenate(
                    [[0], np.cumsum(np.sqrt(np.diff(rrx)**2 + np.diff(rry)**2))]
                )
                lp = dict(dist_km=dist / 1000, z=lp_z, base=lp_b)
        except Exception:
            lp = None

    return dict(XX_km=XX_km, YY_km=YY_km, Z_topo=elev_m, Z_bot=Z_bot, lp=lp)


def _dibujar_bloque_3d_real(ax, p, c, rd):
    """Bloque 3D usando DEM Copernicus real + base acuífero (BOT shapefile)."""
    XX_km  = rd["XX_km"]
    YY_km  = rd["YY_km"]
    Z_TOPO = rd["Z_topo"]
    Z_BOT  = rd["Z_bot"]    # puede ser None (Róbalo)

    Z_NF = np.where(~np.isnan(Z_TOPO), Z_TOPO - p["prof_nf"], np.nan)
    if Z_BOT is not None:
        Z_NF = np.where(~np.isnan(Z_BOT),
                        np.maximum(Z_NF, Z_BOT + 0.5), Z_NF)

    # Superficies 3D
    ax.plot_surface(XX_km, YY_km, Z_TOPO, color=COLORES["topografia"],
                    alpha=0.55, linewidth=0, antialiased=True)
    ax.plot_surface(XX_km, YY_km, Z_NF, color=COLORES["NF"],
                    alpha=0.28, linewidth=0, antialiased=True)
    if Z_BOT is not None:
        ax.plot_surface(XX_km, YY_km, Z_BOT, color=COLORES["sustrato"],
                        alpha=0.42, linewidth=0, antialiased=True)

    # Sección transversal (fila con mayor cobertura de datos BOT, o mid)
    if Z_BOT is not None:
        mid_i = int(np.argmax((~np.isnan(Z_BOT)).sum(axis=1)))
    else:
        mid_i = Z_TOPO.shape[0] // 2

    xs_x  = XX_km[mid_i, :]
    xs_y0 = np.full_like(xs_x, YY_km[mid_i, 0])
    xs_t  = Z_TOPO[mid_i, :]
    xs_n  = Z_NF[mid_i, :]
    xs_b  = (Z_BOT[mid_i, :] if Z_BOT is not None
             else xs_t - p["espesor_q_centro"])
    xs_b  = np.minimum(xs_b, xs_n - 0.5)
    mask  = ~(np.isnan(xs_t) | np.isnan(xs_n) | np.isnan(xs_b))
    if mask.sum() > 4:
        xx_, yt_, yn_, yb_, yf_ = (
            xs_x[mask], xs_t[mask], xs_n[mask], xs_b[mask], xs_y0[mask])
        v_ns  = list(zip(xx_, yf_, yt_)) + list(zip(xx_[::-1], yf_[::-1], yn_[::-1]))
        v_sat = list(zip(xx_, yf_, yn_)) + list(zip(xx_[::-1], yf_[::-1], yb_[::-1]))
        ax.add_collection3d(Poly3DCollection(
            [v_ns], alpha=0.60,
            facecolor=COLORES["cuaternario"], edgecolor="#A09070", linewidth=0.5))
        ax.add_collection3d(Poly3DCollection(
            [v_sat], alpha=0.72,
            facecolor=COLORES["acuifero_sat"], edgecolor="#4A90D9", linewidth=0.7))

    # Cauce principal (mínimo de elevación por fila — omitir filas todo-NaN)
    n_rows = Z_TOPO.shape[0]
    valley_col = np.full(n_rows, -1, dtype=int)
    for _i in range(n_rows):
        _row = Z_TOPO[_i, :]
        if not np.all(np.isnan(_row)):
            valley_col[_i] = int(np.nanargmin(_row))
    vmask_r = valley_col >= 0
    yy_rows = YY_km[:, 0]
    xx_riv  = np.where(vmask_r,
                       XX_km[np.arange(n_rows),
                             np.clip(valley_col, 0, Z_TOPO.shape[1]-1)],
                       np.nan)
    zz_riv  = np.where(vmask_r,
                       Z_TOPO[np.arange(n_rows),
                              np.clip(valley_col, 0, Z_TOPO.shape[1]-1)] - 1,
                       np.nan)
    vmask   = vmask_r & ~np.isnan(zz_riv)
    ax.plot(xx_riv[vmask], yy_rows[vmask], zz_riv[vmask],
            color=COLORES["rio"], linewidth=2.5, zorder=5)

    # Flechas recarga / descarga
    z_max   = float(np.nanmax(Z_TOPO))
    cx_km   = float(np.nanmean(XX_km[~np.isnan(Z_TOPO)]))
    cy_km   = float(np.nanmean(YY_km[~np.isnan(Z_TOPO)]))
    dx_span = float(np.nanmax(XX_km) - np.nanmin(XX_km))
    for dxi in (-0.3, 0.0, 0.3):
        ax.quiver(cx_km + dxi * dx_span * 0.25, cy_km, z_max + 30,
                  0, 0, -22, color=COLORES["recarga"],
                  linewidth=1.5, arrow_length_ratio=0.35, normalize=True)
    if vmask.sum() > 0:
        n_mid = int(vmask.sum() // 2)
        ax.quiver(xx_riv[vmask][n_mid] + dx_span * 0.08,
                  yy_rows[vmask][n_mid],
                  zz_riv[vmask][n_mid] + 5,
                  -dx_span * 0.06, 0, -4,
                  color=COLORES["descarga"], linewidth=2.0,
                  arrow_length_ratio=0.4, normalize=True)

    ax.text(cx_km, cy_km, z_max + 55,
            "Nivel freático est.", fontsize=7, color=DGA_BLUE,
            ha="center", fontweight="bold")

    leyenda = [
        mpatches.Patch(color=COLORES["topografia"], alpha=0.55,
                       label="Terreno (DEM Copernicus 30m)"),
        mpatches.Patch(color=COLORES["cuaternario"], alpha=0.60,
                       label="Relleno cuaternario (zona no sat.)"),
        mpatches.Patch(color=COLORES["acuifero_sat"], alpha=0.72,
                       label="Zona saturada (acuífero libre)"),
        mpatches.Patch(color=COLORES["sustrato"], alpha=0.42,
                       label=p["litologias"][1][0].replace("\n", " ")),
        mpatches.Patch(color=COLORES["NF"], alpha=0.5,
                       label="Nivel freático estimado"),
        mpatches.Patch(color=COLORES["rio"], label="Cauce principal"),
        mpatches.Patch(color=COLORES["recarga"], label="Recarga (infiltración PP)"),
        mpatches.Patch(color=COLORES["descarga"], label="Descarga/Baseflow"),
    ]
    ax.legend(handles=leyenda, loc="upper left", fontsize=6.5,
              ncol=2, framealpha=0.85, edgecolor=DGA_BLUE)

    x_span = float(np.nanmax(XX_km) - np.nanmin(XX_km))
    y_span = float(np.nanmax(YY_km) - np.nanmin(YY_km))
    ax.set_xlabel(f"Δ Este (km)  [span {x_span:.0f} km]", fontsize=8, labelpad=5)
    ax.set_ylabel(f"Δ Norte (km)  [span {y_span:.0f} km]", fontsize=8, labelpad=5)
    ax.set_zlabel("Elevación (m.s.n.m.)", fontsize=8, labelpad=5)
    ax.set_title(
        f"Vista 3D — DEM Copernicus 30m + Base Acuífero Real\n"
        f"Flujo subterráneo: {p['flujo_dir']}",
        fontsize=9, pad=8, color=DGA_BLUE,
    )
    ax.view_init(elev=25, azim=-55)
    ax.tick_params(labelsize=7)


def _dibujar_perfil_real(ax, p, c, lp):
    """Perfil longitudinal basado en DEM Copernicus 30m + base acuífero real."""
    dist_km = lp["dist_km"]
    z_topo  = lp["z"]
    z_base  = lp["base"]      # puede ser None

    valid_t = ~np.isnan(z_topo)
    if valid_t.sum() < 5:
        return False          # señal para usar fallback sintético

    # Rellenar pequeños huecos NaN en topografía
    z_tp = np.where(valid_t, z_topo,
                    np.interp(dist_km, dist_km[valid_t], z_topo[valid_t]))
    L        = dist_km[-1]
    z_nf     = z_tp - p["prof_nf"]
    z_sub_bot = np.nanmin(z_tp) - max(p["espesor_q_centro"] * 1.5, 30)

    if z_base is not None:
        valid_b = ~np.isnan(z_base)
        if valid_b.sum() > 3:
            z_bp = np.where(valid_b,
                            np.minimum(z_base, z_tp - 0.5), np.nan)
            z_nf_sat = np.where(valid_b,
                                np.maximum(z_nf, z_bp + 0.2), z_nf)
            # Relleno cuaternario (terreno → NF)
            ax.fill_between(dist_km, z_nf_sat, z_tp,
                            where=valid_b & valid_t,
                            color=COLORES["cuaternario"], alpha=0.70,
                            label=p["litologias"][0][0].replace("\n", " "),
                            zorder=2)
            # Zona saturada (NF → base)
            ax.fill_between(dist_km, z_bp, z_nf_sat,
                            where=valid_b & valid_t,
                            color=COLORES["acuifero_sat"], alpha=0.65,
                            label="Zona saturada (acuífero lib.)", zorder=3)
            # Sustrato (debajo de la base)
            ax.fill_between(dist_km, z_sub_bot, z_bp,
                            where=valid_b,
                            color=COLORES["sustrato"], alpha=0.50,
                            label=p["litologias"][1][0].replace("\n", " "),
                            zorder=2)
            # Línea de base real
            ax.plot(dist_km[valid_b], z_bp[valid_b],
                    color="#5D4037", linewidth=1.8, linestyle="--",
                    label="Base acuífero (PEGH)", zorder=6)
        else:
            z_base = None   # insuficiente → fallback esquemático

    if z_base is None:
        z_bp_sch = z_tp - p["espesor_q"]
        ax.fill_between(dist_km, z_bp_sch, z_tp,
                        color=COLORES["cuaternario"], alpha=0.70,
                        label=p["litologias"][0][0].replace("\n", " "), zorder=2)
        ax.fill_between(dist_km, z_nf, z_tp,
                        color=COLORES["acuifero_sat"], alpha=0.65,
                        label="Zona saturada (acuífero lib.)", zorder=3)
        ax.fill_between(dist_km, z_sub_bot, z_bp_sch,
                        color=COLORES["sustrato"], alpha=0.50,
                        label=p["litologias"][1][0].replace("\n", " "), zorder=2)

    # Topografía
    ax.plot(dist_km, z_tp, color="#3D5A2E", linewidth=2,
            label="Topografía (DEM Cop. 30m)", zorder=5)
    ax.fill_between(dist_km, z_tp, float(np.nanmax(z_tp)) * 1.05,
                    color=COLORES["topografia"], alpha=0.15, zorder=1)
    ax.plot(dist_km, z_nf, color=COLORES["NF"], linewidth=2,
            linestyle="--", label="Nivel freático (NF est.)", zorder=6)

    # Glaciar (Río El Oro únicamente)
    if p.get("hay_glaciar", False):
        i_gl = int(np.nanargmax(z_tp))
        sl = slice(max(0, i_gl - 1), min(len(dist_km), i_gl + 3))
        ax.fill_between(dist_km[sl], z_tp[sl], z_tp[sl] + 25,
                        color=COLORES["glaciar"], alpha=0.80,
                        label="Glaciar remanente", zorder=7,
                        edgecolor="#99BBDD", linewidth=0.5)

    # Cauce principal
    i_rio = int(np.nanargmin(z_tp))
    ax.annotate("", xy=(dist_km[i_rio], z_tp[i_rio] - 1),
                xytext=(dist_km[i_rio], z_tp[i_rio] - 5),
                arrowprops=dict(arrowstyle="->", color=COLORES["rio"], lw=1.5))
    ax.text(dist_km[i_rio], z_tp[i_rio] - 7,
            "Cauce\nprincipal", ha="center", va="top", fontsize=7,
            color=COLORES["rio"], fontweight="bold")

    # Flechas de flujo subterráneo
    for xi_a, zi_a in zip(dist_km[2::12], z_nf[2::12]):
        ax.annotate("", xy=(xi_a + L * 0.05, zi_a),
                    xytext=(xi_a, zi_a),
                    arrowprops=dict(arrowstyle="->", color="#2E86AB",
                                    lw=1, connectionstyle="arc3,rad=-0.1"))

    # Zonas recarga / descarga
    i_rec = int(np.nanargmax(z_tp))
    ax.axvspan(dist_km[max(0, i_rec - 1)],
               dist_km[min(len(dist_km) - 1, i_rec + 2)],
               alpha=0.12, color=COLORES["recarga"], label="Zona recarga")
    ax.axvspan(0, L * 0.10, alpha=0.12, color=COLORES["descarga"],
               label="Zona descarga")
    y_top = float(np.nanmax(z_tp))
    ax.text(dist_km[i_rec],
            y_top + abs(y_top) * 0.015 if y_top != 0 else y_top + 10,
            f"⬇ RECARGA\n{p['zona_recarga']}",
            fontsize=6.5, ha="center", va="bottom", color=COLORES["recarga"],
            fontweight="bold",
            bbox=dict(fc="white", ec=COLORES["recarga"], alpha=0.8,
                      boxstyle="round,pad=0.2"))
    ax.text(L * 0.04, y_top * 0.72 if y_top > 0 else y_top - abs(y_top) * 0.25,
            f"↑ DESCARGA\n{p['zona_descarga']}",
            fontsize=6.5, ha="left", va="center", color=COLORES["descarga"],
            bbox=dict(fc="white", ec=COLORES["descarga"], alpha=0.8,
                      boxstyle="round,pad=0.2"))

    ax.set_xlabel("Distancia a lo largo del cauce principal (km)", fontsize=9)
    ax.set_ylabel("Elevación (m.s.n.m.)", fontsize=9)
    ax.set_title(
        f"Perfil Longitudinal Real (DEM Cop. 30m) — Unidades Hidrogeológicas\n"
        f"Recarga estimada: {c['recarga_mm_anual']} mm/año  |  "
        f"Prof. NF: {c['profundidad_NBF_m'][0]}–{c['profundidad_NBF_m'][1]} m",
        fontsize=9, color=DGA_BLUE,
    )
    ax.legend(loc="upper right", fontsize=7, ncol=2,
              framealpha=0.9, edgecolor=DGA_BLUE)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.xaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_xlim(-L * 0.02, L * 1.02)
    return True


# -------------------------------------------------------------------
# FUNCIÓN PRINCIPAL: DIAGRAMA CONCEPTUAL SUBTERRÁNEO POR CUENCA
# -------------------------------------------------------------------

def generar_modelo_subterraneo(nombre_cuenca: str, datos_cuenca: dict,
                                params_geol: dict) -> str:
    """
    Genera figura completa: sección transversal 3D + perfil longitudinal +
    tabla parámetros + diagrama de balance subterráneo.
    """
    fig = plt.figure(figsize=(20, 14), dpi=150)
    fig.patch.set_facecolor("white")

    # Layout: 2 filas, 3 columnas
    gs = gridspec.GridSpec(2, 3, figure=fig,
                           height_ratios=[1.4, 1],
                           hspace=0.35, wspace=0.3,
                           left=0.05, right=0.97,
                           top=0.90, bottom=0.05)

    ax_3d = fig.add_subplot(gs[0, :2], projection="3d")
    ax_tabla = fig.add_subplot(gs[0, 2])
    ax_perfil = fig.add_subplot(gs[1, :2])
    ax_balance = fig.add_subplot(gs[1, 2])

    p = params_geol
    c = datos_cuenca
    real_data = _cargar_datos_reales(nombre_cuenca)

    # ── PANEL 1: BLOQUE 3D ──────────────────────────────────────────
    _dibujar_bloque_3d(ax_3d, p, c, real_data=real_data)

    # ── PANEL 2: TABLA DE PARÁMETROS ─────────────────────────────────
    _dibujar_tabla_parametros(ax_tabla, p, c)

    # ── PANEL 3: PERFIL LONGITUDINAL (2D) ──────────────────────────
    _dibujar_perfil_longitudinal(ax_perfil, p, c, real_data=real_data)

    # ── PANEL 4: DIAGRAMA BALANCE SUBTERRÁNEO ───────────────────────
    _dibujar_balance_subterraneo(ax_balance, p, c)

    # ── CABECERA ───────────────────────────────────────────────────
    fig.suptitle(
        f"MODELO CONCEPTUAL SUBTERRÁNEO PRELIMINAR\n{p['titulo'].upper()}",
        fontsize=13, fontweight="bold", color=DGA_BLUE, y=0.97,
        bbox=dict(boxstyle="round,pad=0.3", fc="#EEF2F8", ec=DGA_BLUE, lw=1.5)
    )

    # Pie de figura
    pie = (f"Fuente: Elaboración propia — IDIEM/DGA  |  Resolución Obs. DGA N°6  |  "
           f"Software: Python 3 / matplotlib  |  CRS: EPSG:4326  |  "
           f"Fecha: 11-03-2026")
    fig.text(0.5, 0.01, pie, ha="center", va="bottom", fontsize=7,
             color="#555", style="italic")

    # Guardar
    nombre_arch = f"MC_Subterraneo_{nombre_cuenca.replace(' ', '_')}.png"
    ruta = os.path.join(FIG_DIR, nombre_arch)
    fig.savefig(ruta, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"  ✓ Guardado: {nombre_arch}")
    return ruta


def _dibujar_bloque_3d(ax, p, c, real_data=None):
    """Bloque 3D del sistema acuífero con sección transversal."""
    ax.set_facecolor("#F0F4F8")
    if real_data is not None:
        _dibujar_bloque_3d_real(ax, p, c, real_data)
        return

    ancho = p["ancho_valle_km"]
    largo = 6.0    # largo del bloque (km)
    alto  = p["espesor_q_centro"] + 20  # altura total (m escalada)

    # Dimensiones del bloque
    dx = np.linspace(-ancho/2, ancho/2, 30)
    dy = np.linspace(0, largo, 30)
    X, Y = np.meshgrid(dx, dy)

    # Topografía: perfil transversal tipo valle (paraboloide)
    topo_val = p["topo_valle"]
    h_ladera = min(p["perfil_ladera"][3], 250)  # limitar para visualización
    Z_topo = topo_val + h_ladera * (dx / (ancho/2))**2
    Z_TOPO = np.tile(Z_topo, (30, 1))

    # Base del cuaternario: parabólica
    espesor_centro = p["espesor_q_centro"]
    Z_base_q = topo_val - espesor_centro * (1 - (dx / (ancho/2))**2)
    Z_BASE_Q = np.tile(Z_base_q, (30, 1))

    # Nivel freático (NF): paralelo a topografía pero bajado prof_nf
    prof_nf = p["prof_nf"]
    Z_NF = Z_TOPO - prof_nf

    # Superficie topográfica
    ax.plot_surface(X, Y, Z_TOPO, color=COLORES["topografia"],
                    alpha=0.6, linewidth=0, antialiased=True, label="Topografía")

    # Superficie del nivel freático (zona saturada)
    ax.plot_surface(X, Y, Z_NF, color=COLORES["NF"],
                    alpha=0.35, linewidth=0.3, antialiased=True)

    # Base del cuaternario (sustrato)
    ax.plot_surface(X, Y, Z_BASE_Q, color=COLORES["sustrato"],
                    alpha=0.5, linewidth=0, antialiased=True)

    # Sección transversal del frente (cara Y=0)
    x_sc = np.linspace(-ancho/2, ancho/2, 60)
    z_topo_sc = topo_val + h_ladera * (x_sc / (ancho/2))**2
    z_nf_sc   = z_topo_sc - prof_nf
    z_base_sc = topo_val - espesor_centro * (1 - (x_sc / (ancho/2))**2)
    y_sc0     = np.zeros_like(x_sc)

    # Polígono zona no saturada
    verts_ns = list(zip(x_sc, y_sc0, z_topo_sc)) + \
               list(zip(x_sc[::-1], y_sc0[::-1], z_nf_sc[::-1]))
    poly_ns = Poly3DCollection([verts_ns], alpha=0.55,
                               facecolor=COLORES["cuaternario"],
                               edgecolor="#A09070", linewidth=0.5)
    ax.add_collection3d(poly_ns)

    # Polígono zona saturada
    verts_sat = list(zip(x_sc, y_sc0, z_nf_sc)) + \
                list(zip(x_sc[::-1], y_sc0[::-1], z_base_sc[::-1]))
    poly_sat = Poly3DCollection([verts_sat], alpha=0.65,
                                facecolor=COLORES["acuifero_sat"],
                                edgecolor="#4A90D9", linewidth=0.7)
    ax.add_collection3d(poly_sat)

    # Río en el fondo del valle (eje)
    y_rio = np.linspace(0, largo, 50)
    x_rio = np.zeros(50)
    z_rio = np.full(50, topo_val - prof_nf * 0.5)  # ligeramente bajo NF
    ax.plot(x_rio, y_rio, z_rio, color=COLORES["rio"],
            linewidth=2.5, zorder=5, label="Cauce principal")

    # Flechas de recarga (lluvia infiltrando)
    for xi in [-ancho*0.3, 0, ancho*0.3]:
        zi_top = topo_val + h_ladera * (xi/(ancho/2))**2
        zi_bot = zi_top - prof_nf + 2
        ax.quiver(xi, largo*0.5, zi_top + 8, 0, 0, -8,
                  color=COLORES["recarga"], linewidth=1.5,
                  arrow_length_ratio=0.35, normalize=True)

    # Flechas de flujo subterráneo
    for yi in [1.0, 2.5, 4.5]:
        ax.quiver(-ancho*0.2, yi, topo_val - espesor_centro*0.5,
                  ancho*0.15, 0.8, 0,
                  color=COLORES["NF"], linewidth=1.2,
                  arrow_length_ratio=0.3, normalize=True)

    # Flecha de descarga al río
    ax.quiver(-0.5, largo*0.5, topo_val - prof_nf,
              0.5, 0, -1,
              color=COLORES["descarga"], linewidth=2,
              arrow_length_ratio=0.4, normalize=True)

    # Anotaciones
    ax.text(ancho/2 + 0.3, largo*0.1, topo_val + h_ladera*0.8,
            p["litologias"][0][0], fontsize=7, color="#5D4037",
            ha="left", va="center")
    ax.text(-ancho/2 - 0.3, largo*0.8, topo_val - espesor_centro*0.7,
            p["litologias"][1][0], fontsize=7, color="#4A3728",
            ha="right", va="center")

    ax.text(0, largo * 0.85, topo_val - prof_nf + 1,
            "Nivel\nFreático", fontsize=7, color=DGA_BLUE,
            ha="center", fontweight="bold")

    # Leyenda manual
    leyenda = [
        mpatches.Patch(color=COLORES["topografia"], alpha=0.6, label="Topografía / Suelo"),
        mpatches.Patch(color=COLORES["cuaternario"], alpha=0.55, label="Relleno cuaternario (zona no sat.)"),
        mpatches.Patch(color=COLORES["acuifero_sat"], alpha=0.65, label="Zona saturada (acuífero libre)"),
        mpatches.Patch(color=COLORES["sustrato"], alpha=0.5, label=p["litologias"][1][0].replace("\n", " ")),
        mpatches.Patch(color=COLORES["rio"], label="Cauce principal"),
        mpatches.Patch(color=COLORES["recarga"], label="Recarga (infiltración PP)"),
        mpatches.Patch(color=COLORES["descarga"], label="Descarga/Baseflow"),
    ]
    ax.legend(handles=leyenda, loc="upper left", fontsize=6.5,
              ncol=2, framealpha=0.85, edgecolor=DGA_BLUE)

    ax.set_xlabel("Ancho transversal (km)", fontsize=8, labelpad=5)
    ax.set_ylabel("Dirección de flujo (km)", fontsize=8, labelpad=5)
    ax.set_zlabel("Elevación (m.s.n.m.)", fontsize=8, labelpad=5)
    ax.set_title(
        f"Vista 3D — {p['tipo_cuenca']}\nFlujo subterráneo: {p['flujo_dir']}",
        fontsize=9, pad=8, color=DGA_BLUE
    )
    ax.view_init(elev=25, azim=-55)
    ax.tick_params(labelsize=7)


def _dibujar_tabla_parametros(ax, p, c):
    """Panel con tabla de parámetros hidrogeológicos locales."""
    ax.axis("off")

    bh = c["balance_hidrico_mm"]

    rows = [
        ["PARÁMETRO", "VALOR", "FUENTE"],
        ["─" * 15, "─" * 12, "─" * 12],
        ["Área cuenca", f"{c['area_km2']:,.1f} km²", "SIG"],
        ["Elevación media", f"{c['elevacion_media_m']} m.s.n.m.", "DEM"],
        ["Clima (Köppen)", f"{c['koppen']}", "PMETobs"],
        ["PP media anual", f"{c['PP_media_anual_mm']} mm/año", "PMETobs"],
        ["ETR estimada", f"{c['ETR_anual_mm']} mm/año", "Penman-M."],
        ["Q medio anual", f"{c['Q_medio_anual_m3s']} m³/s", "DGA"],
        ["Coef. escorrentía", f"{c['coeficiente_escorrentia']:.2f}", "Calculado"],
        ["─" * 15, "─" * 12, "─" * 12],
        ["SHAC", c["shac"].replace("SHAC ", ""), "DGA"],
        ["Tipo acuífero", c["tipo_acuifero"], "Informe E1"],
        ["Espesor Cuat. (m)", f"{c['espesor_acuifero_m'][0]}–{c['espesor_acuifero_m'][1]}", "PEGH/2021"],
        ["Prof. NF (m)", f"{c['profundidad_NBF_m'][0]}–{c['profundidad_NBF_m'][1]}", "Ref. PEGH"],
        ["K hidráulica (m/d)", f"{c['conductividad_hid_md'][0]}–{c['conductividad_hid_md'][1]}", "PEGH/2021"],
        ["Recarga est.", f"{c['recarga_mm_anual']} mm/año", "Est. propio"],
        ["% recarga/PP", f"{c['recarga_especifica_pct_pp']}%", "Est. propio"],
        ["─" * 15, "─" * 12, "─" * 12],
        ["Dem. total", f"{c['demanda_total_Ls']:.1f} L/s", "DAA/DGA"],
        ["Dem. C. Humano", f"{c['demanda_consumo_humano_Ls']:.1f} L/s", "Informe E1"],
        ["DAA subterráneo", f"{c['DAA_subterraneo_Ls']:.1f} L/s", "DGA"],
    ]

    col_w = [0.5, 0.28, 0.22]
    xs = [0.01, 0.51, 0.79]
    ys = np.linspace(0.99, 0.02, len(rows))

    for i, row in enumerate(rows):
        bold = (i == 0)
        bg = "#EEF2F8" if i == 0 else ("white" if i % 2 == 0 else "#F7F9FC")
        if row[0].startswith("─"):
            ax.axhline(y=ys[i], xmin=0.01, xmax=0.99,
                       color="#AABBCC", linewidth=0.5)
            continue
        ax.add_patch(FancyBboxPatch((0.01, ys[i] - 0.02), 0.97, 0.03,
                                    boxstyle="round,pad=0.002",
                                    facecolor=bg, edgecolor="none", zorder=0))
        for j, (col, text) in enumerate(zip(xs, row)):
            ax.text(col, ys[i], text, ha="left", va="center",
                    fontsize=7.5 if not bold else 8,
                    fontweight="bold" if bold else "normal",
                    color=DGA_BLUE if bold else "#222",
                    transform=ax.transAxes)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Parámetros Hidrogeológicos Locales", fontsize=9,
                 fontweight="bold", color=DGA_BLUE, pad=6)

    # Cuadros de texto notas especiales
    notas = p.get("notas_especiales", "")
    if notas:
        ax.text(0.01, 0.01, f"Nota: {notas}",
                fontsize=6.5, color="#555", style="italic",
                va="bottom", transform=ax.transAxes,
                wrap=True, bbox=dict(fc="#FFFBEA", ec="#CCBB00",
                                     boxstyle="round,pad=0.3", alpha=0.9))


def _dibujar_perfil_longitudinal(ax, p, c, real_data=None):
    """Perfil longitudinal geológico 2D con unidades hidrogeológicas."""
    if real_data is not None and real_data.get("lp") is not None:
        if _dibujar_perfil_real(ax, p, c, real_data["lp"]):
            return

    x = np.array(p["x_perfil"])
    topografia = np.array(p["perfil_ladera"])
    topo_val = p["topo_valle"]
    espesor_q = p["espesor_q"]
    espesor_ch = p["espesor_q_centro"]
    prof_nf = p["prof_nf"]

    # Normalizar x a km
    L_total = c.get("longitud_cauce_principal_km", 25)
    x_km = x / x.max() * L_total

    # Índice del valle (mínimo de topografía → zona de relleno)
    i_min = np.argmin(topografia[1:-1]) + 1

    # Base cuaternario (depresión en el centro del valle)
    base_q = np.copy(topografia).astype(float)
    for i in range(len(topografia)):
        dist_centro = abs(i - i_min) / len(topografia) * 2
        base_q[i] = topografia[i] - espesor_ch * np.exp(-dist_centro**2 * 3)
        base_q[i] = max(base_q[i], topo_val - espesor_ch - 5)

    # Nivel freático
    nf = topografia - prof_nf * 1.2
    nf = np.maximum(nf, base_q + 0.5)

    # Relleno cuaternario
    ax.fill_between(x_km, base_q, topografia,
                    color=COLORES["cuaternario"], alpha=0.7,
                    label=p["litologias"][0][0].replace("\n", " "),
                    zorder=2)

    # Zona saturada
    ax.fill_between(x_km, base_q, nf,
                    color=COLORES["acuifero_sat"], alpha=0.65,
                    label="Zona saturada (acuífero lib.)", zorder=3)

    # Sustrato
    ax.fill_between(x_km, base_q.min() - 30, base_q,
                    color=COLORES["sustrato"], alpha=0.55,
                    label=p["litologias"][1][0].replace("\n", " "),
                    zorder=2)

    # Topografía
    ax.plot(x_km, topografia, color="#3D5A2E", linewidth=2,
            label="Superficie topográfica", zorder=5)
    ax.fill_between(x_km, topografia, topografia.max()*1.05,
                    color=COLORES["topografia"], alpha=0.15, zorder=1)

    # Nivel freático
    ax.plot(x_km, nf, color=COLORES["NF"], linewidth=2,
            linestyle="--", label="Nivel freático (NF)", zorder=6)

    # Glaciar (Río El Oro)
    if p.get("hay_glaciar", False):
        i_gl = np.argmax(topografia)
        x_gl = x_km[max(0, i_gl-1):min(len(x_km), i_gl+2)]
        t_gl = topografia[max(0, i_gl-1):min(len(topografia), i_gl+2)]
        ax.fill_between(x_gl, t_gl, t_gl + 25,
                        color=COLORES["glaciar"], alpha=0.8,
                        label="Glaciar remanente", zorder=7,
                        edgecolor="#99BBDD", linewidth=0.5)

    # Río en superficie
    i_rio = np.argmin(topografia)
    ax.annotate("", xy=(x_km[i_rio], topografia[i_rio] - 1),
                xytext=(x_km[i_rio], topografia[i_rio] - 4),
                arrowprops=dict(arrowstyle="->", color=COLORES["rio"], lw=1.5))
    ax.text(x_km[i_rio], topografia[i_rio] - 6,
            "Cauce\nprincipal", ha="center", va="top", fontsize=7,
            color=COLORES["rio"], fontweight="bold")

    # Flechas de flujo subterráneo
    for xi, bi, ni in zip(x_km[1::3], base_q[1::3], nf[1::3]):
        zm = (bi + ni) / 2
        ax.annotate("", xy=(xi + L_total*0.06, zm),
                    xytext=(xi, zm),
                    arrowprops=dict(arrowstyle="->", color="#2E86AB",
                                    lw=1, connectionstyle="arc3,rad=-0.1"))

    # Zonas de recarga y descarga
    i_rec = np.argmax(topografia)
    ax.axvspan(x_km[max(0,i_rec-1)], x_km[min(len(x_km)-1,i_rec+1)],
               alpha=0.12, color=COLORES["recarga"], label="Zona recarga")
    ax.axvspan(x_km[0]-L_total*0.02, x_km[0]+L_total*0.08,
               alpha=0.12, color=COLORES["descarga"], label="Zona descarga")

    # Anotaciones zonas
    y_max = topografia.max()
    ax.text(x_km[i_rec], y_max * 1.02, f"⬇ RECARGA\n{p['zona_recarga']}",
            fontsize=6.5, ha="center", va="bottom", color=COLORES["recarga"],
            fontweight="bold",
            bbox=dict(fc="white", ec=COLORES["recarga"], alpha=0.8,
                      boxstyle="round,pad=0.2"))
    ax.text(x_km[0] + L_total*0.03, y_max * 0.7,
            f"↑ DESCARGA\n{p['zona_descarga']}",
            fontsize=6.5, ha="left", va="center", color=COLORES["descarga"],
            bbox=dict(fc="white", ec=COLORES["descarga"], alpha=0.8,
                      boxstyle="round,pad=0.2"))

    ax.set_xlabel("Distancia a lo largo del cauce principal (km)", fontsize=9)
    ax.set_ylabel("Elevación (m.s.n.m.)", fontsize=9)
    ax.set_title(
        f"Perfil Geológico Longitudinal — Unidades Hidrogeológicas\n"
        f"Recarga estimada: {c['recarga_mm_anual']} mm/año  |  "
        f"Prof. NF: {c['profundidad_NBF_m'][0]}–{c['profundidad_NBF_m'][1]} m",
        fontsize=9, color=DGA_BLUE
    )
    ax.legend(loc="upper right", fontsize=7, ncol=2, framealpha=0.9,
              edgecolor=DGA_BLUE)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.xaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_xlim(x_km.min() - L_total*0.02, x_km.max() + L_total*0.02)


def _dibujar_balance_subterraneo(ax, p, c):
    """Diagrama de balance hídrico subterráneo (entradas/salidas)."""
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor("white")

    area = c["area_km2"]
    R_mm = c["recarga_mm_anual"]
    # Convertir mm/año × km² → m³/s
    conv = area * 1e6 / (365.25 * 86400) / 1000  # mm/año → m³/s por km²

    recarga = R_mm * conv
    qbase   = recarga * 0.85   # ~85% de la recarga sale como baseflow
    dalsubs  = recarga * 0.05  # ~5% variación almacenamiento
    qbombeo = c["DAA_subterraneo_Ls"] / 1000  # L/s → m³/s
    qbase = max(qbase - qbombeo * 0.5, 0.001)

    # Caja central: acuífero
    cx, cy = 0.5, 0.45
    box_w, box_h = 0.38, 0.18

    # Fondo azul acuífero
    acq_box = FancyBboxPatch((cx - box_w/2, cy - box_h/2), box_w, box_h,
                              boxstyle="round,pad=0.02",
                              facecolor=COLORES["acuifero_sat"],
                              edgecolor=DGA_BLUE, linewidth=2.0)
    ax.add_patch(acq_box)
    ax.text(cx, cy + 0.02, "ACUÍFERO", ha="center", va="center",
            fontsize=10, fontweight="bold", color=DGA_BLUE)
    ax.text(cx, cy - 0.05,
            f"{c['tipo_acuifero']}\ne={c['espesor_acuifero_m'][0]}–{c['espesor_acuifero_m'][1]} m\n"
            f"K={c['conductividad_hid_md'][0]}–{c['conductividad_hid_md'][1]} m/d",
            ha="center", va="center", fontsize=7.5, color="#1A237E",
            style="italic")

    def flecha_con_label(x0, y0, x1, y1, label, valor, color, lado="up"):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>",
                                    color=color, lw=2,
                                    mutation_scale=18,
                                    connectionstyle="arc3,rad=0"))
        offset = 0.07 if lado == "up" else -0.07
        mx, my = (x0+x1)/2, (y0+y1)/2 + offset
        ax.text(mx, my,
                f"{label}\n{valor:.4f} m³/s\n({valor/conv:.0f} mm/año)",
                ha="center", va="center", fontsize=7.5,
                color=color, fontweight="bold",
                bbox=dict(fc="white", ec=color, alpha=0.9,
                          boxstyle="round,pad=0.15"))

    # ENTRADAS
    # Recarga por PP (desde arriba)
    flecha_con_label(cx, 0.88, cx, cy + box_h/2 + 0.01,
                     "⬇  Recarga PP", recarga, COLORES["recarga"], "up")
    # Recarga lateral (desde izquierda, si cuenca grande)
    if area > 200:
        rec_lat = recarga * 0.12
        flecha_con_label(0.08, cy, cx - box_w/2 - 0.01, cy,
                         "⬅ Rec. lateral", rec_lat, "#27AE60", "up")

    # SALIDAS
    # Baseflow al río (a la derecha)
    flecha_con_label(cx + box_w/2 + 0.01, cy + 0.02,
                     0.93, cy + 0.02,
                     "Baseflow →\n(descarga río)", qbase,
                     COLORES["descarga"], "up")

    # Bombeo / extracciones (hacia abajo)
    if qbombeo > 1e-6:
        flecha_con_label(cx + 0.05, cy - box_h/2 - 0.01,
                         cx + 0.05, 0.12,
                         "⬇ Extracciones\n(bombeo/DAA)", qbombeo,
                         COLORES["bombeo"], "up")

    # Variación almacenamiento
    ax.text(cx - 0.22, cy - 0.23,
            f"ΔAlmacenamiento ≈ {dalsubs:.5f} m³/s\n"
            f"(~{dalsubs/conv:.1f} mm/año)",
            ha="center", va="center", fontsize=7,
            color="#555", style="italic",
            bbox=dict(fc="#FFFFF0", ec="#CCCC00",
                      boxstyle="round,pad=0.2", alpha=0.9))

    # Balance total
    entradas_tot = recarga + (recarga*0.12 if area > 200 else 0)
    salidas_tot  = qbase + qbombeo + dalsubs
    cierre = entradas_tot - salidas_tot
    color_cierre = "#27AE60" if abs(cierre) < entradas_tot*0.05 else "#E74C3C"

    ax.text(0.5, 0.04,
            f"BALANCE: Entradas={entradas_tot:.4f}  Salidas={salidas_tot:.4f}  "
            f"ΔS={cierre:.5f} m³/s",
            ha="center", va="bottom", fontsize=7,
            color=color_cierre, fontweight="bold",
            bbox=dict(fc="white", ec=color_cierre,
                      boxstyle="round,pad=0.2", alpha=0.95))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Balance Hídrico Subterráneo\n(valores indicativos preliminares)",
                 fontsize=9, fontweight="bold", color=DGA_BLUE, pad=6)


# -------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "="*65)
    print("GENERANDO MODELOS CONCEPTUALES SUBTERRÁNEOS POR CUENCA")
    print("Resolución Observación DGA N°6")
    print("="*65)

    mapeo = {
        "Penitente": ("Penitente", "Penitente"),
        "El Oro":    ("El Oro",    "El Oro"),
        "Robalo":    ("Robalo",    "Robalo"),
    }

    rutas_generadas = []
    for key_json, (key_geol, nombre_archivo) in mapeo.items():
        if key_json not in CUENCAS:
            print(f"  ⚠ Cuenca '{key_json}' no encontrada en JSON")
            continue
        if key_geol not in PARAMS_GEOL:
            print(f"  ⚠ Parámetros geológicos de '{key_geol}' no definidos")
            continue
        print(f"\n  Generando: {PARAMS_GEOL[key_geol]['titulo']}...")
        ruta = generar_modelo_subterraneo(nombre_archivo,
                                          CUENCAS[key_json],
                                          PARAMS_GEOL[key_geol])
        rutas_generadas.append(ruta)

    print(f"\n{'='*65}")
    print(f"✓ {len(rutas_generadas)} figuras generadas en:")
    print(f"  {FIG_DIR}")
    print("\nACCIÓN SIGUIENTE: Ejecutar 03_modelo_conceptual_superficial.py")
