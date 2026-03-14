"""
Script 03: Modelo Conceptual Superficial Preliminar — Por Cuenca
Proyecto: Análisis de Recursos Hídricos - Cuencas Magallanes (IDIEM/DGA)
Propósito: Generar diagramas de nodos WEAP-style del balance hídrico superficial
           para cada cuenca de estudio por SEPARADO, incluyendo:
           - Diagrama de nodos (catchments, ríos, demandas, lagunas, acuífero)
           - Balance hídrico superficial esquemático a escala con valores
           - Mapa conceptual de subcuencas internas
           Resolución Observación DGA N°7 (Sección 5.1.2 del Informe Etapa 1)
Autor: Especialista Senior en Modelación
Fecha: 11-03-2026
Software: Python 3 / matplotlib / networkx (código abierto, entregable a DGA)
"""

import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import matplotlib.gridspec as gridspec
import networkx as nx
from project_paths import BASE_DIR, PY_SCRIPTS_DIR, resolve_input

# -------------------------------------------------------------------
# RUTAS
# -------------------------------------------------------------------
OUT_DIR   = PY_SCRIPTS_DIR
JSON_PATH = resolve_input("02 PyScripts Magallanes/datos_cuencas.json")
FIG_DIR   = os.path.join(OUT_DIR, "Figuras_Obs7_ModeloSuperficial")
os.makedirs(FIG_DIR, exist_ok=True)

with open(JSON_PATH, encoding="utf-8") as f:
    CUENCAS = json.load(f)

# -------------------------------------------------------------------
# ESTILOS
# -------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "figure.facecolor": "white",
})

DGA_BLUE = "#003087"
C = {
    "catchment": "#A8D8A8",   # verde - área generadora de escorrentía
    "lago":      "#AED6F1",   # azul claro - almacenamiento
    "rio":       "#2E86AB",   # azul río
    "demanda":   "#F1948A",   # rojo suave - demanda
    "acuifero":  "#F9E79F",   # amarillo - acuífero
    "salida":    "#85C1E9",   # azul oscuro - salida cuenca
    "lluvia":    "#D6EAF8",   # lluvia/precip
    "et":        "#FDEBD0",   # naranja claro - ET
    "borde":     "#2C3E50",
}

# -------------------------------------------------------------------
# DEFINICIÓN DE NODOS POR CUENCA
# -------------------------------------------------------------------

MODELOS_SUP = {
    "Penitente": {
        "titulo": "Cuenca del Río Penitente",
        "subtitulo": "Sistema hidrológico semi-árido — BSk | Área: 1,750 km²",
        "descripcion_modelo": (
            "Sistema de modelación: WEAP (Water Evaluation and Planning System)\n"
            "Cuenca semi-árida, fuerte demanda ganadera, recarga subterránea limitada.\n"
            "La cuenca se subdivide en 3 subcatchments según zonas BNA y características climáticas-topográficas."
        ),
        "nodos": [
            # Catchments (subcuencas) - generadores de escorrentía
            {"id": "C1", "tipo": "catchment", "label": "Subcuenca Alta\nCordillera\n(480 km²)", "pos": (0.15, 0.75)},
            {"id": "C2", "tipo": "catchment", "label": "Subcuenca Media\nPampa\n(820 km²)", "pos": (0.45, 0.78)},
            {"id": "C3", "tipo": "catchment", "label": "Subcuenca Baja\nLlanura\n(450 km²)", "pos": (0.72, 0.70)},
            # Lagunas
            {"id": "L1", "tipo": "lago", "label": "Lagunas\nestepáricas\n(3.2 km²)", "pos": (0.30, 0.58)},
            # Río principal (nodo de tránsito)
            {"id": "R1", "tipo": "rio", "label": "Río Penitente\n(tramo alto)", "pos": (0.22, 0.48)},
            {"id": "R2", "tipo": "rio", "label": "Río Penitente\n(tramo medio)", "pos": (0.50, 0.42)},
            {"id": "R3", "tipo": "rio", "label": "Río Penitente\nen Morro Chico\n(Q=3.2 m³/s)", "pos": (0.75, 0.35)},
            # Acuífero
            {"id": "A1", "tipo": "acuifero", "label": "SHAC Penitente\n(Acuífero libre\nCuaternario)", "pos": (0.50, 0.20)},
            # Demandas
            {"id": "D1", "tipo": "demanda", "label": "Ganadería\n(26.4 L/s)", "pos": (0.60, 0.60)},
            {"id": "D2", "tipo": "demanda", "label": "Cons. Humano\nRural (2.1 L/s)", "pos": (0.80, 0.55)},
            # Salida
            {"id": "S1", "tipo": "salida", "label": "Estrecho de\nMagallanes\n(salida cuenca)", "pos": (0.92, 0.28)},
        ],
        "flechas": [
            # Catchments → Red hídrica
            ("C1", "R1", "Esc. directa\n+ Percolación", "green"),
            ("C2", "R2", "Esc. directa\n+ Percolación", "green"),
            ("C3", "R3", "Esc. directa", "green"),
            # Lagunas
            ("L1", "R2", "Descarga\nlagunar", "blue"),
            ("C1", "L1", "Aporte\nsuperficial", "steelblue"),
            # Río principal
            ("R1", "R2", "Q tramo →", "blue"),
            ("R2", "R3", "Q tramo →", "blue"),
            ("R3", "S1", "Q salida\n(aforo)", "navy"),
            # Acuífero
            ("R2", "A1", "Percolación\nprofunda", "goldenrod"),
            ("A1", "R3", "Baseflow\n(descarga)", "darkorange"),
            # Demandas
            ("R2", "D1", "Extracción\nDAA sup.", "red"),
            ("R3", "D2", "Extracción\nDAA sup.", "red"),
            ("A1", "D2", "DAA\nsubterráneo", "darkred"),
        ],
        "val_pp_subcuencas": {"C1": 160, "C2": 115, "C3": 90},   # mm/año PP
        "val_et_subcuencas": {"C1": 130, "C2": 110, "C3": 90},
        "val_q_salida": 3.2,   # m³/s
        "estacion_control": "Penitente en Morro Chico",
        "pp_media": 120, "etr_media": 110, "q_mm": 57, "rec_mm": 10,
    },
    "El Oro": {
        "titulo": "Cuenca del Río El Oro",
        "subtitulo": "Sistema hidrológico húmedo — Csc | Área: 707 km²  |  Tierra del Fuego",
        "descripcion_modelo": (
            "Sistema de modelación: WEAP (Water Evaluation and Planning System)\n"
            "Cuenca húmeda con escorrentía significativa. Presencia de glaciar remanente.\n"
            "Se subdivide en 2 subcatchments: alta montaña (glaciar+nival) y piedemonte-valle."
        ),
        "nodos": [
            {"id": "GL", "tipo": "catchment", "label": "Glaciar + Area\nNival (alta)\n(~80 km²)", "pos": (0.18, 0.78)},
            {"id": "C1", "tipo": "catchment", "label": "Subcuenca Alta\nMontaña\n(280 km²)", "pos": (0.40, 0.80)},
            {"id": "C2", "tipo": "catchment", "label": "Subcuenca Baja\nValle Rio Oro\n(347 km²)", "pos": (0.68, 0.72)},
            {"id": "L1", "tipo": "lago", "label": "Laguna\nBaquedano\n(0.5 km²)", "pos": (0.30, 0.57)},
            {"id": "R1", "tipo": "rio", "label": "Río El Oro\n(tramo alto)", "pos": (0.35, 0.44)},
            {"id": "R2", "tipo": "rio", "label": "Río El Oro\nBahía San Felipe\n(Q=10.5 m³/s)", "pos": (0.68, 0.35)},
            {"id": "A1", "tipo": "acuifero", "label": "SHAC Río Oro\n(Acuífero libre\nCuaternario TF)", "pos": (0.50, 0.18)},
            {"id": "D1", "tipo": "demanda", "label": "Ganadería TF\n(41.7 L/s)", "pos": (0.58, 0.60)},
            {"id": "D2", "tipo": "demanda", "label": "Cons. Humano\n(3.5 L/s)", "pos": (0.80, 0.55)},
            {"id": "S1", "tipo": "salida", "label": "Bahía San Felipe\n(Canal Beagle)\nSalida cuenca", "pos": (0.90, 0.28)},
        ],
        "flechas": [
            ("GL", "R1",  "Deshielo +\nEscorrentía nival", "deepskyblue"),
            ("C1", "R1",  "Esc. directa\n+ Percolación", "green"),
            ("C2", "R2",  "Esc. directa", "green"),
            ("C1", "L1",  "Aporte sup.", "steelblue"),
            ("L1", "R1",  "Descarga\nlagunar", "blue"),
            ("R1", "R2",  "Q tramo →\n(río principal)", "blue"),
            ("R2", "S1",  "Q salida\n(aforo Bahía SF)", "navy"),
            ("C2", "A1",  "Percolación\nprofunda", "goldenrod"),
            ("A1", "R2",  "Baseflow →", "darkorange"),
            ("R2", "D1",  "Extracción\nDAA sup.", "red"),
            ("R2", "D2",  "Extracción", "red"),
            ("A1", "D2",  "DAA\nsubterráneo", "darkred"),
        ],
        "val_pp_subcuencas": {"GL": 1100, "C1": 950, "C2": 800},
        "val_et_subcuencas": {"GL": 200, "C1": 380, "C2": 380},
        "val_q_salida": 10.5,
        "estacion_control": "Oro en Bahía San Felipe",
        "pp_media": 900, "etr_media": 380, "q_mm": 468, "rec_mm": 108,
    },
    "Robalo": {
        "titulo": "Cuenca del Río Róbalo",
        "subtitulo": "Cuenca torrencial de montaña — ET (Tundra) | Área: 22 km² | Puerto Williams",
        "descripcion_modelo": (
            "Sistema de modelación: WEAP (Water Evaluation and Planning System)\n"
            "Cuenca muy pequeña y abrupta (22 km²). Dominada por escorrentía directa.\n"
            "CRÍTICA: único suministro de agua potable de Puerto Williams (3,000 hab).\n"
            "Un solo catchment de montaña → obras de captación → distribución AP."
        ),
        "nodos": [
            {"id": "C1", "tipo": "catchment", "label": "Cuenca Montaña\nCerro Bandera\n(22 km²)", "pos": (0.20, 0.75)},
            {"id": "L1", "tipo": "lago", "label": "Lagunas\ntorrente\n(0.52 km²)", "pos": (0.40, 0.57)},
            {"id": "R1", "tipo": "rio", "label": "Río Róbalo\n(3.65 km)\nQ=0.45 m³/s", "pos": (0.55, 0.42)},
            {"id": "A1", "tipo": "acuifero", "label": "Acuífero\nFisurado\n(limitado)", "pos": (0.38, 0.22)},
            {"id": "OT", "tipo": "demanda", "label": "Obra Toma\nAguas Magallanes\n(captación AP)", "pos": (0.72, 0.55)},
            {"id": "D1", "tipo": "demanda", "label": "Agua Potable\nPuerto Williams\n(12.0 L/s)", "pos": (0.85, 0.38)},
            {"id": "S1", "tipo": "salida", "label": "Canal Beagle\n(salida cuenca)", "pos": (0.85, 0.22)},
        ],
        "flechas": [
            ("C1", "L1",  "Esc. directa\n+ int. lagunare", "green"),
            ("L1", "R1",  "Descarga\nlagunar", "blue"),
            ("C1", "R1",  "Esc. directa\n(torrencial)", "darkgreen"),
            ("R1", "OT",  "Captación AP\n(Aguas Magallanes)", "blue"),
            ("OT", "D1",  "Distribución\nAP urbana", "darkblue"),
            ("C1", "A1",  "Infiltración\n(fisuras roca)", "goldenrod"),
            ("A1", "R1",  "Baseflow\n(débil)", "darkorange"),
            ("R1", "S1",  "Excedentes →\nCanal Beagle", "navy"),
        ],
        "val_pp_subcuencas": {"C1": 700},
        "val_et_subcuencas": {"C1": 280},
        "val_q_salida": 0.45,
        "estacion_control": "Róbalo en Puerto Williams",
        "pp_media": 700, "etr_media": 280, "q_mm": 646, "rec_mm": 35,
    },
}

# -------------------------------------------------------------------
# TIPOS DE NODOS: forma y color
# -------------------------------------------------------------------

ESTILOS_NODOS = {
    "catchment": {"shape": "ellipse", "color": C["catchment"], "ec": "#2D7025", "lw": 1.8, "size": (0.14, 0.08)},
    "lago":      {"shape": "ellipse", "color": C["lago"],      "ec": "#1565C0", "lw": 1.5, "size": (0.10, 0.06)},
    "rio":       {"shape": "box",     "color": C["rio"],       "ec": "#154360", "lw": 1.5, "size": (0.13, 0.07)},
    "acuifero":  {"shape": "diamond", "color": C["acuifero"],  "ec": "#7D6608", "lw": 1.8, "size": (0.13, 0.075)},
    "demanda":   {"shape": "box",     "color": C["demanda"],   "ec": "#922B21", "lw": 1.5, "size": (0.12, 0.065)},
    "salida":    {"shape": "hexagon", "color": C["salida"],    "ec": "#1A5276", "lw": 2.0, "size": (0.12, 0.065)},
}


def draw_node(ax, x, y, tipo, label):
    """Dibuja un nodo según su tipo."""
    est = ESTILOS_NODOS[tipo]
    w, h = est["size"]
    color = est["color"]
    ec    = est["ec"]
    lw    = est["lw"]

    if est["shape"] in ("ellipse", "box"):
        if est["shape"] == "box":
            patch = FancyBboxPatch((x - w/2, y - h/2), w, h,
                                   boxstyle="round,pad=0.01",
                                   facecolor=color, edgecolor=ec,
                                   linewidth=lw, zorder=3)
        else:
            patch = mpatches.Ellipse((x, y), w, h,
                                     facecolor=color, edgecolor=ec,
                                     linewidth=lw, zorder=3)
        ax.add_patch(patch)

    elif est["shape"] == "diamond":
        pts = np.array([[x, y+h/2], [x+w/2, y], [x, y-h/2], [x-w/2, y]])
        diamond = plt.Polygon(pts, closed=True,
                              facecolor=color, edgecolor=ec,
                              linewidth=lw, zorder=3)
        ax.add_patch(diamond)

    elif est["shape"] == "hexagon":
        angles = np.linspace(30, 390, 7) * np.pi / 180
        xs = x + w/2 * np.cos(angles)
        ys = y + h/2 * np.sin(angles)
        hex_p = plt.Polygon(list(zip(xs, ys)), closed=True,
                             facecolor=color, edgecolor=ec,
                             linewidth=lw, zorder=3)
        ax.add_patch(hex_p)

    ax.text(x, y, label, ha="center", va="center",
            fontsize=7, fontweight="bold" if tipo in ("rio", "acuifero") else "normal",
            color=ec, zorder=4, multialignment="center")


def draw_arrow(ax, pos_dict, src, dst, label, color):
    """Dibuja una flecha entre dos nodos con etiqueta."""
    x0, y0 = pos_dict[src]
    x1, y1 = pos_dict[dst]

    # Pequeño offset para evitar que la flecha comience en el centro
    dx = x1 - x0
    dy = y1 - y0
    dist = np.hypot(dx, dy)
    if dist == 0:
        return
    nx_, ny_ = dx/dist, dy/dist
    offset = 0.04
    x0s = x0 + nx_ * offset * 1.2
    y0s = y0 + ny_ * offset * 0.8
    x1e = x1 - nx_ * offset
    y1e = y1 - ny_ * offset * 0.8

    ax.annotate("", xy=(x1e, y1e), xytext=(x0s, y0s),
                arrowprops=dict(arrowstyle="-|>",
                                color=color, lw=1.5,
                                mutation_scale=12,
                                connectionstyle="arc3,rad=0.05"),
                zorder=2)
    mx, my = (x0s + x1e) / 2, (y0s + y1e) / 2
    # Pequeño desvío para que el texto no quede sobre la flecha
    perp_x = -dy / dist * 0.04
    perp_y =  dx / dist * 0.035
    ax.text(mx + perp_x, my + perp_y, label,
            ha="center", va="center", fontsize=6,
            color=color, zorder=5,
            bbox=dict(fc="white", ec=color, alpha=0.85,
                      boxstyle="round,pad=0.12", lw=0.7))


def dibujar_barra_balance(ax_bar, mod, cuenca_data):
    """Barra de balance hídrico superficial."""
    ax_bar.set_facecolor("#F8F9FA")
    pp  = mod["pp_media"]
    etr = mod["etr_media"]
    q   = mod["q_mm"]
    rec = mod["rec_mm"]

    labels = ["P\n(Precipitación)", "ETR\n(Evapotransp.)", "Q\n(Escorrentía)", "Rec\n(Recarga)"]
    valores = [pp, etr, q, rec]
    colores = ["#2980B9", "#E67E22", "#27AE60", "#F39C12"]

    bars = ax_bar.bar(labels, valores, color=colores, edgecolor="white",
                      linewidth=1.5, zorder=3, width=0.55)
    for bar, val in zip(bars, valores):
        ax_bar.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + pp*0.02,
                    f"{val} mm/año\n({val/pp*100:.0f}% P)",
                    ha="center", va="bottom", fontsize=8,
                    fontweight="bold", color="#222")

    ax_bar.set_ylabel("Altura de agua (mm/año)", fontsize=8)
    ax_bar.set_title("Balance Hídrico Superficial\n(valores anuales promedio)",
                     fontsize=9, fontweight="bold", color=DGA_BLUE)
    ax_bar.axhline(y=pp, color="#2980B9", linestyle="--", linewidth=1.2,
                   alpha=0.6, label=f"P = {pp} mm/año")
    ax_bar.yaxis.grid(True, linestyle=":", alpha=0.5, zorder=0)
    ax_bar.set_axisbelow(True)

    # Anotar cierre de balance
    cierre = pp - etr - q - rec
    ax_bar.text(0.98, 0.97,
                f"ΔS = P - ETR - Q - Rec\n= {pp} - {etr} - {q} - {rec}\n= {cierre} mm/año",
                ha="right", va="top", fontsize=7.5,
                transform=ax_bar.transAxes,
                color="#555", style="italic",
                bbox=dict(fc="#FFFFF0", ec="#CCCC00",
                          boxstyle="round,pad=0.3", alpha=0.9))
    ax_bar.legend(fontsize=7.5, loc="upper center")


def generar_modelo_superficial(nombre_cuenca, mod, cuenca_data):
    """Genera la figura completa del modelo conceptual superficial."""
    fig = plt.figure(figsize=(20, 12), dpi=150)
    fig.patch.set_facecolor("white")

    gs = gridspec.GridSpec(1, 2, figure=fig,
                           width_ratios=[1.7, 1],
                           wspace=0.25, left=0.03, right=0.97,
                           top=0.88, bottom=0.06)

    ax_nodos = fig.add_subplot(gs[0, 0])
    ax_bar   = fig.add_subplot(gs[0, 1])

    # ── DIAGRAMA DE NODOS ────────────────────────────────────────────
    ax_nodos.set_facecolor("#EEF4FF")
    ax_nodos.set_xlim(0, 1)
    ax_nodos.set_ylim(0, 1)
    ax_nodos.axis("off")

    # Fondo estilizado - lluvia encima
    ax_nodos.text(0.5, 0.96, "☁   P (Precipitación)   ☁",
                  ha="center", va="top", fontsize=8,
                  color="#2980B9", style="italic",
                  bbox=dict(fc="#D6EAF8", ec="#2980B9",
                            boxstyle="round,pad=0.3", alpha=0.9))
    ax_nodos.text(0.5, 0.905, "⬇  P distribuida uniformemente sobre la cuenca  ⬇",
                  ha="center", va="top", fontsize=7.5,
                  color="#1A5276", style="italic")

    # Número de flechas "lluvia"
    for xi in [0.10, 0.28, 0.46, 0.64, 0.82]:
        ax_nodos.annotate("", xy=(xi, 0.88), xytext=(xi, 0.94),
                          arrowprops=dict(arrowstyle="-|>",
                                          color="#2980B9", lw=1.2,
                                          mutation_scale=8))

    # Posiciones de nodos
    pos_dict = {n["id"]: n["pos"] for n in mod["nodos"]}

    # Dibujar flechas primero (debajo de nodos)
    for (src, dst, label, color) in mod["flechas"]:
        draw_arrow(ax_nodos, pos_dict, src, dst, label, color)

    # Dibujar nodos
    for nodo in mod["nodos"]:
        draw_node(ax_nodos, nodo["pos"][0], nodo["pos"][1],
                  nodo["tipo"], nodo["label"])

    # Leyenda de nodos
    leyenda = [
        mpatches.Patch(color=C["catchment"], ec="#2D7025", lw=1.5,
                       label="Subcuenca / Catchment (fuente escorrentía)"),
        mpatches.Patch(color=C["lago"], ec="#1565C0", lw=1.5,
                       label="Cuerpo lacustre (almacenamiento sup.)"),
        mpatches.Patch(color=C["rio"], ec="#154360", lw=1.5,
                       label="Tramo de río / punto de caudal"),
        mpatches.Patch(color=C["acuifero"], ec="#7D6608", lw=1.5,
                       label="Acuífero (almacenamiento sub.)"),
        mpatches.Patch(color=C["demanda"], ec="#922B21", lw=1.5,
                       label="Nodo de demanda (extracción)"),
        mpatches.Patch(color=C["salida"], ec="#1A5276", lw=1.5,
                       label="Punto de salida (cierre cuenca)"),
    ]
    ax_nodos.legend(handles=leyenda, loc="lower left", fontsize=6.5,
                    framealpha=0.9, edgecolor=DGA_BLUE, ncol=2,
                    title="SIMBOLOGÍA", title_fontsize=7)

    # Información modelo
    ax_nodos.text(0.01, 0.01, mod["descripcion_modelo"],
                  ha="left", va="bottom", fontsize=6.5,
                  transform=ax_nodos.transAxes, style="italic",
                  color="#444",
                  bbox=dict(fc="white", ec="#AAAAAA",
                            boxstyle="round,pad=0.3", alpha=0.9))

    ax_nodos.set_title(
        f"Diagrama Conceptual Superficial — {mod['titulo']}\n{mod['subtitulo']}",
        fontsize=10, fontweight="bold", color=DGA_BLUE, pad=8
    )

    # ── BARRA DE BALANCE ────────────────────────────────────────────
    dibujar_barra_balance(ax_bar, mod, cuenca_data)

    # Añadir estación de control
    ax_bar.text(0.5, -0.12,
                f"Estación de control: {mod['estacion_control']}\n"
                f"Q medio = {mod['val_q_salida']} m³/s",
                ha="center", va="top", fontsize=8,
                transform=ax_bar.transAxes,
                color=DGA_BLUE, fontweight="bold",
                bbox=dict(fc="#EEF2F8", ec=DGA_BLUE,
                          boxstyle="round,pad=0.3", lw=1.2))

    # ── CABECERA Y PIE ──────────────────────────────────────────────
    fig.suptitle(
        f"MODELO CONCEPTUAL SUPERFICIAL PRELIMINAR\n{mod['titulo'].upper()}",
        fontsize=13, fontweight="bold", color=DGA_BLUE, y=0.97,
        bbox=dict(boxstyle="round,pad=0.3", fc="#EEF2F8",
                  ec=DGA_BLUE, lw=1.5)
    )
    fig.text(0.5, 0.01,
             f"Fuente: Elaboración propia — IDIEM/DGA  |  Resolución Obs. DGA N°7  |  "
             f"Software: Python 3 / matplotlib  |  Fecha: 11-03-2026",
             ha="center", va="bottom", fontsize=7,
             color="#555", style="italic")

    nombre_arch = f"MC_Superficial_{nombre_cuenca.replace(' ', '_')}.png"
    ruta = os.path.join(FIG_DIR, nombre_arch)
    fig.savefig(ruta, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"  ✓ Guardado: {nombre_arch}")
    return ruta


# -------------------------------------------------------------------
# EJECUCIÓN
# -------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "="*65)
    print("GENERANDO MODELOS CONCEPTUALES SUPERFICIALES POR CUENCA")
    print("Resolución Observación DGA N°7")
    print("="*65)

    mapeo = {
        "Penitente": ("Penitente", "Penitente"),
        "El Oro":    ("El Oro",    "El_Oro"),
        "Robalo":    ("Robalo",    "Robalo"),
    }

    rutas = []
    for key_json, (key_mod, nombre_arch) in mapeo.items():
        if key_json not in CUENCAS:
            print(f"  ⚠ '{key_json}' no en datos JSON")
            continue
        if key_mod not in MODELOS_SUP:
            print(f"  ⚠ Modelo superficial de '{key_mod}' no definido")
            continue
        print(f"\n  Generando: {MODELOS_SUP[key_mod]['titulo']}...")
        r = generar_modelo_superficial(nombre_arch, MODELOS_SUP[key_mod],
                                       CUENCAS[key_json])
        rutas.append(r)

    print(f"\n{'='*65}")
    print(f"✓ {len(rutas)} figuras generadas en:")
    print(f"  {FIG_DIR}")
    print("\nACCIÓN SIGUIENTE: Ejecutar 04_balance_hidrico_cuencas.py")
