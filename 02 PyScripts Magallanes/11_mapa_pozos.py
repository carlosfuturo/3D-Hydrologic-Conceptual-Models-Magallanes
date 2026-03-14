"""
Script 11: Mapa de Pozos por Cuenca (estático + interactivo)
Proyecto: Análisis de Recursos Hídricos - Cuencas Magallanes (IDIEM/DGA)
Propósito: Visualizar la distribución espacial de pozos subterráneos
           sobre las tres cuencas de estudio, con simbología por cuenca,
           profundidad y tipo (surgente / normal / monitoreo).
Salidas:
  - Fig11_Mapa_Pozos_Cuencas.png  : mapa estático de alta resolución
  - mapa_pozos_interactivo.html   : mapa interactivo Folium con popups
Autor: Especialista Senior en Modelación
Fecha: 2026
"""

import os, json, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import folium
from folium.plugins import MarkerCluster
from pyproj import Transformer
from project_paths import BASE_DIR, PY_SCRIPTS_DIR, resolve_input

warnings.filterwarnings("ignore")

# ── RUTAS ─────────────────────────────────────────────────────────────────
SIG_DIR  = os.path.join(BASE_DIR, "01 Etapa 1", "Anexos", "Anexo E - SIG", "04_Geodatabases", "PERHC")
OUT_DIR  = PY_SCRIPTS_DIR
FIG_DIR  = os.path.join(OUT_DIR, "Figuras_Pozos_Acuifero")
os.makedirs(FIG_DIR, exist_ok=True)

POZOS_GEOJSON = resolve_input("02 PyScripts Magallanes/pozos_acuifero.geojson")

# ── PALETA ────────────────────────────────────────────────────────────────
C_CUENCA = {
    "Penitente": {"fill": "#3498DB", "edge": "#1A5276", "hex_folium": "#3498DB"},
    "Oro"      : {"fill": "#E74C3C", "edge": "#7B241C", "hex_folium": "#E74C3C"},
    "Robalo"   : {"fill": "#27AE60", "edge": "#145A32", "hex_folium": "#27AE60"},
}
C_BASIN_FILL = {
    "Penitente": "#AED6F1",
    "Oro"      : "#F5B7B1",
    "Robalo"   : "#A9DFBF",
}

# ── TRANSFORMADOR UTM→LatLon ───────────────────────────────────────────────
T_LL = Transformer.from_crs("EPSG:32719", "EPSG:4326", always_xy=True)

def utm_to_latlon(E, N):
    lon, lat = T_LL.transform(E, N)
    return lat, lon

# ── CARGAR DATOS ──────────────────────────────────────────────────────────
print("Cargando datos ...")

# Cuencas
gdf_pen = gpd.read_file(resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/cuenca_rio_penitente.shp")).to_crs("EPSG:32719")
gdf_oro = gpd.read_file(resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/cuenca_rio_del_oro.shp")).to_crs("EPSG:32719")
gdf_rob = gpd.read_file(resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/cuenca_rio_robalo.shp")).to_crs("EPSG:32719")

# Red hidrográfica
gdf_rh_pen = gpd.read_file(resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/red_hidro_penitente.shp")).to_crs("EPSG:32719")
gdf_rh_oro = gpd.read_file(resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/red_hidro_oro.shp")).to_crs("EPSG:32719")
gdf_rh_rob = gpd.read_file(resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/red_hidro_robalo.shp")).to_crs("EPSG:32719")

# Lagos
gdf_lagos = gpd.read_file(resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/hidro_masas_lacustres.shp")).to_crs("EPSG:32719")

# Pozos
with open(POZOS_GEOJSON, encoding="utf-8") as f:
    gj = json.load(f)

records = []
for feat in gj["features"]:
    p = feat["properties"]
    E, N = feat["geometry"]["coordinates"]
    p["E_wgs84"] = E
    p["N_wgs84"] = N
    records.append(p)
df = pd.DataFrame(records)

# GeoDataFrame de pozos (UTM 32719)
gdf_pozos = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["E_wgs84"], df["N_wgs84"]),
    crs="EPSG:32719"
)

print(f"  {len(gdf_pozos)} pozos cargados")

# ── ═══════════════════════════════════════════════════════════════════════
#    MAPA ESTÁTICO
# ══════════════════════════════════════════════════════════════════════════
print("Generando mapa estático ...")

fig, ax = plt.subplots(figsize=(13, 15), facecolor="#F8F9FA")
ax.set_facecolor("#E8EEF4")  # color mar/fondo

# ── Cuencas ──────────────────────────────────────────────────────────────
for gdf, nombre in [(gdf_pen, "Penitente"), (gdf_oro, "Oro"), (gdf_rob, "Robalo")]:
    gdf.plot(ax=ax, facecolor=C_BASIN_FILL[nombre], edgecolor=C_CUENCA[nombre]["edge"],
             linewidth=1.2, alpha=0.55, zorder=1)

# ── Lagos ─────────────────────────────────────────────────────────────────
gdf_lagos.plot(ax=ax, facecolor="#85C1E9", edgecolor="#2980B9",
               linewidth=0.5, alpha=0.7, zorder=2)

# ── Red hidrográfica ──────────────────────────────────────────────────────
for gdf_rh, nombre in [(gdf_rh_pen, "Penitente"), (gdf_rh_oro, "Oro"), (gdf_rh_rob, "Robalo")]:
    gdf_rh.plot(ax=ax, color=C_CUENCA[nombre]["fill"],
                linewidth=0.6, alpha=0.7, zorder=3)

# ── Pozos — por tipo y cuenca ─────────────────────────────────────────────
def get_marker_size(prof):
    """Tamaño del marcador proporcional a la profundidad."""
    if pd.isna(prof):
        return 35
    return max(30, min(200, float(prof) * 1.4))

# Separar subconjuntos
df_monitor = gdf_pozos[gdf_pozos["codigo"] == "INVERNADA-MON"]
df_surg    = gdf_pozos[(gdf_pozos["surgente"] == True) & (gdf_pozos["codigo"] != "INVERNADA-MON")]
df_normal  = gdf_pozos[(gdf_pozos["surgente"] != True) & (gdf_pozos["codigo"] != "INVERNADA-MON")]

# Pozos normales (color por cuenca, tamaño por profundidad)
for cuenca, color_info in C_CUENCA.items():
    sub = df_normal[df_normal["cuenca"] == cuenca]
    if len(sub) == 0:
        continue
    sizes = [get_marker_size(p) for p in sub["prof_m"]]
    ax.scatter(sub["E_wgs84"], sub["N_wgs84"],
               c=color_info["fill"], s=sizes, marker="o",
               edgecolors=color_info["edge"], linewidths=0.7,
               alpha=0.88, zorder=5, label=f"Pozo subterráneo — {cuenca}")

# Surgentes (estrella dorada)
if len(df_surg):
    ax.scatter(df_surg["E_wgs84"], df_surg["N_wgs84"],
               c="#F1C40F", s=180, marker="*",
               edgecolors="#7D6608", linewidths=0.9,
               zorder=6, label="Pozo surgente (artesiano)")

# Monitoreo (triángulo naranja)
if len(df_monitor):
    ax.scatter(df_monitor["E_wgs84"], df_monitor["N_wgs84"],
               c="#E67E22", s=130, marker="^",
               edgecolors="#7E5109", linewidths=0.9,
               zorder=6, label="Pozo de monitoreo")

# ── Etiquetas pozos con estratigrafía completa ───────────────────────────
LABEL_POZOS = {
    "ND-1202-1299": "Morro Chico\n(43 m, NE=7.4 m)",
    "ND-1203-719" : "Nova Austral\n(62 m)",
    "ND-1203-739" : "Bahía Inútil\n(30 m)",
    "ND-1203-723" : "Cabaña Sur ZG-3\n(140 m, surgente)",
    "ND-1203-724" : "Lautaro Sur 7\n(80 m, surgente)",
}
for cod, label in LABEL_POZOS.items():
    row = gdf_pozos[gdf_pozos["codigo"] == cod]
    if len(row):
        E = row.iloc[0]["E_wgs84"]
        N = row.iloc[0]["N_wgs84"]
        ax.annotate(label,
                    xy=(E, N), xytext=(10, 8), textcoords="offset points",
                    fontsize=6.5, color="#1B2631",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7, ec="none"),
                    arrowprops=dict(arrowstyle="-", color="gray", lw=0.6),
                    zorder=8)

# ── Etiquetas de cuencas ──────────────────────────────────────────────────
LABEL_CUENCAS = {
    "Penitente": (330000, 4215000),
    "Oro"      : (445000, 4110000),
    "Robalo"   : (584640, 3907500),
}
for nombre, (LX, LY) in LABEL_CUENCAS.items():
    ax.text(LX, LY, f"Cuenca\nRío {nombre}",
            fontsize=9, fontweight="bold", color=C_CUENCA[nombre]["edge"],
            ha="center", va="center", zorder=9,
            bbox=dict(boxstyle="round,pad=0.35", fc="white", alpha=0.6, ec=C_CUENCA[nombre]["edge"], lw=0.8))

# ── Leyenda tamaño = profundidad ──────────────────────────────────────────
for prof, label in [(30, "sin dato"), (50, "50 m"), (100, "100 m"), (180, "180 m")]:
    s = get_marker_size(prof if prof > 30 else np.nan)
    ax.scatter([], [], c="gray", s=s, marker="o", alpha=0.7,
               edgecolors="k", linewidths=0.5, label=f"Profundidad ~{label}")

# ── Ejes y estética ───────────────────────────────────────────────────────
ax.set_xlabel("Este UTM [m]  —  WGS84 / UTM Zona 19S (EPSG:32719)", fontsize=9)
ax.set_ylabel("Norte UTM [m]", fontsize=9)
ax.set_title("Pozos Subterráneos — Cuencas Hidrológicas de Magallanes\n"
             "Región de Magallanes y Antártica Chilena", fontsize=12, fontweight="bold", pad=12)

ax.ticklabel_format(style="plain", axis="both")
ax.tick_params(labelsize=7.5)
ax.grid(True, linestyle="--", alpha=0.35, color="white", linewidth=0.8)
ax.set_aspect('equal', adjustable='datalim')

# ── Leyenda combinada ─────────────────────────────────────────────────────
leg = ax.legend(loc="lower left", fontsize=7.5, framealpha=0.92,
                edgecolor="#BDC3C7", title="Simbología", title_fontsize=8,
                ncol=1, markerscale=1.0)

# ── Escala gráfica aproximada (50 km) ────────────────────────────────────
xlim = ax.get_xlim()
ylim = ax.get_ylim()
sx0  = xlim[0] + (xlim[1] - xlim[0]) * 0.65
sy0  = ylim[0] + (ylim[1] - ylim[0]) * 0.04
ax.plot([sx0, sx0 + 50000], [sy0, sy0], color="k", lw=2.5, zorder=10)
ax.text(sx0 + 25000, sy0 + (ylim[1]-ylim[0])*0.01, "50 km",
        ha="center", fontsize=7.5, fontweight="bold", zorder=10)

# ── Norte ─────────────────────────────────────────────────────────────────
ax.annotate("N", xy=(xlim[0] + (xlim[1]-xlim[0])*0.95, ylim[0] + (ylim[1]-ylim[0])*0.92),
            fontsize=14, fontweight="bold", ha="center", va="center", zorder=10)
ax.annotate("↑", xy=(xlim[0] + (xlim[1]-xlim[0])*0.95, ylim[0] + (ylim[1]-ylim[0])*0.89),
            fontsize=16, ha="center", va="center", zorder=10)

plt.tight_layout()
out_static = os.path.join(FIG_DIR, "Fig11_Mapa_Pozos_Cuencas.png")
fig.savefig(out_static, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"  → Mapa estático: {out_static}")

# ── ═══════════════════════════════════════════════════════════════════════
#    MAPA INTERACTIVO FOLIUM
# ══════════════════════════════════════════════════════════════════════════
print("Generando mapa interactivo Folium ...")

# Centro del mapa (centroide de todas las cuencas)
lat_c, lon_c = utm_to_latlon(440000, 4075000)
m = folium.Map(location=[lat_c, lon_c], zoom_start=8,
               tiles="CartoDB positron",
               attr="© CartoDB © OpenStreetMap contributors")

# ── Capa cuencas ──────────────────────────────────────────────────────────
CUENCA_GDF = [
    (gdf_pen, "Penitente", "#3498DB"),
    (gdf_oro, "Oro",       "#E74C3C"),
    (gdf_rob, "Robalo",    "#27AE60"),
]
for gdf_c, nombre, color in CUENCA_GDF:
    gdf_ll = gdf_c.to_crs("EPSG:4326")
    folium.GeoJson(
        gdf_ll.__geo_interface__,
        name=f"Cuenca Río {nombre}",
        style_function=lambda f, c=color: {
            "fillColor": c, "color": c,
            "weight": 1.8, "fillOpacity": 0.18,
        },
        tooltip=f"Cuenca Río {nombre}",
    ).add_to(m)

# ── Capa red hídrica ───────────────────────────────────────────────────────
for gdf_rh, nombre, color in [
    (gdf_rh_pen, "Penitente", "#3498DB"),
    (gdf_rh_oro, "Oro",       "#E74C3C"),
    (gdf_rh_rob, "Robalo",    "#27AE60"),
]:
    gdf_ll = gdf_rh.to_crs("EPSG:4326")
    folium.GeoJson(
        gdf_ll.__geo_interface__,
        name=f"Red hídrica {nombre}",
        style_function=lambda f, c=color: {
            "color": c, "weight": 1.0, "opacity": 0.65,
        },
    ).add_to(m)

# ── Pozos como marcadores ─────────────────────────────────────────────────
ICON_COLOR_MAP = {
    "Penitente": "blue",
    "Oro"      : "red",
    "Robalo"   : "green",
}

fg_pozos = folium.FeatureGroup(name="Pozos subterráneos", show=True)

for _, row in gdf_pozos.iterrows():
    lat, lon = utm_to_latlon(row["E_wgs84"], row["N_wgs84"])
    cuenca   = str(row.get("cuenca", ""))
    cod      = str(row.get("codigo", ""))
    nombre   = str(row.get("nombre", "")) or str(row.get("titular", ""))[:40]
    prof     = row.get("prof_m")
    ne       = row.get("ne_m")
    caudal   = row.get("caudal_ls")
    surgente = row.get("surgente", False)
    estado   = str(row.get("estado", ""))
    fuente   = str(row.get("fuente", ""))
    obs      = str(row.get("observaciones", ""))

    # Determinar icono
    if cod == "INVERNADA-MON":
        icon_color, icon_name = "orange", "tint"
        tooltip_tag = "Monitoreo"
    elif surgente:
        icon_color, icon_name = "gold",   "star"
        tooltip_tag = "Surgente"
    else:
        icon_color = ICON_COLOR_MAP.get(cuenca, "gray")
        icon_name  = "tint"
        tooltip_tag = "Subterráneo"

    # Popup HTML
    prof_str   = f"{prof:.0f} m"  if pd.notna(prof)   else "s/d"
    ne_str     = f"{ne:.2f} m"   if pd.notna(ne)     else "s/d"
    caudal_str = f"{caudal:.1f} L/s" if pd.notna(caudal) else "s/d"
    acuif_ini  = row.get("acuifero_ini")
    acuif_fin  = row.get("acuifero_fin")
    estrat_str = str(row.get("estrat", "")) or "—"
    acuif_str  = (f"{acuif_ini:.0f}–{acuif_fin:.0f} m"
                  if pd.notna(acuif_ini) and pd.notna(acuif_fin)
                  else "—")
    surg_str   = "✔ Surgente" if surgente else "—"
    vol_str    = f"{row.get('vol_mee_m3a'):,.0f} m³/año" if pd.notna(row.get('vol_mee_m3a')) else "—"

    popup_html = f"""
    <div style="font-family:Arial,sans-serif;font-size:12px;width:300px">
      <b style="font-size:13px;color:#2C3E50">{cod}</b><br>
      <i style="color:#7F8C8D">{nombre}</i><hr style="margin:4px 0">
      <table style="width:100%;border-collapse:collapse">
        <tr><td style="color:#5D6D7E;padding:1px 4px"><b>Cuenca</b></td>
            <td style="padding:1px 4px">{cuenca}</td></tr>
        <tr><td style="color:#5D6D7E;padding:1px 4px"><b>Tipo</b></td>
            <td style="padding:1px 4px">{tooltip_tag}</td></tr>
        <tr style="background:#F2F3F4"><td style="color:#5D6D7E;padding:1px 4px"><b>Est. DGA</b></td>
            <td style="padding:1px 4px">{estado}</td></tr>
        <tr><td style="color:#5D6D7E;padding:1px 4px"><b>Profundidad</b></td>
            <td style="padding:1px 4px">{prof_str}</td></tr>
        <tr style="background:#F2F3F4"><td style="color:#5D6D7E;padding:1px 4px"><b>Nivel estático</b></td>
            <td style="padding:1px 4px">{ne_str}</td></tr>
        <tr><td style="color:#5D6D7E;padding:1px 4px"><b>Caudal</b></td>
            <td style="padding:1px 4px">{caudal_str}</td></tr>
        <tr style="background:#F2F3F4"><td style="color:#5D6D7E;padding:1px 4px"><b>Surgente</b></td>
            <td style="padding:1px 4px">{surg_str}</td></tr>
        <tr><td style="color:#5D6D7E;padding:1px 4px"><b>Acuífero</b></td>
            <td style="padding:1px 4px">{acuif_str}</td></tr>
        <tr style="background:#F2F3F4"><td style="color:#5D6D7E;padding:1px 4px"><b>Vol. MEE</b></td>
            <td style="padding:1px 4px">{vol_str}</td></tr>
        <tr><td style="color:#5D6D7E;padding:1px 4px"><b>Fuente</b></td>
            <td style="padding:1px 4px;font-size:10px">{fuente}</td></tr>
      </table>
      {'<hr style="margin:4px 0"><b>Estratigrafía:</b><br><span style="font-size:10px">' + estrat_str + '</span>' if estrat_str and estrat_str != "—" else ""}
      <hr style="margin:4px 0">
      <span style="font-size:10px;color:#7F8C8D">{obs[:120]}{'…' if len(obs)>120 else ''}</span>
    </div>
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=f"{cod} | {cuenca} | Prof: {prof_str}",
        icon=folium.Icon(color=icon_color, icon=icon_name, prefix="fa"),
    ).add_to(fg_pozos)

fg_pozos.add_to(m)

# ── Control de capas ───────────────────────────────────────────────────────
folium.LayerControl(collapsed=False).add_to(m)

# ── Leyenda HTML ───────────────────────────────────────────────────────────
legend_html = """
<div style="
    position: fixed;
    bottom: 30px; right: 30px;
    z-index: 1000;
    background-color: white;
    padding: 12px 16px;
    border: 1px solid #BDC3C7;
    border-radius: 8px;
    font-family: Arial, sans-serif;
    font-size: 12px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.15);
    min-width: 180px;
">
  <b style="font-size:13px">Leyenda</b><hr style="margin:4px 0">
  <div><span style="color:#3498DB;font-size:16px">●</span>  Pozo — Cuenca Penitente</div>
  <div><span style="color:#E74C3C;font-size:16px">●</span>  Pozo — Cuenca El Oro</div>
  <div><span style="color:#27AE60;font-size:16px">●</span>  Pozo — Cuenca Róbalo</div>
  <div><span style="color:#F1C40F;font-size:16px">★</span>  Pozo surgente (artesiano)</div>
  <div><span style="color:#E67E22;font-size:16px">▲</span>  Pozo de monitoreo</div>
  <hr style="margin:4px 0">
  <div style="font-size:10px;color:#7F8C8D">Click en marcador → popup</div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# ── Guardar HTML ──────────────────────────────────────────────────────────
out_html = os.path.join(OUT_DIR, "mapa_pozos_interactivo.html")
m.save(out_html)
print(f"  → Mapa interactivo: {out_html}")

# ── SUMMARY ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("ARCHIVOS GENERADOS")
print("=" * 60)
print(f"  PNG : {out_static}")
print(f"  HTML: {out_html}")
print("=" * 60)
print("Script 11 (mapa pozos) completado.")
