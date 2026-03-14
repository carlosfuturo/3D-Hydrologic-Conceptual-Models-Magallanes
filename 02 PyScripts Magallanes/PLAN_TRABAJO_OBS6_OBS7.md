# Plan de Trabajo — Resolución Observaciones DGA N°6 y N°7
## Estudio: Análisis de Recursos Hídricos Subterráneos en Cuencas de la Región de Magallanes y de la Antártica Chilena
**Fecha elaboración:** 11 de marzo de 2026  
**Plazo entrega informe corregido:** 19 de marzo de 2026  
**Responsable:** Especialista Senior en Modelación  

---

## 1. DIAGNÓSTICO DEL PROBLEMA

### Observación DGA N°6 (Observaciones Generales, Sección 5.1.1)
> *"Realizar el modelo conceptual subterráneo preliminar para cada una de las cuencas de estudio por separado, indicando la información local de cada una, esquematizando el balance hídrico a escala y con el software apropiado para ello."*

**Problema identificado en Informe E1:**  
La sección 5.1.1 presenta un único modelo conceptual subterráneo de carácter genérico para las tres cuencas en conjunto, basado en la estructura PEGH (estudios regionales DGA de dominios mucho más extensos). No se individualiza la hidrogeología específica de cada cuenca; el balance no está esquematizado a escala local; no se identifica con precisión las zonas de recarga/descarga ni la geometría del relleno cuaternario por cuenca.  
Además, la Obs. de Contenido N°24 (p.159) reitera que se deben *"eliminar mapas que no entreguen información específica al estudio"* (refiriéndose a los mapas de dominios de PEGH que cubren áreas regionales ajenas al estudio).

### Observación DGA N°7 (Observaciones Generales, Sección 5.1.2)
> *"Realizar el modelo conceptual superficial preliminar para cada una de las cuencas de estudio por separado, indicando la información local de cada una, esquematizando el balance hídrico a escala y con el software apropiado para ello."*

**Problema identificado en Informe E1:**  
La sección 5.1.2 presenta un solo diagrama esquemático general para las tres cuencas (Figura 84). No se distinguen ni detallan los elementos locales de cada cuenca (subcatchments internos, puntos de demanda específicos, cuerpos lacustres, interacción río-acuífero por cuenca). La Obs. de Contenido N°25 (p.167) lo reitera.

### Requerimiento de las Bases DGA (Letra F, Etapa I):
> *"El modelo conceptual tanto preliminar como final deberá compilarse en un capítulo descriptivo y de forma gráfica en 3D en un software apropiado... Se considerará adecuada la generación de esquemas o dibujos gráficos de las cuencas de estudio que permitan robustecer la conceptualización hidrogeológica."*

---

## 2. INFORMACIÓN DISPONIBLE - DIAGNÓSTICO DE UTILIDAD

### 2.1 Shapefiles (Anexo E - SIG)
| Archivo | Cuencas | Utilidad |
|---|---|---|
| `cuenca_rio_penitente.shp` | Penitente | ALTA - Límite exacto, área 1750.41 km² |
| `cuenca_rio_del_oro.shp` | El Oro | ALTA - Límite exacto, área 706.8 km² |
| `cuenca_rio_robalo.shp` | Róbalo | ALTA - Límite exacto, área 22.0 km² |
| `red_hidro_penitente.shp` | Penitente | ALTA - Red hídrica: ríos, esteros (37 tramos) |
| `red_hidro_oro.shp` | El Oro | ALTA - Red hídrica (6 tramos) |
| `red_hidro_robalo.shp` | Róbalo | ALTA - Red hídrica (1 tramo, 3.65 km) |
| `hidro_masas_lacustres.shp` | Todas | ALTA - Cuerpos lacustres (17 registros) |
| `hidro_clima_koppen.shp` | Todas | MEDIA - Clasificación climática por cuenca |
| `Fluviometricas.shp` (DGA) | Todas | ALTA - Estaciones fluviométricas |
| `Meteorologicas.shp` (DGA) | Todas | ALTA - Estaciones meteorológicas |
| `Calidad_de_Aguas.shp` (DGA) | Todas | MEDIA - Puntos calidad de agua |
| `Cuencas_BNA.shp`, `SubCuencas_BNA.shp`, `SubSubCuencas_BNA.shp` (DGA) | Todas | ALTA - Subcuencas BNA para subdivisión interna |
| **`propsBOT_Vertientes_Proj.shp`** (03 SIG Magallanes) | **Penitente** | **ALTA — Elevación base acuífero (campo `Bottom1`, m.s.n.m.); 2,714 pts totales, 2,714 dentro de cuenca, grilla 300 m** |
| **`propsBOT_Fuego_Proj.shp`** (03 SIG Magallanes) | **El Oro** | **ALTA — Elevación base acuífero (campo `Bottom1`, m.s.n.m.); 97,765 pts totales, 3,378 dentro de cuenca, grilla 300 m** |

### 2.2 DEMs y Rasters (Anexo E - 05_Raster)
| Archivo | Utilidad |
|---|---|
| `EZ_DEM_penitente.shp`, `EZ_DEM_oro.shp`, `EZ_DEM_robalo.shp` | ALTA - Datos de elevación para perfiles y sección transversal |
| `EZ_slope_penitente.shp`, `EZ_slope_oro.shp`, `EZ_slope_robalo.shp` | ALTA - Pendientes por cuenca |

### 2.3 Otras capas (06_Otras)
| Archivo | Utilidad |
|---|---|
| `Basins_PMETobs.shp` | ALTA - Cuencas PMETobs para precipitación espacializada |
| `INV_PG_2022_v2.shp` | ALTA - Inventario de glaciares (componente criófera) |
| `Hitos_2023_Actualizado.shp` | MEDIA - Hitos limítrofes |

### 2.4 Imágenes modelo conceptual (Anexo B)
| Archivo | Diagnóstico |
|---|---|
| `modelo_coneptual_subterraneo.png` | BASE EXISTENTE - Versión genérica a mejorar por cuenca |
| `modelo_conceptual_superficial.png` | BASE EXISTENTE - Versión genérica a mejorar por cuenca |
| `diagrama_esquematico_tres_cuencas.png` | BASE - Diagrama WEAP genérico a reemplazar |
| Perfiles estratigráficos (x3) | ALTA - Información litológica específica por sector |
| `mapa_hidrogeologico_oro.png` | ALTA - Hidrogeología Cuenca del Oro |
| `mapa_hidrogeologico_2.png` | ALTA - Hidrogeología otra cuenca |
| `modelo_hidrogeologico_3d_1.png` | ALTA - Existe modelo 3D previo a mejorar |
| `modelo_hidrogeologico_rio_penitente.png` | ALTA - Modelo específico Penitente (base) |

### 2.5 Datos del Informe Etapa 1
| Datos | Cuenca | Utilidad |
|---|---|---|
| Área, perímetro, morphometría | Todas | ALTA - Para balance a escala |
| Clima: PP, T, clasificación Koppen | Todas | ALTA - Entradas del balance |
| Caudales (series diarias, promedios mensuales) | Todas | ALTA - Calibración conceptual |
| Perfiles estratigráficos (Tablas 4 y 5) | Penitente/Oro | ALTA - Unidades litológicas |
| SHAC identificados | Penitente/Oro/Róbalo | ALTA - Acuíferos reconocidos |
| DAA subterráneos y superficiales | Todas | ALTA - Demanda por cuenca |
| Demanda consumo humano | Todas | ALTA - Nodos de demanda |
| Geofísica disponible | Todas | ALTA - Profundidad del relleno |

---

## 3. PLAN DE TRABAJO

### FASE 1: Extracción y sistematización de datos por cuenca (Día 1-2)
**Script 01:** `01_extraccion_datos_cuencas.py`
- Calcular morfometría específica por cuenca (área, altimetría media, pendiente media)
- Extraer parámetros climáticos por cuenca (PP media anual, T media, ET estimada)
- Sistematizar datos de demanda (DAA, consumo humano, uso agrícola) por cuenca
- Inventariar nodos hidrológicos (estaciones, SHAC, pozos, bocatomas)

### FASE 2: Modelo Conceptual Subterráneo por Cuenca (Día 2-4)
**Script 02:** `02_modelo_conceptual_subterraneo.py`

**Para cada cuenca, generar:**
1. **Sección transversal esquemática 3D**: perfil valle-ladera mostrando:
   - Basamento rocoso (sustrato impermeable)
   - Relleno cuaternario (acuífero libre)
   - Tabla de agua (nivel freático)
   - Zonas de recarga (precipitación, infiltración)
   - Zonas de descarga (afloramientos, ríos, extracciones)
   - Dirección de flujo subterráneo

2. **Diagrama de balance subterráneo a escala**: con flujos estimados:
   - Entradas: Recarga por precipitación (R_prec), Recarga lateral (R_lat), Interacción río-acuífero (+)
   - Salidas: Afloramientos base flow (Q_base), Extracciones/bombeo (Q_ext), Interacción río-acuífero (-)
   - ΔAlmacenamiento = Entradas - Salidas

**Parámetros específicos por cuenca:**
- **Río Penitente**: SHAC activo, relleno cuaternario Pampa estepárica, PP~120 mm/año (BSk), área 1750 km²
- **Río El Oro**: SHAC reconocido, relleno cuaternario TDF, PP~900 mm/año (Csc), área 707 km²  
- **Río Róbalo**: Cuenca pequeña 22 km², sustrato rocoso expuesto, PP~700 mm/año (ET-tundra), abastecimiento Puerto Williams

### FASE 3: Modelo Conceptual Superficial por Cuenca (Día 3-5)
**Script 03:** `03_modelo_conceptual_superficial.py`

**Para cada cuenca, generar:**
1. **Diagrama de nodos WEAP-style**: mostrando
   - Catchments/subcuencas de generación de escorrentía (subdivisión BNA)
   - Nodos de almacenamiento: lagunas, embalses
   - Tramos de río con numeración
   - Nodos de demanda: consumo humano, ganadería, riego
   - Conexión superficial-subterránea (percolación → acuífero)
   - Punto de cierre / salida de la cuenca

2. **Balance hídrico superficial esquemático a escala** con valores indicativos:
   - P (precipitación), ET (evapotranspiración), Q (caudal medido), ΔS
   - Entradas vs. salidas

### FASE 4: Integración y generación de figuras finales (Día 5-6)
**Script 04:** `04_balance_hidrico_cuencas.py`
- Calcular balance hídrico anual por cuenca (P - ET - Q = ΔS)
- Verificar cierre del balance con datos disponibles
- Generar tabla comparativa de parámetros de balance para las 3 cuencas

### FASE 5: Documentación y texto del informe (Día 6-7)
**Script 05:** `05_texto_observaciones_67.py`
- Generar texto Markdown/Word con:
  - Nueva sección 5.1.1 (Modelo Conceptual Subterráneo - una subsección por cuenca)
  - Nueva sección 5.1.2 (Modelo Conceptual Superficial - una subsección por cuenca)
  - Referencias a figuras generadas
  - Pie de página software utilizado

### FASE 6: Visualización 3D estilo Leapfrog (completada 12-Mar-2026)
**Script 07:** `07_mapa_3d_leapfrog.py`
- Genera figuras 3D interactivas (HTML Plotly) y estáticas (PNG) por cuenca + combinada.
- **Base del acuífero:** fuente primaria = `propsBOT_{Vertientes,Fuego}_Proj.shp` (campo `Bottom1` en m.s.n.m.), interpolación lineal sobre grilla DEM 30m.
- **Enmascarado de áreas sin dato:** puntos filtrados con buffer configurable por cuenca (`bot_buffer`); luego máscara `cKDTree` distancia máxima (1.5× espaciado de grilla = 450 m), eliminando triángulos vacíos en zonas de roca sin acuífero.
- **Fallback:** para Róbalo (sin shp BOT): gaussiano derivado de Fig. 75 PEGH DGA 2021.
- **Pozos de bombeo (12-Mar-2026):** integración de `pozos_acuifero.csv` (campo `subterranea==True`). Cada pozo se visualiza como marcador diamante verde (`#00e676`) a +15 m sobre el terreno; los sondajes con `prof_m` conocida muestran una línea vertical verde desde la superficie hasta la profundidad del pozo. Tooltip: código, caudal (l/s), profundidad, elevación terreno.
- **Red hidrológica con hover (12-Mar-2026):** `_drape_river_coords()` retorna texto de hover con el campo `NOMBRE` de cada segmento de río; al pasar el cursor sobre cualquier tramo aparece el nombre del cauce.
- **Resultados (12-Mar-2026):**

| Cuenca | Fuente base | Puntos usados | Celdas con dato | Bottom1 rango | Pozos subterr. |
|---|---|---|---|---|---|
| Penitente | `propsBOT_Vertientes_Proj.shp` | 4,501 (buf 2,400 m) | 619 / 5,280 | 77–277 m.s.n.m. | 15 (8 con prof) |
| El Oro | `propsBOT_Fuego_Proj.shp` | 3,634 (buf 1,200 m) | 499 / 2,590 | −225–211 m.s.n.m. | 17 (13 con prof) |
| Róbalo | Gaussiano (Fig. 75 PEGH) | — | — | — | 0 |

---

## 4. SOFTWARE PROPUESTO

Según las Bases DGA (Letra F): *"El modelo conceptual... de forma gráfica en 3D en un software apropiado"*

**Software seleccionado para el modelo conceptual preliminar:**
- **Python 3.x** con:
  - `matplotlib` (2D/3D schematic diagrams — código abierto, replicable)
  - `mpl_toolkits.mplot3d` (vistas 3D de perfiles)
  - `geopandas` + `pyshp` (procesamiento de datos SIG)
  - `networkx` (diagramas de nodos para balance superficial)
  - `plotly` (diagramas interactivos 3D opcionales)
- **QGIS** (mapas base por cuenca, vinculación con shapes del Anexo E)

**Justificación:** Software de código abierto, sin licencia, que garantiza la replicabilidad y entrega de scripts al mandante (DGA). Cumple el requerimiento de registro de procesos en "archivos digitales y formatos originales, claros y autosustentables" (Bases DGA, Letra F, Etapa V).

---

## 5. PRODUCTOS ENTREGABLES

| N° | Producto | Tipo | Sección informe |
|---|---|---|---|
| 1 | Modelo conceptual subterráneo - Río Penitente | Figura (PNG/PDF) | 5.1.1 |
| 2 | Modelo conceptual subterráneo - Río El Oro | Figura (PNG/PDF) | 5.1.1 |
| 3 | Modelo conceptual subterráneo - Río Róbalo | Figura (PNG/PDF) | 5.1.1 |
| 4 | Diagrama balance hídrico subterráneo - Río Penitente | Figura (PNG/PDF) | 5.1.1 |
| 5 | Diagrama balance hídrico subterráneo - Río El Oro | Figura (PNG/PDF) | 5.1.1 |
| 6 | Diagrama balance hídrico subterráneo - Río Róbalo | Figura (PNG/PDF) | 5.1.1 |
| 7 | Modelo conceptual superficial (nodos) - Río Penitente | Figura (PNG/PDF) | 5.1.2 |
| 8 | Modelo conceptual superficial (nodos) - Río El Oro | Figura (PNG/PDF) | 5.1.2 |
| 9 | Modelo conceptual superficial (nodos) - Río Róbalo | Figura (PNG/PDF) | 5.1.2 |
| 10 | Balance hídrico cuantitativo comparativo | Tabla | 5.1.1/5.1.2 |
| 11 | Scripts Python (código fuente documentado) | .py | Anexo F |
| 12 | Texto secciones 5.1.1 y 5.1.2 corregido | docx | Informe E1 rev. |
| **13** | **Modelo 3D interactivo base acuífero — Río Penitente** | **HTML + PNG** | **5.1.1** |
| **14** | **Modelo 3D interactivo base acuífero — Río El Oro** | **HTML + PNG** | **5.1.1** |
| **15** | **Modelo 3D interactivo base acuífero — Río Róbalo** | **HTML + PNG** | **5.1.1** |
| **16** | **Modelo 3D combinado 3 cuencas** | **HTML** | **5.1.1** |
| **17** | **Pozos de bombeo integrados en figura 3D (marcadores verdes + sondajes)** | **HTML** | **5.1.1** |
| **18** | **Hover interactivo red hidrológica (NOMBRE cauce)** | **HTML** | **5.1.1** |

---

## 6. CRONOGRAMA

| Día | Actividad | Entregable |
|---|---|---|
| 11 Mar (hoy) | Diagnóstico, plan, extracción datos | Plan de trabajo + Script 01 |
| 12 Mar | Modelo subterráneo Penitente + El Oro | Scripts 02a, Figuras 1-4 |
| 13 Mar | Modelo subterráneo Róbalo + ajustes | Script 02b, Figuras 5-6 |
| 14 Mar | Modelo superficial Penitente + El Oro | Script 03a, Figuras 7-10 |
| 17 Mar | Modelo superficial Róbalo + balance integrado | Script 03b+04, Figuras 11-12 |
| 18 Mar | Texto informe + revisión interna | Script 05, texto |
| 19 Mar | Entrega DGA | Informe E1 corregido |

---

## 7. NOTAS TÉCNICAS

### Cuenca Río Penitente
- **Área:** 1,750.41 km² | **Clima:** BSk (semi-árido estepárico) | PP media: ~120 mm/año
- **SHAC:** SHAC Penitente (yacimiento en relleno cuaternario de pampa)
- **Acuífero:** Libre en relleno cuaternario (gravas, arenas); sustrato Fm. Loreto (impermeable rel.)
- **Estación control:** Río Penitente en Morro Chico
- **Desafío:** Cuenca semi-árida → recarga baja, eficiencia de recarga ~5-10% PP; demanda ganadera significativa

### Cuenca Río El Oro
- **Área:** 706.8 km² | **Clima:** Csc (mediterráneo frío) | PP media: ~900 mm/año
- **SHAC:** SHAC Río Oro reconocido
- **Acuífero:** Libre en relleno cuaternario (Fm. cuaternarias glaciofluviales)
- **Estación control:** Río Oro en Bahía San Felipe (Tierra del Fuego)
- **Desafío:** alta PP pero descarga rápida; geología compleja Tierra del Fuego

### Cuenca Río Róbalo
- **Área:** 22 km² | **Clima:** ET (tundra) | PP media: ~700 mm/año
- **Abastecimiento urbano:** Puerto Williams (único suministro de agua potable)
- **Acuífero:** Limitado → cuenca pequeña, roca expuesta predominante
- **Estación control:** Río Róbalo en Puerto Williams
- **Desafío:** Cuenca crítica por uso AP; riesgo cambio climático (retroceso glaciar?)

---

## 8. GUÍA DE SCRIPTS DEL PROYECTO (ESPECÍFICA MAGALLANES)

Este bloque resume, en formato operativo, el ecosistema de scripts de `02 PyScripts Magallanes` para la resolución de las Observaciones DGA N°6 y N°7 y la generación de productos gráficos/técnicos del estudio.

### 8.1 Estructura funcional del flujo

Aunque los scripts están en un único directorio, el flujo real de trabajo se organiza en 4 capas:

```text
02 PyScripts Magallanes/
├── 1_extraccion_base/         # Consolidación de datos por cuenca
│   └── 01_extraccion_datos_cuencas.py
├── 2_modelacion_conceptual/   # Modelos conceptual subterráneo y superficial
│   ├── 02_modelo_conceptual_subterraneo.py
│   ├── 03_modelo_conceptual_superficial.py
│   └── 04_balance_hidrico_cuencas.py
├── 3_documentacion/           # Texto técnico de respuesta a observaciones
│   └── 05_texto_observaciones_67.py
└── 4_productos_SIG_3D/        # DEM, espesor, pozos y visualización interactiva
    ├── 08_descargar_dem_copernicus.py
    ├── 09_digitalizar_espesor_relleno.py
    ├── 10_pozos_acuifero.py
    ├── 11_mapa_pozos.py
    ├── 12_dataset_estratigrafico_UH.py
    └── 07_mapa_3d_leapfrog.py
```

### 8.2 Inventario de scripts y propósito

1. `01_extraccion_datos_cuencas.py`
   Consolida parámetros morfométricos, climáticos, hidrológicos e hidrogeológicos por cuenca y genera el dataset base (`datos_cuencas.json`).

2. `02_modelo_conceptual_subterraneo.py`
   Genera modelo conceptual subterráneo por cuenca (vistas 3D y esquemas hidrogeológicos) para respuesta directa a Obs. N°6.

3. `03_modelo_conceptual_superficial.py`
   Genera modelo conceptual superficial WEAP-style por cuenca (nodos de oferta/demanda, conexiones y balance) para Obs. N°7.

4. `04_balance_hidrico_cuencas.py`
   Calcula y grafica balance hídrico comparativo (P, ETR, Q, recarga, cierre) entre Penitente, El Oro y Róbalo.

5. `05_texto_observaciones_67.py`
   Construye texto técnico en Markdown/TXT para las secciones 5.1.1 y 5.1.2 del informe corregido.

6. `08_descargar_dem_copernicus.py`
   Descarga tiles Copernicus GLO-30, genera mosaicos por cuenca y reproyecta a EPSG:32719.

7. `09_digitalizar_espesor_relleno.py`
   Digitaliza/ajusta raster de espesor de relleno cuaternario (Figura 6-17/75) y exporta rasters regionales y por cuenca.

8. `10_pozos_acuifero.py`
   Integra fuentes de pozos (DDAA, shapefile, planillas), limpia y estandariza atributos, y exporta `pozos_acuifero.csv` y `pozos_acuifero.geojson`.

9. `11_mapa_pozos.py`
   Genera mapa estático e interactivo (Folium) de pozos por cuenca.

10. `12_dataset_estratigrafico_UH.py`
    Construye dataset estratigráfico con clasificación por Unidades Hidrogeológicas (UH).

11. `07_mapa_3d_leapfrog.py`
    Producto 3D integrador: DEM + base acuífero + red hídrica + pozos + estaciones + lagunas, con salidas HTML/PNG por cuenca y figura combinada.

### 8.3 Secuencia recomendada de ejecución

```bash
# 1) Base de datos por cuenca
python3 01_extraccion_datos_cuencas.py

# 2) Modelos conceptuales y balance
python3 02_modelo_conceptual_subterraneo.py
python3 03_modelo_conceptual_superficial.py
python3 04_balance_hidrico_cuencas.py

# 3) Texto técnico para informe
python3 05_texto_observaciones_67.py

# 4) Insumos SIG/3D
python3 08_descargar_dem_copernicus.py
python3 09_digitalizar_espesor_relleno.py
python3 10_pozos_acuifero.py
python3 11_mapa_pozos.py
python3 12_dataset_estratigrafico_UH.py

# 5) Integración visual 3D final
python3 07_mapa_3d_leapfrog.py
```

### 8.4 Entradas críticas del proyecto

- `01 Etapa 1/Anexos/Anexo E - SIG/04_Geodatabases/PERHC/*.shp`
  Cuencas, red hídrica y capas base de análisis.
- `01 Etapa 1/Anexos/Anexo E - SIG/05_Raster/*.shp`
  Extensiones de trabajo para DEM y pendientes.
- `03 SIG Magallanes/propsBOT_*_Proj.shp`
  Elevación de base acuífero (`Bottom1`) para Penitente y El Oro.
- `03 SIG Magallanes/Lagunas.shp`
  Polígonos de cuerpos lacustres integrados al modelo 3D.
- `01 Etapa 1/Antecedentes/Pozos/*`
  Fuentes de pozos y derechos de agua.
- `02 PyScripts Magallanes/data_set_oferta_hidrica.xlsx`
  Oferta superficial/subterránea para estaciones y tablas de recarga.

### 8.5 Salidas principales

- `datos_cuencas.json` (dataset consolidado por cuenca)
- `Figuras_Obs6_ModeloSubterraneo/` (figuras de modelo conceptual subterráneo)
- `Figuras_Obs7_ModeloSuperficial/` (figuras de modelo conceptual superficial)
- `Figuras_Obs6_Obs7_Balance/` (gráficos y tablas de balance)
- `Texto_Correcciones_Obs67/` (texto técnico para informe)
- `pozos_acuifero.csv`, `pozos_acuifero.geojson`, `mapa_pozos_interactivo.html`
- `DEM_Copernicus_30m/` (tiles, mosaicos y espesor)
- `Figuras_3D_Leapfrog/`:
  - `3D_Leapfrog_Penitente.html/.png`
  - `3D_Leapfrog_El_Oro.html/.png`
  - `3D_Leapfrog_Robalo.html/.png`
  - `3D_Leapfrog_COMBO_3Cuencas.html`

### 8.6 Parámetros y convenciones técnicas

- Sistema de referencia principal: EPSG:32719 (UTM 19S).
- Coordenadas en visualización 3D:
  ejes E/N etiquetados en metros UTM (`E (m)`, `N (m)`).
- Integración de base acuífero:
  prioridad `Bottom1` desde shapefile BOT; fallback a espesor digitalizado/gaussiano cuando no hay BOT.
- Control de calidad visual en 3D:
  máscara de distancia con `cKDTree` para evitar extrapolación espuria,
  drapeado de red hídrica, pozos de bombeo y lagunas con hover.

### 8.7 Dependencias mínimas

- Python 3.9+
- `numpy`, `pandas`, `geopandas`, `shapely`, `rasterio`, `scipy`
- `matplotlib`, `networkx`, `plotly`, `folium`, `pyproj`, `pyshp`

### 8.8 Problemas comunes y solución rápida

1. Error de rutas base:
   verificar `BASE_DIR`/`BASE` dentro de cada script.

2. Shapefile sin visualización en 3D:
   confirmar CRS EPSG:32719 y existencia de campo esperado (`Bottom1`, `NOMBRE`, etc.).

3. Superficies 3D incompletas:
   revisar datos de entrada (DEM/espesor/BOT) y regenerar en orden 08 → 09 → 07.

4. Lentitud o uso alto de RAM:
   ejecutar por script, cerrar figuras intermedias y validar tamaño de mosaicos DEM.

---

## 9. VISUALIZADOR 3D EN ARCGIS PRO (13-Mar-2026)

### 9.1 Objetivo

Hacer accesibles los modelos 3D Plotly interactivos desde ArcGIS Pro (Windows VM / Parallels) sin depender de un servidor externo ni de AGOL. El notebook `02_notebook_viewer.ipynb` funciona como interfaz embebida directamente en ArcGIS Pro.

### 9.2 Estructura de archivos

```text
3ds ArcGIS Pro/
├── 02_notebook_viewer.ipynb   ← Notebook con selector de modelo (activo)
├── 01_upload_htmls_agol.py    ← Sube HTMLs a AGOL como Web Mapping Application
├── 04_upload_notebook_agol.py ← Sube notebook a AGOL (primera vez)
├── 05_set_app_urls_agol.py    ← Actualiza campo URL de cada ítem en AGOL
├── 06_update_notebook_agol.py ← Actualiza contenido de notebook en AGOL
├── 07_make_public_agol.py     ← Hace públicos los ítems en AGOL
└── notas/
    ├── agol_item_urls.json    ← IDs y URLs de ítems en AGOL
    └── index_modelos_3d.html  ← Índice HTML con links públicos a los modelos
```

### 9.3 IDs de ítems en AGOL (portal: `idiem.maps.arcgis.com`, carpeta `Magallanes_3D`)

| Ítem | Item ID |
|------|---------|
| Cuenca Penitente | `18b42e85c92046008bdf54d5ce4bc282` |
| Cuenca El Oro | `2bc3c95de6e045058711d129c59d8101` |
| Cuenca Robalo | `51348d2ca7c84f4392582e6077a0bbe6` |
| Modelo Combinado | `fffd299b7303413e8c2863e389163367` |
| Notebook Visor | `70f742bf784e4304aa18950c0c0045a6` |

Todos los ítems son `"Web Mapping Application"` (HTMLs dentro de ZIP); el notebook es tipo `"Notebook"`.

### 9.4 Cómo funciona el notebook

El notebook lee los HTMLs directamente desde la ruta Mac compartida vía Parallels, los codifica en base64 y los embebe como `data:text/html;base64,...` dentro de un `<iframe>`. Un `<select>` HTML con JavaScript (`onchange`) intercambia el `src` del iframe sin ningún callback de Python, lo que garantiza que el selector funcione correctamente dentro del motor de notebook restringido de ArcGIS Pro.

**Flujo de carga:**
```
Shift+Enter en ArcGIS Pro
  → Python lee \\Mac\Home\...\Figuras_3D_Leapfrog\*.html
  → Codifica bytes a base64
  → Genera HTML con <select> JS + <iframe>
  → ArcGIS Pro renderiza el iframe con Plotly completo
```

**Rutas clave:**
- Mac: `/Users/carlosfloresarenas/Documents/Proyectos/Flores/IDIEM/01 Magallanes/02 PyScripts Magallanes/Figuras_3D_Leapfrog/`
- Windows VM: `\\Mac\Home\Documents\Proyectos\Flores\IDIEM\01 Magallanes\02 PyScripts Magallanes\Figuras_3D_Leapfrog\`

### 9.5 Cómo abrir el visualizador en ArcGIS Pro

1. Abrir ArcGIS Pro → **Insert** → **New Notebook** (o abrir desde `3ds ArcGIS Pro/02_notebook_viewer.ipynb`)
2. Conectar al portal `idiem.maps.arcgis.com` como `carlos_hidrofuturo`
3. Ejecutar la celda (Shift+Enter) — se cargan los 4 modelos automáticamente
4. Cambiar el modelo con el desplegable HTML

### 9.6 Cómo actualizar los modelos (flujo completo)

```bash
# 1. En Mac — regenerar HTMLs con cambios al script
cd "02 PyScripts Magallanes"
source ../.venv/bin/activate
python 07_mapa_3d_leapfrog.py

# 2. En Mac — actualizar notebook en AGOL (opcional)
cd "3ds ArcGIS Pro"
python 06_update_notebook_agol.py

# 3. En ArcGIS Pro — re-ejecutar la celda del notebook (Shift+Enter)
#    Los archivos se leen frescos desde \\Mac\Home\... en cada ejecución
```

No es necesario re-subir los HTMLs a AGOL; el notebook los lee directamente desde el sistema de archivos compartido en cada ejecución.

### 9.7 Decisiones técnicas y alternativas descartadas

| Enfoque | Resultado | Razón del descarte |
|---------|-----------|-------------------|
| `IFrame` con ruta local (`file://...`) | ✗ | Navegador bloquea acceso a archivos locales desde iframe |
| `data:text/html;base64` + `ipywidgets.Output` | ✗ | ArcGIS Pro no ejecuta callbacks de widgets Python (`observe`) |
| `widgets.interact` | ✗ | Tampoco dispara callbacks en ArcGIS Pro |
| `os.startfile()` / `subprocess` botones | ✗ | ArcGIS Pro no ejecuta callbacks de botones Python |
| Servidor HTTP `localhost` + `<a target="_blank">` | ✗ | ArcGIS Pro bloquea `target="_blank"` |
| **Servidor HTTP `localhost` + `<iframe>` JS** | ✓ | Funciona, pero requiere esperar sync de archivos en VM |
| **`data:text/html;base64` + `<select>` JS** | ✓ (**solución final**) | Sin servidor, sin callbacks Python, no depende de sync |

### 9.8 Colores y estilo visual (tema Leapfrog oscuro)

| Elemento | Color | Hex |
|----------|-------|-----|
| Fondo escena / paper | Azul marino | `#1a3a5c` / `#0f2540` |
| Terreno DEM | Amarillo vivo | `#f0e030` |
| Base acuífero | Azul vivo | `#00b0ff` |
| Paredes del bloque | Gradiente azul→ocre→amarillo | `#00b0ff` → `#4fc3f7` → `#b06020` → `#f0e030` |
| Límite cuenca | Cian | `#00e5ff` |
| Red hidrológica | Azul | `#1a6aff` |
| Lagunas | Azul claro | `#64b5f6` |
| Pozos de bombeo | Verde vivo | `#00e676` |
| Estación fluviométrica | Azul cielo | `#29b6f6` |
| Ejes / grillas | Azul medio | `#3a6a9a` |
| Texto | Blanco azulado | `#e8f0f8` |

**Nota sobre color del acuífero en ArcGIS Pro:** El motor WebGL del navegador embebido en ArcGIS Pro renderiza superficies `go.Surface` con `cmin≈cmax` como negro. La solución aplicada es usar `surfacecolor=np.full_like(z, 0.5)` con `cmin=0, cmax=1`, forzando el color al punto medio exacto de la escala de colores. El fondo azul marino mejora adicionalmente el contraste.

### 9.9 Leyenda por figura

Cada figura individual por cuenca incluye en la leyenda interactiva de Plotly:
- **Terreno (DEM)** — proxy Scatter3d amarillo (las superficies `go.Surface` no aparecen en leyenda de Plotly por defecto)
- **Base acuífero** — proxy Scatter3d azul vivo
- Límite cuenca, Red hidrológica, Lagunas, Pozos de bombeo, Estación fluviométrica

La figura combinada (3 cuencas) usa una anotación HTML manual de leyenda en la esquina inferior derecha.

---

