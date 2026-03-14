"""
Script 01: Extracción y sistematización de datos por cuenca
Proyecto: Análisis de Recursos Hídricos - Cuencas Magallanes (IDIEM/DGA)
Propósito: Extraer parámetros morfométricos, climáticos, hidrológicos y de demanda
           para cada cuenca de estudio, como insumo para los modelos conceptuales
           (Resolución Observaciones DGA N°6 y N°7)
Autor: Especialista Senior en Modelación
Fecha: 11-03-2026
"""

import os
import numpy as np
import shapefile
import json
from project_paths import BASE_DIR, PY_SCRIPTS_DIR, resolve_input

# -------------------------------------------------------------------
# RUTAS BASE
# -------------------------------------------------------------------
BASE_DIR = "/Users/carlosfloresarenas/Documents/Proyectos/Flores/IDIEM/01 Magallanes"
SIG_DIR  = os.path.join(BASE_DIR, "01 Etapa 1", "Anexos", "Anexo E - SIG", "04_Geodatabases")
OUT_DIR  = PY_SCRIPTS_DIR
os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------------------------
# 1. PARÁMETROS MORFOMÉTRICOS Y CLIMÁTICOS POR CUENCA
#    (sistematizados del Informe Etapa 1 y SIG disponible)
# -------------------------------------------------------------------

CUENCAS = {
    "Penitente": {
        "shapefile": resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/cuenca_rio_penitente.shp"),
        "red_hidro": resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/red_hidro_penitente.shp"),
        "nombre_completo": "Cuenca del Río Penitente",
        "codigo_BNA": "1221",
        "area_km2": 1750.41,
        "perim_km": 318.05,
        "elevacion_max_m": 1400,   # cota máxima aproximada (Informe E1, Cap. 2)
        "elevacion_min_m": 10,     # cota mínima (nivel mar/desembocadura Estrecho)
        "elevacion_media_m": 400,
        "pendiente_media_pct": 8.5,
        # Climáticos (PMETobs, Cap. 2.1, Informe E1)
        "PP_media_anual_mm": 120,   # BSk - semi-árido estepárico
        "T_media_anual_C": 8.0,
        "ETP_anual_mm": 450,        # Penman-Monteith estimado
        "ETR_anual_mm": 110,        # ETR ≈ PP (clima árido: P < ETP)
        "koppen": "BSk",
        "koppen_desc": "Clima semiárido frío de estepa",
        # Hidrológicos (Informe E1, Cap. 5.4 / estación DGA)
        "Q_medio_anual_m3s": 3.2,   # Río Penitente en Morro Chico
        "Q_especifico_Ls_km2": 1.8,
        "caudal_rendimiento_mm": 57, # Q anual en mm sobre área
        # Hidrogeológicos (Informe E1 Cap. 2.2.3 / SHAC)
        "shac": "SHAC Penitente",
        "tipo_acuifero": "Libre",
        "litologia_acuifero": "Gravas y arenas fluvioglaciales (Cuaternario)",
        "espesor_acuifero_m": (5, 25),  # rango estimado (PEGH 2021)
        "sustrato": "Fm. Loreto (Eoceno) - Lutitas y areniscas, baja permeabilidad",
        "profundidad_NBF_m": (2, 8),    # Nivel de agua freática
        "conductividad_hid_md": (5, 50),# K en m/d (estimado PEGH)
        "recarga_especifica_pct_pp": 8, # ~8% de PP → ~10 mm/año
        "recarga_mm_anual": 10,
        # Demanda (Informe E1, Cap. 5.3)
        "demanda_total_Ls": 28.5,       # total DAA otorgados
        "demanda_consumo_humano_Ls": 2.1,
        "demanda_ganaderia_Ls": 26.4,
        "DAA_subterraneo_Ls": 2.3,
        # Red hídrica
        "longitud_cauce_principal_km": 95.0,
        "orden_maximo_strahler": 4,
        "cuerpos_lacustres_n": 6,
        "area_lacustre_km2": 3.2,
        # Glaciares
        "glaciares_presencia": False,
        # Estaciones de monitoreo
        "estaciones_fluviometricas": ["Penitente en Morro Chico (12700002-4)"],
        "estaciones_meteorologicas": ["Morro Chico-DGA"],
    },
    "El Oro": {
        "shapefile": resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/cuenca_rio_del_oro.shp"),
        "red_hidro": resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/red_hidro_oro.shp"),
        "nombre_completo": "Cuenca del Río El Oro",
        "codigo_BNA": "1281",
        "area_km2": 706.8,
        "perim_km": 263.97,
        "elevacion_max_m": 800,
        "elevacion_min_m": 20,
        "elevacion_media_m": 250,
        "pendiente_media_pct": 12.0,
        # Climáticos
        "PP_media_anual_mm": 900,   # Csc - mediterráneo frío lluvioso
        "T_media_anual_C": 6.0,
        "ETP_anual_mm": 380,
        "ETR_anual_mm": 380,        # ETR ≈ ETP (P >> ETP)
        "koppen": "Csc",
        "koppen_desc": "Clima mediterráneo frío de lluvia invernal",
        # Hidrológicos
        "Q_medio_anual_m3s": 10.5,  # Río Oro en Bahía San Felipe
        "Q_especifico_Ls_km2": 14.9,
        "caudal_rendimiento_mm": 468,
        # Hidrogeológicos
        "shac": "SHAC Río Oro",
        "tipo_acuifero": "Libre",
        "litologia_acuifero": "Gravas y arenas glaciofluviales (Cuaternario TF)",
        "espesor_acuifero_m": (5, 30),
        "sustrato": "Fm. Latorre / Complejo Tobífera - Rocas metamórficas e ígneas",
        "profundidad_NBF_m": (1, 6),
        "conductividad_hid_md": (8, 80),
        "recarga_especifica_pct_pp": 12,  # ~12% de PP
        "recarga_mm_anual": 108,
        # Demanda
        "demanda_total_Ls": 45.2,
        "demanda_consumo_humano_Ls": 3.5,
        "demanda_ganaderia_Ls": 41.7,
        "DAA_subterraneo_Ls": 4.1,
        # Red hídrica
        "longitud_cauce_principal_km": 76.4,
        "orden_maximo_strahler": 4,
        "cuerpos_lacustres_n": 8,
        "area_lacustre_km2": 12.5,
        # Glaciares
        "glaciares_presencia": True,
        "glaciares_area_km2": 2.1,
        # Estaciones
        "estaciones_fluviometricas": ["Oro en Bahía San Felipe (12800002-K)"],
        "estaciones_meteorologicas": ["Vicuña-DGA (TDF)"],
    },
    "Robalo": {
        "shapefile": resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/cuenca_rio_robalo.shp"),
        "red_hidro": resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/red_hidro_robalo.shp"),
        "nombre_completo": "Cuenca del Río Róbalo",
        "codigo_BNA": "1280",
        "area_km2": 22.0,
        "perim_km": 24.07,
        "elevacion_max_m": 510,    # Cerro Bandera ~509 m
        "elevacion_min_m": 50,
        "elevacion_media_m": 250,
        "pendiente_media_pct": 38.0, # cuenca muy abrupta, montañosa
        # Climáticos
        "PP_media_anual_mm": 700,   # ET - clima de tundra
        "T_media_anual_C": 4.0,
        "ETP_anual_mm": 280,
        "ETR_anual_mm": 280,
        "koppen": "ET",
        "koppen_desc": "Clima de tundra",
        # Hidrológicos
        "Q_medio_anual_m3s": 0.45,  # Río Róbalo en Puerto Williams
        "Q_especifico_Ls_km2": 20.5,
        "caudal_rendimiento_mm": 646,
        # Hidrogeológicos
        "shac": "SHAC Puerto Williams",
        "tipo_acuifero": "Fisurado/Limitado",
        "litologia_acuifero": "Roca fisurada (Complejo granítico - Batolito H. Moreno)",
        "espesor_acuifero_m": (0, 5),    # mínimo - roca aflorante dominante
        "sustrato": "Batolito Hornos-Moreno - Granitos y granodioritas (Paleozoico)",
        "profundidad_NBF_m": (0, 2),
        "conductividad_hid_md": (0.1, 5),  # muy baja en roca fisurada
        "recarga_especifica_pct_pp": 5,
        "recarga_mm_anual": 35,
        # Demanda
        "demanda_total_Ls": 12.0,         # Puerto Williams ~3,000 hab
        "demanda_consumo_humano_Ls": 12.0, # toda la demanda = AP urbano
        "demanda_ganaderia_Ls": 0.0,
        "DAA_subterraneo_Ls": 0.0,
        # Red hídrica
        "longitud_cauce_principal_km": 3.65,
        "orden_maximo_strahler": 2,
        "cuerpos_lacustres_n": 2,
        "area_lacustre_km2": 0.3,
        # Glaciares
        "glaciares_presencia": False,
        # Estaciones
        "estaciones_fluviometricas": ["Róbalo en Puerto Williams (12200001-9)"],
        "estaciones_meteorologicas": ["Puerto Williams-DMC", "Puerto Williams-DGA"],
    },
}

# -------------------------------------------------------------------
# 2. CALCULAR PARÁMETROS DERIVADOS
# -------------------------------------------------------------------

def calcular_parametros_derivados(c: dict) -> dict:
    """Calcula parámetros adicionales del balance hídrico."""
    # Factor de forma Gravelius (Kc = P / (2*sqrt(π*A)))
    Kc = c["perim_km"] / (2 * np.sqrt(np.pi * c["area_km2"]))
    c["factor_forma_Kc"] = round(Kc, 3)

    # Tiempo de concentración estimado (Kirpich adaptado para cuencas naturales)
    L = c["longitud_cauce_principal_km"]
    S = c["pendiente_media_pct"] / 100
    Tc_h = 0.0195 * (L * 1000) ** 0.77 * S ** (-0.385) / 3600
    c["tiempo_concentracion_h"] = round(Tc_h, 2)

    # Coeficiente de escorrentía anual
    Q_mm = c["caudal_rendimiento_mm"]
    P_mm = c["PP_media_anual_mm"]
    if P_mm > 0:
        c["coeficiente_escorrentia"] = round(Q_mm / P_mm, 3)
    else:
        c["coeficiente_escorrentia"] = 0

    # Balance hídrico simplificado (mm/año)
    c["balance_hidrico_mm"] = {
        "P": c["PP_media_anual_mm"],
        "ETR": c["ETR_anual_mm"],
        "Q_sup": c["caudal_rendimiento_mm"],
        "Recarga_sbt": c["recarga_mm_anual"],
        "Cierre_balance": c["PP_media_anual_mm"] - c["ETR_anual_mm"] -
                          c["caudal_rendimiento_mm"] - c["recarga_mm_anual"],
    }
    return c

# Aplicar cálculos
for nombre, cuenca in CUENCAS.items():
    CUENCAS[nombre] = calcular_parametros_derivados(cuenca)

# -------------------------------------------------------------------
# 3. LEER GEOMETRÍAS DE LOS SHAPEFILES (longitud de red hídrica)
# -------------------------------------------------------------------

def leer_red_hidrica(shp_path: str) -> dict:
    """Lee red hídrica y extrae estadísticas de longitud."""
    resultado = {"longitud_total_km": 0, "n_tramos": 0, "tipos": {}}
    if not os.path.exists(shp_path):
        return resultado
    try:
        sf = shapefile.Reader(shp_path)
        fields = [f[0] for f in sf.fields[1:]]
        for rec in sf.records():
            rec_dict = dict(zip(fields, rec))
            long_km = rec_dict.get("LONG_KM", 0) or 0
            tipo = rec_dict.get("TIPO", "SN")
            resultado["longitud_total_km"] += long_km
            resultado["n_tramos"] += 1
            resultado["tipos"][tipo] = resultado["tipos"].get(tipo, 0) + long_km
        resultado["longitud_total_km"] = round(resultado["longitud_total_km"], 2)
    except Exception as e:
        print(f"  Advertencia al leer {shp_path}: {e}")
    return resultado

print("\n" + "="*70)
print("EXTRACCIÓN DE DATOS POR CUENCA - MAGALLANES")
print("Observaciones DGA N°6 y N°7 - Modelos Conceptuales por Cuenca")
print("="*70)

resultados_red = {}
for nombre, cuenca in CUENCAS.items():
    red = leer_red_hidrica(cuenca["red_hidro"])
    resultados_red[nombre] = red
    CUENCAS[nombre]["red_hidrica_stats"] = red

# -------------------------------------------------------------------
# 4. LEER MASAS LACUSTRES POR CUENCA
# -------------------------------------------------------------------

shp_lagos = resolve_input("01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/hidro_masas_lacustres.shp")
lagos_por_cuenca = {"Penitente": [], "El Oro": [], "Robalo": []}

if os.path.exists(shp_lagos):
    sf = shapefile.Reader(shp_lagos)
    fields = [f[0] for f in sf.fields[1:]]
    for rec in sf.records():
        rd = dict(zip(fields, rec))
        layer = rd.get("layer", "")
        nombre_lago = rd.get("NOMBRE", "SN")
        area = rd.get("AREA_KM2", 0)
        if "penitente" in layer.lower():
            lagos_por_cuenca["Penitente"].append({"nombre": nombre_lago, "area_km2": area})
        elif "oro" in layer.lower():
            lagos_por_cuenca["El Oro"].append({"nombre": nombre_lago, "area_km2": area})
        elif "robalo" in layer.lower():
            lagos_por_cuenca["Robalo"].append({"nombre": nombre_lago, "area_km2": area})

for nombre in CUENCAS:
    CUENCAS[nombre]["lagos"] = lagos_por_cuenca.get(nombre, [])

# -------------------------------------------------------------------
# 5. IMPRIMIR RESUMEN POR CUENCA
# -------------------------------------------------------------------

for nombre, c in CUENCAS.items():
    print(f"\n{'─'*60}")
    print(f"  CUENCA: {c['nombre_completo'].upper()}")
    print(f"{'─'*60}")
    print(f"  Código BNA:          {c['codigo_BNA']}")
    print(f"  Área:                {c['area_km2']:,.1f} km²")
    print(f"  Perímetro:           {c['perim_km']:.1f} km")
    print(f"  Factor forma (Kc):   {c['factor_forma_Kc']:.3f}")
    print(f"  Elevación máx/min:   {c['elevacion_max_m']}/{c['elevacion_min_m']} m.s.n.m.")
    print(f"  Elevación media:     {c['elevacion_media_m']} m.s.n.m.")
    print(f"  Pendiente media:     {c['pendiente_media_pct']:.1f}%")
    print(f"  Tc estimado:         {c['tiempo_concentracion_h']:.1f} h")
    print(f"\n  CLIMA ({c['koppen']}): {c['koppen_desc']}")
    print(f"  PP anual:            {c['PP_media_anual_mm']} mm/año")
    print(f"  T media:             {c['T_media_anual_C']} °C")
    print(f"  ETP:                 {c['ETP_anual_mm']} mm/año")
    print(f"  ETR:                 {c['ETR_anual_mm']} mm/año")
    print(f"\n  HIDROLOGÍA:")
    print(f"  Q medio anual:       {c['Q_medio_anual_m3s']} m³/s")
    print(f"  Rendimiento hídrico: {c['Q_especifico_Ls_km2']:.1f} L/s/km²")
    print(f"  Coef. escorrentía:   {c['coeficiente_escorrentia']:.3f}")
    bh = c["balance_hidrico_mm"]
    print(f"\n  BALANCE HÍDRICO (mm/año):")
    print(f"    P   = {bh['P']:6.0f} mm")
    print(f"    ETR = {bh['ETR']:6.0f} mm  ({bh['ETR']/bh['P']*100:.0f}% de P)")
    print(f"    Q   = {bh['Q_sup']:6.0f} mm  ({bh['Q_sup']/bh['P']*100:.0f}% de P)")
    print(f"    Rec = {bh['Recarga_sbt']:6.0f} mm  ({bh['Recarga_sbt']/bh['P']*100:.0f}% de P)")
    print(f"    ΔS  = {bh['Cierre_balance']:6.0f} mm  (cierre balance)")
    print(f"\n  HIDROGEOLOGÍA:")
    print(f"  SHAC:                {c['shac']}")
    print(f"  Tipo acuífero:       {c['tipo_acuifero']}")
    print(f"  Litología acuífero:  {c['litologia_acuifero']}")
    print(f"  Espesor acuífero:    {c['espesor_acuifero_m'][0]}-{c['espesor_acuifero_m'][1]} m")
    print(f"  Recarga estimada:    {c['recarga_mm_anual']} mm/año ({c['recarga_especifica_pct_pp']}% de P)")
    print(f"\n  DEMANDA:")
    print(f"  Demanda total:       {c['demanda_total_Ls']:.1f} L/s")
    print(f"  Consumo humano:      {c['demanda_consumo_humano_Ls']:.1f} L/s")
    print(f"  Ganadería/riego:     {c['demanda_ganaderia_Ls']:.1f} L/s")
    print(f"  DAA subterráneo:     {c['DAA_subterraneo_Ls']:.1f} L/s")
    print(f"\n  RED HÍDRICA:")
    red = c.get("red_hidrica_stats", {})
    print(f"  N° tramos:           {red.get('n_tramos', '?')}")
    print(f"  Longitud total:      {red.get('longitud_total_km', '?')} km")
    tipos = red.get("tipos", {})
    for tipo, lon in tipos.items():
        print(f"    {tipo}: {lon:.1f} km")
    print(f"\n  CUERPOS LACUSTRES:")
    for lago in c.get("lagos", []):
        print(f"    {lago['nombre']}: {lago['area_km2']:.2f} km²")

# -------------------------------------------------------------------
# 6. GUARDAR DATOS EN JSON (para usar en Scripts 02 y 03)
# -------------------------------------------------------------------

# Convertir tuplas a listas para serialización JSON
def prepare_for_json(obj):
    if isinstance(obj, tuple):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: prepare_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [prepare_for_json(i) for i in obj]
    elif isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    return obj

output_json = os.path.join(OUT_DIR, "datos_cuencas.json")
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(prepare_for_json(CUENCAS), f, ensure_ascii=False, indent=2)

print(f"\n{'='*70}")
print(f"✓ Datos guardados en: {output_json}")
print(f"{'='*70}")
print("\nACCIÓN SIGUIENTE: Ejecutar script 02_modelo_conceptual_subterraneo.py")
