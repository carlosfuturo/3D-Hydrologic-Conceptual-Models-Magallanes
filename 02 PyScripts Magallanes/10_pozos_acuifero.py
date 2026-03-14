"""
Script 10: Sistematización de Pozos y Datos de Acuífero
Proyecto: Análisis de Recursos Hídricos - Cuencas Magallanes (IDIEM/DGA)
Propósito: Extraer, limpiar y sistematizar datos de pozos subterráneos
           de todas las fuentes disponibles (DGA, SEIA, expedientes DGA,
           pozo monitoreo, MEE extracciones).
           Genera GeoJSON, CSV, y figuras resumen de distribución y
           profundidades por cuenca.
Fuentes de datos:
  - Derechos_de_Agua.xlsx       : 34 derechos agua c/ coordenadas y observaciones
  - DDAA_subte.xlsx             : 9 pozos subterráneos con Q concedido
  - pozo_nuevo.shp              : Pozo La Invernada (monitoreo)
  - MEE/Rio_Oro.csv             : Extracciones efectivas cuenca El Oro
  - Datos PDF extraídos manual : 5 pozos con estratigrafía completa
                                  (ND-1202-1299, ND-1203-719, ND-1203-739,
                                   ND-1203-723, ND-1203-724)
Autor: Especialista Senior en Modelación
Fecha: 2026
"""

import os, re, json, warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba
from pyproj import Transformer
from project_paths import BASE_DIR, PY_SCRIPTS_DIR, resolve_input

warnings.filterwarnings("ignore")

# ── RUTAS ─────────────────────────────────────────────────────────────────
ANT_DIR  = os.path.join(BASE_DIR, "01 Etapa 1", "Antecedentes")
POZ_DIR  = os.path.join(ANT_DIR, "Pozos")
OUT_DIR  = PY_SCRIPTS_DIR
FIG_DIR  = os.path.join(OUT_DIR, "Figuras_Pozos_Acuifero")
os.makedirs(FIG_DIR, exist_ok=True)

DDAA_XLSX    = resolve_input("01 Etapa 1/Antecedentes/Pozos/Consolidado Pozos/Derechos_de_Agua.xlsx")
DDAA_S_XLSX  = resolve_input("01 Etapa 1/Antecedentes/Pozos/DDAA_subte.xlsx")
POZO_SHP     = resolve_input("01 Etapa 1/Antecedentes/Pozos/pozo_nuevo.shp")
MEE_ORO_CSV  = resolve_input("01 Etapa 1/Antecedentes/MEE/Rio_Oro.csv")

# ── TRANSFORMADOR DATUM 1969 → WGS84 ─────────────────────────────────────
# DATUM 1969 (Huso 19) = PSAD56 / UTM Zone 19S = EPSG:24879
# DATUM 1984 (Huso 19) = WGS84 / UTM Zone 19S  = EPSG:32719
T_1969 = Transformer.from_crs("EPSG:24879", "EPSG:32719", always_xy=True)

def to_wgs84(E_orig, N_orig, datum):
    """Convierte coordenadas UTM Zona 19 al datum WGS84 (EPSG:32719)."""
    d = int(datum) if datum else 1984
    if d == 1969:
        E_wgs, N_wgs = T_1969.transform(E_orig, N_orig)
        return round(E_wgs, 1), round(N_wgs, 1)
    else:  # 1984 ya es WGS84
        return float(E_orig), float(N_orig)

# ── EXTRACCIÓN DE PROFUNDIDAD DESDE TEXTO ─────────────────────────────────
# Patrones en orden de especificidad decreciente
_DEPTH_PATTERNS = [
    (r'\((\d+)\s*o\s*(\d+)\s*m\)',   lambda m: (int(m.group(1)) + int(m.group(2))) / 2),
    (r'profundidad\s+([\d,\.]+)\s*m', lambda m: float(m.group(1).replace(',', '.'))),
    (r'Profundidad\s+([\d,\.]+)\s*m', lambda m: float(m.group(1).replace(',', '.'))),
    (r'\(([\d]+)\s*m\)',              lambda m: float(m.group(1))),
    (r'[Pp]ozo\s+(\d+)\s*m',         lambda m: float(m.group(1))),
    (r'([\d]+)\s*m[,\s]',            lambda m: float(m.group(1))),
]

def parse_depth(text):
    """Extrae la profundidad en metros de un string de observaciones."""
    if not text or str(text).strip() in ('', 'None', 'nan'):
        return np.nan
    for pat, func in _DEPTH_PATTERNS:
        m = re.search(pat, str(text), re.IGNORECASE)
        if m:
            return func(m)
    return np.nan

def is_surgente(text):
    """Indica si el pozo es surgente/artesiano."""
    if not text:
        return False
    return bool(re.search(r'surgente|artesiano|artesian', str(text), re.IGNORECASE))

# ── DATOS ESTRATIGRÁFICOS EXTRAÍDOS DE PDFs ────────────────────────────────
# Fuente: expedientes DGA procesados en Script previo (extract_pozos.py)
# Unidad acuífera = "relleno cuaternario fluvioglacial" (gravas/arenas)
DATOS_PDF = {
    "ND-1202-1299": {
        "nombre"      : "Morro Chico",
        "cuenca"      : "Penitente",
        "E_orig"      : 331957,
        "N_orig"      : 4230484,
        "datum"       : 1984,
        "prof_m"      : 43.0,
        "ne_m"        : 7.40,   # nivel estático (m bajo brocal)
        "nd_m"        : 9.56,   # nivel dinámico (m bajo brocal)
        "caudal_ls"   : 1.2,
        "surgente"    : False,
        "estrat"      : [
            (0.0,  0.3,  "Capa vegetal"),
            (0.3,  3.0,  "Arcilla amarilla"),
            (3.0, 12.0,  "Arena y grava"),
            (12.0, 42.0, "Grava y piedra [ACUÍFERO]"),
            (42.0, 43.0, "Grava y arcilla gris"),
        ],
        "acuifero_ini": 3.0,
        "acuifero_fin": 42.0,
        "fuente"      : "Expediente DGA ND-1202-1299",
    },
    "ND-1203-719": {
        "nombre"      : "Nova Austral",
        "cuenca"      : "Oro",
        "E_orig"      : 409225,
        "N_orig"      : 4093261,
        "datum"       : 1984,
        "prof_m"      : 62.0,
        "ne_m"        : 2.14,
        "nd_m"        : 40.76,  # nivel máx en prueba de bombeo (1860 min)
        "caudal_ls"   : 2.0,
        "surgente"    : False,
        "estrat"      : [],     # estratigrafía en figuras del PDF, no digitalizable
        "acuifero_ini": np.nan,
        "acuifero_fin": np.nan,
        "fuente"      : "Expediente DGA ND-1203-719",
    },
    "ND-1203-739": {
        "nombre"      : "Bahía Inútil",
        "cuenca"      : "Oro",
        "E_orig"      : 479709,
        "N_orig"      : 4076333,
        "datum"       : 1984,
        "prof_m"      : 30.0,
        "ne_m"        : 5.30,
        "nd_m"        : np.nan,
        "caudal_ls"   : np.nan,
        "surgente"    : False,
        "estrat"      : [],
        "acuifero_ini": np.nan,
        "acuifero_fin": np.nan,
        "fuente"      : "Expediente DGA ND-1203-739",
    },
    "ND-1203-723": {
        "nombre"      : "Cabaña Sur ZG-3 (IPROMSA)",
        "cuenca"      : "Oro",
        "E_orig"      : 450184,
        "N_orig"      : 4144485,
        "datum"       : 1984,
        "prof_m"      : 140.0,
        "ne_m"        : np.nan,
        "nd_m"        : np.nan,
        "caudal_ls"   : np.nan,
        "surgente"    : True,
        "estrat"      : [],
        "acuifero_ini": np.nan,
        "acuifero_fin": np.nan,
        "fuente"      : "Expediente DGA ND-1203-723",
    },
    "ND-1203-724": {
        "nombre"      : "Lautaro Sur 7 (IPROMSA)",
        "cuenca"      : "Oro",
        "E_orig"      : 458714,
        "N_orig"      : 4142414,
        "datum"       : 1984,
        "prof_m"      : 80.0,
        "ne_m"        : np.nan,
        "nd_m"        : np.nan,
        "caudal_ls"   : np.nan,
        "surgente"    : True,
        "estrat"      : [],
        "acuifero_ini": np.nan,
        "acuifero_fin": np.nan,
        "fuente"      : "Expediente DGA ND-1203-724",
    },
}

# ── 1. LEER Derechos_de_Agua.xlsx ─────────────────────────────────────────
print("=" * 65)
print("SCRIPT 10 — Sistematización de Pozos y Acuíferos")
print("=" * 65)
print("\n[1/5] Leyendo Derechos_de_Agua.xlsx ...")

df_ddaa = pd.read_excel(DDAA_XLSX, sheet_name=0, engine="openpyxl")
# Estandarizar nombres de columnas
df_ddaa.columns = [str(c).strip() for c in df_ddaa.columns]
# Columnas clave: Cuenca, CODIGO, Estado, SOLICITANTE, TIPO DERECHO,
#                 Caudal L/s, N, E, HUSO, DATUM, Observaciones
col_map = {
    "Cuenca": "cuenca_raw",
    "CODIGO": "codigo",
    "Estado": "estado",
    "SOLICITANTE": "titular",
    "TIPO DERECHO": "tipo_derecho",
    "Caudal L/s": "caudal_xlsx_ls",
    "N": "N_orig",
    "E": "E_orig",
    "HUSO": "huso",
    "DATUM": "datum",
    "Observaciones": "observaciones",
    "Expediente?": "expediente",
}
df_ddaa = df_ddaa.rename(columns={k: v for k, v in col_map.items() if k in df_ddaa.columns})

# Filtrar filas con coordenadas válidas y código
df_ddaa = df_ddaa[df_ddaa["N_orig"].notna() & df_ddaa["E_orig"].notna()].copy()
df_ddaa = df_ddaa[df_ddaa["codigo"].notna()].copy()
df_ddaa["N_orig"] = pd.to_numeric(df_ddaa["N_orig"], errors="coerce")
df_ddaa["E_orig"] = pd.to_numeric(df_ddaa["E_orig"], errors="coerce")
df_ddaa = df_ddaa[df_ddaa["N_orig"].notna()].copy()

print(f"    → {len(df_ddaa)} registros cargados")

# ── 2. LEER DDAA_subte.xlsx para Q concedido ──────────────────────────────
print("\n[2/5] Leyendo DDAA_subte.xlsx ...")
df_sub = pd.read_excel(DDAA_S_XLSX, sheet_name=0, engine="openpyxl")
df_sub.columns = [str(c).strip() for c in df_sub.columns]
# Mapear caudal concedido por código
col_codigo = [c for c in df_sub.columns if "CODIGO" in c.upper()][0]
col_ls     = [c for c in df_sub.columns if "L/s" in c or "ls" in c.lower()][0]
q_dict = dict(zip(df_sub[col_codigo].astype(str).str.strip(),
                  pd.to_numeric(df_sub[col_ls], errors="coerce")))
print(f"    → {len(q_dict)} pozos subterráneos con Q en DDAA_subte")

# ── 3. LEER MEE/Rio_Oro.csv ───────────────────────────────────────────────
print("\n[3/5] Leyendo MEE/Rio_Oro.csv ...")
df_mee = pd.read_csv(MEE_ORO_CSV, sep=";", decimal=".", encoding="utf-8")
df_mee.columns = [c.strip() for c in df_mee.columns]
# Columnas clave: Código Obra, UTM Norte, UTM Este, Nombre del Titular,
#                 Volumen (m3/año), meses Ene-Dic
mee_anual = {}
for _, row in df_mee.iterrows():
    cod = str(row.get("Código Obra", "")).strip()
    try:
        vol = float(str(row.get("Volumen (m3/año)", "")).replace(",", "."))
    except (ValueError, TypeError):
        vol = np.nan
    if cod:
        mee_anual[cod] = vol
print(f"    → {len(mee_anual)} registros MEE El Oro ({len(df_mee)} filas)")

# ── 4. CONSTRUIR DATASET PRINCIPAL ─────────────────────────────────────────
print("\n[4/5] Construyendo dataset unificado ...")

records = []

for _, row in df_ddaa.iterrows():
    cod  = str(row.get("codigo", "")).strip()
    obs  = str(row.get("observaciones", ""))
    datum = int(row.get("datum", 1984)) if pd.notna(row.get("datum")) else 1984

    # Coordenadas → WGS84
    try:
        E_wgs, N_wgs = to_wgs84(row["E_orig"], row["N_orig"], datum)
    except Exception:
        E_wgs, N_wgs = float(row["E_orig"]), float(row["N_orig"])

    # Cuenca: estandarizar nombre
    cuenca_raw = str(row.get("cuenca_raw", "")).strip()
    if "oro" in cuenca_raw.lower():
        cuenca = "Oro"
    elif "penitente" in cuenca_raw.lower():
        cuenca = "Penitente"
    elif "robalo" in cuenca_raw.lower() or "róbalo" in cuenca_raw.lower():
        cuenca = "Robalo"
    else:
        cuenca = cuenca_raw

    # Tipo de derecho
    tipo = str(row.get("tipo_derecho", "")).strip()
    subterranea = "subterr" in tipo.lower()

    # Profundidad (desde Observaciones o datos PDF)
    if cod in DATOS_PDF:
        prof   = DATOS_PDF[cod]["prof_m"]
        ne     = DATOS_PDF[cod]["ne_m"]
        nd     = DATOS_PDF[cod]["nd_m"]
        q_pdf  = DATOS_PDF[cod]["caudal_ls"]
        surge  = DATOS_PDF[cod]["surgente"]
        acuif_ini = DATOS_PDF[cod]["acuifero_ini"]
        acuif_fin = DATOS_PDF[cod]["acuifero_fin"]
        fuente = DATOS_PDF[cod]["fuente"]
        nombre = DATOS_PDF[cod]["nombre"]
        estrat_str = "; ".join(
            [f"{a:.1f}–{b:.1f}m: {d}" for a, b, d in DATOS_PDF[cod]["estrat"]]
        )
    else:
        prof   = parse_depth(obs)
        ne     = np.nan
        nd     = np.nan
        q_pdf  = np.nan
        surge  = is_surgente(obs)
        acuif_ini = np.nan
        acuif_fin = np.nan
        fuente = "Derechos_de_Agua.xlsx"
        nombre = ""
        estrat_str = ""

    # Caudal: preferir DDAA_subte si disponible
    q_xlsx = row.get("caudal_xlsx_ls", np.nan)
    q_sub  = q_dict.get(cod, np.nan)
    caudal = q_sub if pd.notna(q_sub) else (q_xlsx if pd.notna(q_xlsx) else q_pdf)

    # Volumen anual MEE (solo Oro, por código OB-)
    vol_mee = np.nan
    for k in mee_anual:
        # MEE tiene "Código Obra" (OB-1203-XX), no el ND- de DGA;
        # cruzar por coord aproximada si no hay código directo
        pass

    rec = {
        "codigo"      : cod,
        "nombre"      : nombre,
        "cuenca"      : cuenca,
        "tipo_derecho": tipo,
        "subterranea" : subterranea,
        "surgente"    : surge,
        "titular"     : str(row.get("titular", "")).strip(),
        "estado"      : str(row.get("estado", "")).strip(),
        "E_wgs84"     : E_wgs,
        "N_wgs84"     : N_wgs,
        "datum_orig"  : datum,
        "prof_m"      : prof,
        "ne_m"        : ne,
        "nd_m"        : nd,
        "caudal_ls"   : caudal,
        "acuifero_ini": acuif_ini,
        "acuifero_fin": acuif_fin,
        "estrat"      : estrat_str,
        "observaciones": obs,
        "expediente"  : str(row.get("expediente", "")).strip(),
        "fuente"      : fuente,
    }
    records.append(rec)

# ── Agregar Pozo La Invernada desde shapefile ──────────────────────────────
try:
    gdf_nuevo = gpd.read_file(POZO_SHP)
    for _, row in gdf_nuevo.iterrows():
        geom = row.geometry
        if geom is None:
            continue
        E_wgs, N_wgs = geom.x, geom.y
        # Asegurar EPSG:32719
        if gdf_nuevo.crs and gdf_nuevo.crs.to_epsg() != 32719:
            from pyproj import Transformer as Tr2
            txf = Tr2.from_crs(gdf_nuevo.crs.to_epsg(), 32719, always_xy=True)
            E_wgs, N_wgs = txf.transform(E_wgs, N_wgs)
        rec_nuevo = {
            "codigo"      : "INVERNADA-MON",
            "nombre"      : "Pozo La Invernada",
            "cuenca"      : "Penitente",
            "tipo_derecho": "Monitoreo",
            "subterranea" : True,
            "surgente"    : False,
            "titular"     : str(row.get("NOMBRE", row.get("nombre", ""))).strip(),
            "estado"      : "Monitoreo",
            "E_wgs84"     : round(E_wgs, 1),
            "N_wgs84"     : round(N_wgs, 1),
            "datum_orig"  : 1984,
            "prof_m"      : np.nan,
            "ne_m"        : np.nan,
            "nd_m"        : np.nan,
            "caudal_ls"   : np.nan,
            "acuifero_ini": np.nan,
            "acuifero_fin": np.nan,
            "estrat"      : "",
            "observaciones": "Pozo de monitoreo (pozo_nuevo.shp)",
            "expediente"  : "",
            "fuente"      : "pozo_nuevo.shp",
        }
        records.append(rec_nuevo)
    print(f"    → Pozo La Invernada agregado (pozo_nuevo.shp)")
except Exception as e:
    print(f"    ⚠ No se pudo leer pozo_nuevo.shp: {e}")

# ── Cruzar MEE por coordenadas (tolerancia 200 m) ─────────────────────────
# MEE solo tiene OB-codes; cruzar por (E, N) con tolerancia 200 m
mee_coords = []
for _, mrow in df_mee.iterrows():
    try:
        mN = float(str(mrow.get("UTM Norte", "")).replace(",", "."))
        mE = float(str(mrow.get("UTM Este",  "")).replace(",", "."))
        mvol = float(str(mrow.get("Volumen (m3/año)", "")).replace(",", "."))
        mcod = str(mrow.get("Código Obra", "")).strip()
        if mN > 0 and mE > 0:
            mee_coords.append((mN, mE, mvol, mcod))
    except (ValueError, TypeError):
        continue

MATCH_TOL = 200  # metros
for rec in records:
    for mN, mE, mvol, mcod in mee_coords:
        dN = abs(rec["N_wgs84"] - mN)
        dE = abs(rec["E_wgs84"] - mE)
        if dN < MATCH_TOL and dE < MATCH_TOL:
            rec["vol_mee_m3a"] = mvol
            rec["cod_mee"]     = mcod
            break
    else:
        rec.setdefault("vol_mee_m3a", np.nan)
        rec.setdefault("cod_mee", "")

# ── 5. EXPORTAR RESULTADOS ─────────────────────────────────────────────────
print(f"\n[5/5] Exportando resultados ({len(records)} pozos) ...")

df = pd.DataFrame(records)

# ── GeoJSON ────────────────────────────────────────────────────────────────
features = []
for _, row in df.iterrows():
    props = {k: (None if (isinstance(v, float) and np.isnan(v)) else v)
             for k, v in row.items() if k not in ("E_wgs84", "N_wgs84")}
    feat = {
        "type"      : "Feature",
        "geometry"  : {"type": "Point", "coordinates": [row["E_wgs84"], row["N_wgs84"]]},
        "properties": props,
    }
    features.append(feat)

geojson = {"type": "FeatureCollection",
           "crs" : {"type": "name",
                    "properties": {"name": "urn:ogc:def:crs:EPSG::32719"}},
           "features": features}

geojson_path = os.path.join(OUT_DIR, "pozos_acuifero.geojson")
with open(geojson_path, "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)
print(f"    → GeoJSON: {geojson_path}")

# ── CSV ────────────────────────────────────────────────────────────────────
csv_path = os.path.join(OUT_DIR, "pozos_acuifero.csv")
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"    → CSV:     {csv_path}")

# ── RESUMEN CONSOLA ──────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("RESUMEN DATASET POZOS")
print("=" * 65)
print(f"Total pozos/derechos : {len(df)}")
df_sub_only = df[df["subterranea"] == True]
print(f"Subterráneos         : {len(df_sub_only)}")
for c in ["Penitente", "Oro", "Robalo"]:
    n = len(df[df["cuenca"] == c])
    ns = len(df_sub_only[df_sub_only["cuenca"] == c])
    print(f"  {c:12s} : {n:3d} total, {ns:3d} subterráneos")

print(f"\nPozos con profundidad : {df['prof_m'].notna().sum()}")
print(f"  Penitente   rango: {df[df['cuenca']=='Penitente']['prof_m'].min():.0f}–{df[df['cuenca']=='Penitente']['prof_m'].max():.0f} m")
print(f"  El Oro      rango: {df[df['cuenca']=='Oro']['prof_m'].min():.0f}–{df[df['cuenca']=='Oro']['prof_m'].max():.0f} m")
print(f"Pozos surgentes       : {df['surgente'].sum()}")
print(f"Pozos con NE          : {df['ne_m'].notna().sum()}")
print(f"Pozos con Q bombeo    : {df['caudal_ls'].notna().sum()}")
print(f"Cruzados MEE          : {(df['vol_mee_m3a'].notna()).sum()}")

# ── FIGURAS ────────────────────────────────────────────────────────────────
COLORS = {"Penitente": "#1f77b4", "Oro": "#d62728", "Robalo": "#2ca02c", "": "#999"}

# ── Fig 1: Mapa distribución pozos ───────────────────────────────────────
fig1, ax1 = plt.subplots(figsize=(10, 8))
for cuenca, color in COLORS.items():
    mask = df["cuenca"] == cuenca
    sub  = df[mask]
    if len(sub) == 0:
        continue
    ax1.scatter(sub["E_wgs84"], sub["N_wgs84"],
                c=color, s=60, label=f"Cuenca {cuenca} (n={len(sub)})",
                edgecolors="k", linewidths=0.5, zorder=3, alpha=0.9)

# Anotar pozos con estratigrafía completa
for cod, info in DATOS_PDF.items():
    E, N = to_wgs84(info["E_orig"], info["N_orig"], info["datum"])
    ax1.annotate(cod.replace("ND-1202-", "").replace("ND-1203-", ""),
                 xy=(E, N), xytext=(6, 6), textcoords="offset points",
                 fontsize=7, color="navy", fontweight="bold")

# Pozo La Invernada
inv = df[df["codigo"] == "INVERNADA-MON"]
if len(inv):
    ax1.scatter(inv["E_wgs84"], inv["N_wgs84"],
                marker="^", c="orange", s=120, edgecolors="k",
                linewidths=0.8, zorder=4, label="Pozo monitoreo")

ax1.set_xlabel("Este UTM (m) — EPSG:32719", fontsize=9)
ax1.set_ylabel("Norte UTM (m)", fontsize=9)
ax1.set_title("Distribución de pozos – Cuencas Magallanes\n(WGS84 / UTM Zona 19S)", fontsize=10)
ax1.legend(fontsize=8, loc="lower right")
ax1.grid(True, ls="--", alpha=0.4)
ax1.ticklabel_format(style="plain", axis="both")
ax1.tick_params(labelsize=7)
plt.tight_layout()
fig1.savefig(os.path.join(FIG_DIR, "Fig10_01_Mapa_Pozos.png"), dpi=150)
plt.close(fig1)
print("\n    → Figura 1: mapa distribución pozos")

# ── Fig 2: Histograma profundidades por cuenca ────────────────────────────
fig2, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, cuenca in zip(axes, ["Penitente", "Oro"]):
    sub = df[(df["cuenca"] == cuenca) & df["prof_m"].notna()]["prof_m"]
    if len(sub) == 0:
        ax.set_visible(False)
        continue
    ax.hist(sub, bins=min(12, len(sub)), color=COLORS[cuenca],
            edgecolor="white", alpha=0.85)
    ax.axvline(sub.mean(),   color="k",    lw=1.5, ls="--", label=f"Media {sub.mean():.0f} m")
    ax.axvline(sub.median(), color="gray", lw=1.5, ls=":",  label=f"Mediana {sub.median():.0f} m")
    ax.set_xlabel("Profundidad (m)", fontsize=9)
    ax.set_ylabel("N° pozos", fontsize=9)
    ax.set_title(f"Profundidad pozos — Cuenca {cuenca}", fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", ls="--", alpha=0.4)

plt.tight_layout()
fig2.savefig(os.path.join(FIG_DIR, "Fig10_02_Histograma_Profundidades.png"), dpi=150)
plt.close(fig2)
print("    → Figura 2: histograma profundidades")

# ── Fig 3: Columnas estratigráficas (pozos con datos PDF) ────────────────
pozos_estrat = {k: v for k, v in DATOS_PDF.items() if v["estrat"]}
if pozos_estrat:
    ncols = len(pozos_estrat)
    fig3, axes3 = plt.subplots(1, ncols, figsize=(3 * ncols, 10), sharey=False)
    if ncols == 1:
        axes3 = [axes3]

    LITO_COLORS = {
        "Capa vegetal"         : "#8B4513",
        "Arcilla"              : "#DEB887",
        "Arena y grava"        : "#F4D03F",
        "Grava y piedra"       : "#AAB7B8",
        "Grava y arcilla"      : "#D5DBDB",
        "Roca"                 : "#716D6D",
    }
    def lito_color(desc):
        for k, v in LITO_COLORS.items():
            if k.lower() in desc.lower():
                return v
        return "#CCCCCC"

    for ax, (cod, info) in zip(axes3, pozos_estrat.items()):
        max_depth = info["prof_m"]
        for (z0, z1, desc) in info["estrat"]:
            h = z1 - z0
            fc = lito_color(desc)
            ec = "#E74C3C" if "ACUÍFERO" in desc else "black"
            lw = 2.0 if "ACUÍFERO" in desc else 0.5
            ax.bar(0.5, h, bottom=z0, width=0.8, color=fc, edgecolor=ec,
                   linewidth=lw, align="center")
            ax.text(0.5, z0 + h / 2, desc.replace(" [ACUÍFERO]", ""),
                    ha="center", va="center", fontsize=7, wrap=True)
        if info["ne_m"] is not np.nan and not (isinstance(info["ne_m"], float) and np.isnan(info["ne_m"])):
            ax.axhline(info["ne_m"], color="steelblue", lw=2, ls="--",
                       label=f"NE={info['ne_m']:.1f} m")
            ax.legend(fontsize=7, loc="lower right")
        ax.set_xlim(0, 1)
        ax.set_ylim(max_depth + 2, 0)
        ax.set_xticks([])
        ax.set_ylabel("Profundidad (m)", fontsize=8)
        cuenca_cod = info["cuenca"]
        ax.set_title(f"{cod}\n({info['nombre']})\nCuenca {cuenca_cod}",
                     fontsize=8, fontweight="bold")
        ax.grid(True, axis="y", ls="--", alpha=0.4)

    plt.suptitle("Columnas Estratigráficas – Pozos con datos de expediente",
                 fontsize=10, y=1.01)
    plt.tight_layout()
    fig3.savefig(os.path.join(FIG_DIR, "Fig10_03_Columnas_Estratigraficas.png"),
                 dpi=150, bbox_inches="tight")
    plt.close(fig3)
    print("    → Figura 3: columnas estratigráficas")

# ── Fig 4: Perfil E-W caudales y profundidades por cuenca ────────────────
fig4, axes4 = plt.subplots(2, 1, figsize=(12, 8))

for ax, cuenca in zip(axes4, ["Penitente", "Oro"]):
    sub = df[(df["cuenca"] == cuenca) & df["prof_m"].notna()].copy()
    sub = sub.sort_values("E_wgs84")
    if len(sub) == 0:
        continue
    sc = ax.scatter(sub["E_wgs84"], sub["prof_m"],
                    c=[COLORS[cuenca]] * len(sub), s=80,
                    edgecolors="k", linewidths=0.5, zorder=3)
    # Marcar surgentes
    surg = sub[sub["surgente"] == True]
    if len(surg):
        ax.scatter(surg["E_wgs84"], surg["prof_m"],
                   marker="*", c="gold", s=200, edgecolors="k",
                   linewidths=0.7, zorder=4, label="Surgente")
    # Anotar códigos cortos
    for _, r in sub.iterrows():
        short = str(r["codigo"]).replace("ND-1202-", "").replace("ND-1203-", "")
        ax.annotate(short, xy=(r["E_wgs84"], r["prof_m"]),
                    xytext=(4, 4), textcoords="offset points", fontsize=6)
    ax.invert_yaxis()
    ax.set_xlabel("Este UTM (m)", fontsize=9)
    ax.set_ylabel("Profundidad (m)", fontsize=9)
    ax.set_title(f"Profundidad vs posición E-O — Cuenca {cuenca}", fontsize=10)
    ax.grid(True, ls="--", alpha=0.4)
    ax.legend(fontsize=8)

plt.tight_layout()
fig4.savefig(os.path.join(FIG_DIR, "Fig10_04_Perfil_EO_Profundidades.png"), dpi=150)
plt.close(fig4)
print("    → Figura 4: perfil E-O profundidades")

# ── Fig 5: Boxplot profundidades por cuenca ───────────────────────────────
fig5, ax5 = plt.subplots(figsize=(7, 5))
cuencas_con_datos = [c for c in ["Penitente", "Oro"]
                     if df[(df["cuenca"] == c) & df["prof_m"].notna()].shape[0] > 0]
data_bp = [df[(df["cuenca"] == c) & df["prof_m"].notna()]["prof_m"].values
           for c in cuencas_con_datos]
bplot = ax5.boxplot(data_bp, labels=cuencas_con_datos, patch_artist=True,
                    medianprops={"color": "black", "linewidth": 2})
for patch, cuenca in zip(bplot["boxes"], cuencas_con_datos):
    patch.set_facecolor(COLORS[cuenca])
    patch.set_alpha(0.7)
ax5.set_ylabel("Profundidad del pozo (m)", fontsize=10)
ax5.set_title("Distribución de profundidades por cuenca", fontsize=11)
ax5.grid(True, axis="y", ls="--", alpha=0.4)
plt.tight_layout()
fig5.savefig(os.path.join(FIG_DIR, "Fig10_05_Boxplot_Profundidades.png"), dpi=150)
plt.close(fig5)
print("    → Figura 5: boxplot profundidades")

# ── RESUMEN ESTRATIGRÁFICO ─────────────────────────────────────────────────
print("\n" + "=" * 65)
print("ESTRATIGRAFÍA DETALLADA (pozos con expediente DGA)")
print("=" * 65)
for cod, info in DATOS_PDF.items():
    E, N = to_wgs84(info["E_orig"], info["N_orig"], info["datum"])
    print(f"\n  Pozo: {cod} — {info['nombre']} (Cuenca {info['cuenca']})")
    print(f"    Coord WGS84: E={E:.0f} N={N:.0f}")
    print(f"    Profundidad: {info['prof_m']} m | "
          f"NE: {info['ne_m']} m | ND: {info['nd_m']} m | "
          f"Q: {info['caudal_ls']} L/s | Surgente: {info['surgente']}")
    if info["estrat"]:
        print("    Estratigrafía:")
        for z0, z1, desc in info["estrat"]:
            tag = " ◄ ACUÍFERO" if "ACUÍFERO" in desc else ""
            print(f"      {z0:5.1f}–{z1:5.1f} m : {desc.replace(' [ACUÍFERO]','')} {tag}")
    if not np.isnan(info["acuifero_ini"]) if isinstance(info["acuifero_ini"], float) else True:
        if not (isinstance(info["acuifero_ini"], float) and np.isnan(info["acuifero_ini"])):
            print(f"    → Acuífero identificado: {info['acuifero_ini']}–{info['acuifero_fin']} m")

print("\n" + "=" * 65)
print("RESUMEN MEE (Extracciones Efectivas — El Oro)")
print("=" * 65)
mee_df2 = df[df["vol_mee_m3a"].notna() & (df["vol_mee_m3a"] > 0)]
if len(mee_df2):
    print(f"  Pozos cruzados: {len(mee_df2)}")
    tot_vol = mee_df2["vol_mee_m3a"].sum()
    print(f"  Volumen anual total (cruzado): {tot_vol:,.0f} m³/año = {tot_vol/1e6:.4f} Mm³/año")
else:
    print("  No se cruzaron pozos con datos MEE (verificar códigos de obra)")

print("\n" + "=" * 65)
print(f"ARCHIVOS GENERADOS:")
print(f"  {geojson_path}")
print(f"  {csv_path}")
print(f"  {FIG_DIR}/Fig10_0[1-5]_*.png")
print("=" * 65)
print("Script 10 completado exitosamente.")
