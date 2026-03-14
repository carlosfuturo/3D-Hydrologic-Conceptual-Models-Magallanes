# 5.1.1 Modelo Conceptual Hidrogeológico Preliminar

> **Respuesta a Observación DGA N°6** — *"Se solicita que el modelo conceptual se presente por cuenca y de forma individual, a escala, y en un software apropiado, tal como lo exigen las Bases Técnicas (Letra F)."*

De acuerdo con lo indicado en las Bases Técnicas (RES. EX. 2497 del 18.07.2025, Letra F), el modelo conceptual hidrogeológico se presenta **de forma individual para cada una de las tres cuencas de estudio**, con representación gráfica en 3D elaborada mediante el software Python 3 (código abierto, licencias transferibles a la DGA). Las figuras correspondientes se incluyen en el Anexo E (SIG) del presente informe.

La modelación conceptual fue desarrollada con el software Python 3.x, utilizando tanto herramientas de representación esquemática (matplotlib / mpl\_toolkits.mplot3d) como visualización 3D interactiva (Plotly), cumpliendo los requisitos de la Letra F respecto a: (i) representación gráfica tridimensional, (ii) generación de figuras a escala, y (iii) transferibilidad del código fuente a la DGA como parte del entregable de la Etapa I.

---

## 5.1.1.1 Cuenca del Río Penitente

**Figura MC-Sub-01**: Modelo Conceptual Hidrogeológico Preliminar — Río Penitente
*(ver archivo `MC_Subterraneo_Penitente.png` en Anexo E / Figuras_Obs6_ModeloSubterraneo)*

La cuenca del Río Penitente presenta un clima semi-árido (BSk) con precipitaciones medias anuales del orden de **120 mm/año**, concentradas principalmente entre mayo y agosto. El sistema hidrogeológico está controlado por los sedimentos cuaternarios de relleno de la Pampa Magallánica, donde se desarrolla un **acuífero libre de tipo poroso granular** (SHAC Penitente), con espesores estimados entre **15 y 30 m** y nivel freático a profundidades de **3–8 m** bajo la superficie.

**Unidades hidrogeológicas identificadas:**
- **Unidad I (acuífero)**: Gravas y arenas fluvioglaciales cuaternarias; conductividad hidráulica K = 5–20 m/día; permeabilidad media-alta.
- **Unidad II (acuitardo)**: Arcillas y limos glaciares; actúa como base del acuífero libre.
- **Unidad III (sustrato)**: Sedimentario cretácico-eoceno; baja permeabilidad, comportamiento como aquitardo.

**Mecanismo de recarga**: La recarga del acuífero se produce principalmente por infiltración directa de precipitaciones sobre el relleno sedimentario de la pampa (recarga difusa), estimada en **10 mm/año** (~8% de la precipitación media). Como fuente secundaria se reconoce la recarga lateral desde los flancos cordilleranos durante el deshielo primaveral y las precipitaciones estivales. No se identifican glaciares ni áreas de deshielo permanente relevante.

**Mecanismo de descarga**: La descarga natural ocurre como flujo de base (*baseflow*) hacia el Río Penitente, manteniendo caudales mínimos en período estival. Las extracciones actuales (DAA subterráneos) son marginales respecto a la recarga estimada.

**Balance subterráneo sintético (mm/año):**

| Componente | Valor (mm/año) | Observación |
|---|---|---|
| Recarga por infiltración directa | +10 | ~8% de P |
| Recarga lateral flanco cordillerano | +3 | estimado |
| Descarga como baseflow | -8 | caudal mínimo período seco |
| Extracciones DAA subterráneo | -2 | DAA registrados DGA |
| Variación almacenamiento (ΔS) | ≈ +3 | sistema en equilibrio dinámico |

---

## 5.1.1.2 Cuenca del Río El Oro

**Figura MC-Sub-02**: Modelo Conceptual Hidrogeológico Preliminar — Río El Oro
*(ver archivo `MC_Subterraneo_El_Oro.png` en Anexo E / Figuras_Obs6_ModeloSubterraneo)*

La cuenca del Río El Oro se ubica en la región central de Tierra del Fuego, con un régimen climático de tipo mediterráneo frío oceánico (Csc) y precipitaciones medias de **900 mm/año**, distribuidas relativamente uniformemente a lo largo del año, con máximos invernales. Presenta un **glaciar remanente** en el sector de altura (>600 m s.n.m.), que constituye un reservorio hídrico adicional y fuente de recarga estival.

El sistema hidrogeológico está asociado a los depósitos fluvioglaciales del valle del Río El Oro (Tierra del Fuego), donde se desarrolla un **acuífero libre glaciofluvial** (SHAC Río Oro) de alta permeabilidad, con espesores estimados entre **20 y 50 m** y niveles freáticos a **1–4 m** de profundidad en el sector del valle.

**Unidades hidrogeológicas identificadas:**
- **Unidad I (acuífero principal)**: Gravas y arenas gruesas glaciofluviales cuaternarias; K = 15–50 m/día; alta permeabilidad.
- **Unidad II (acuitardo local)**: Limos y arcillas de origen lacustre interglacial; distribución discontinua.
- **Unidad III (sustrato)**: Complejo metamórfico-sedimentario paleógeno; baja permeabilidad generalizada.

**Mecanismo de recarga**: La recarga es significativa dado el régimen pluviométrico húmedo; se estima en **108 mm/año** (~12% de P). Las principales fuentes incluyen: (i) infiltración directa sobre el valle fluvioglacial, (ii) recarga inducta riverbank por el Río El Oro en períodos de aguas altas, y (iii) fusión nival y glaciar de la zona alta durante el período estival (octubre–marzo).

**Mecanismo de descarga**: La descarga natural predominante es el flujo de base hacia el Río El Oro, que explica los caudales base relevantes en período seco. Las extracciones para uso ganadero (41.7 L/s DAA, principalmente superficial) y consumo humano (3.5 L/s) son moderadas.

**Balance subterráneo sintético (mm/año):**

| Componente | Valor (mm/año) | Observación |
|---|---|---|
| Recarga por infiltración directa | +85 | precipitaciones sobre valle |
| Recarga inducta + deshielo | +23 | aporte glaciar/nival estival |
| Descarga como baseflow | -95 | caudales base período seco |
| Extracciones DAA subterráneo | -8 | pozos ganaderos Tierra del Fuego |
| Variación almacenamiento (ΔS) | ≈ +5 | sistema en equilibrio dinámico |

---

## 5.1.1.3 Cuenca del Río Róbalo

**Figura MC-Sub-03**: Modelo Conceptual Hidrogeológico Preliminar — Río Róbalo
*(ver archivo `MC_Subterraneo_Robalo.png` en Anexo E / Figuras_Obs6_ModeloSubterraneo)*

La cuenca del Río Róbalo corresponde a una **pequeña cuenca de montaña** (22 km²) de tipo torrencial, ubicada en la isla Navarino, con clima de tundra (ET) y precipitaciones medias de **700 mm/año**, distribuidas uniformemente. Esta cuenca reviste **especial importancia estratégica**: constituye el único sistema de abastecimiento de agua potable de Puerto Williams (~3,000 habitantes).

El sistema hidrogeológico está controlado por el **Batolito Hornos-Moreno** (roca plutónica granítica-granodiorítica), que conforma el sustrato impermeable dominante. El acuífero presente es de tipo **fisurado en roca** (granitos fracturados), de extensión limitada, condicionado por la densidad y apertura del sistema de fracturas.

**Unidades hidrogeológicas identificadas:**
- **Unidad I (acuífero fisurado)**: Granito fracturado del Batolito Hornos-Moreno; K = 0.1–2 m/día; permeabilidad baja a moderada según densidad de fracturas.
- **Unidad II (cobertura)**: Depósitos superficiales coluviales y suelos orgánicos turfosos (peatlands); actúan como reguladores de la recarga.
- **Unidad III (permafrost activo)**: En sectores >600 m s.n.m., se reconoce permafrost discontinuo que aporta escorrentía estacional durante el deshielo.

**Mecanismo de recarga**: La recarga del acuífero fisurado es limitada, estimada en **35 mm/año** (~5% de P), debido al bajo almacenamiento de la roca fracturada y la elevada pendiente de la cuenca que favorece la escorrentía directa. La cobertura orgánica (turbas/peatlands) actúa como regulador de la infiltración hacia el sustrato rocoso.

**Mecanismo de descarga**: La descarga se produce principalmente como flujo base difuso hacia el Río Róbalo. Las extracciones de Aguas Magallanes (12.0 L/s AP Puerto Williams) se realizan directamente del Río Róbalo mediante obra de toma superficial; no se identifican extracciones subterráneas relevantes registradas.

**Balance subterráneo sintético (mm/año):**

| Componente | Valor (mm/año) | Observación |
|---|---|---|
| Recarga por infiltración en roca | +35 | 5% de P |
| Descarga como baseflow | -30 | aporte al río en período seco |
| Extracciones subterráneas | ~0 | sin pozos registrados |
| Variación almacenamiento (ΔS) | ≈ +5 | sistema en equilibrio |

**Nota de gestión hídrica**: Por el carácter estratégico de esta cuenca para el abastecimiento de Puerto Williams, se recomienda establecer un programa de monitoreo continuo del nivel freático y del caudal del Río Róbalo con registro automático (frecuencia mínima: 15 minutos), como medida de alerta temprana ante variaciones climáticas o eventos extremos.



---

## 5.1.1.4 Actualización técnica de soporte 3D (14-03-2026)

Como robustecimiento de la conceptualización subterránea por cuenca, se incorporó un set de modelos 3D interactivos (HTML) y estáticos (PNG) generados con el Script 07, con los siguientes criterios técnicos:

- **Base de acuífero por datos locales**: para Penitente y El Oro se utilizó la elevación de base desde `propsBOT_Vertientes_Proj.shp` y `propsBOT_Fuego_Proj.shp` (campo `Bottom1`, m.s.n.m.).
- **Control de extrapolación**: se aplicó enmascaramiento por distancia máxima usando `cKDTree`, evitando triángulos espurios fuera de zonas con información.
- **Fallback en Róbalo**: al no existir shapefile BOT equivalente, se utilizó superficie gaussiana calibrada a partir de la Fig. 75 PEGH DGA 2021.
- **Integración de pozos de bombeo**: se integró `pozos_acuifero.csv` para visualización de puntos y sondajes con profundidad cuando existe dato.
- **Interacción hidrográfica**: la red hídrica se entrega con `hover` por tramo usando el atributo `NOMBRE`.

**Productos asociados (Anexo E / Figuras_3D_Leapfrog):**

- `3D_Leapfrog_Penitente.html` y `3D_Leapfrog_Penitente.png`
- `3D_Leapfrog_El_Oro.html` y `3D_Leapfrog_El_Oro.png`
- `3D_Leapfrog_Robalo.html` y `3D_Leapfrog_Robalo.png`
- `3D_Leapfrog_COMBO_3Cuencas.html`


---

*Elaborado por: Especialista Senior en Modelación — IDIEM*
*Software: Python 3.x / matplotlib / mpl\_toolkits.mplot3d / Plotly (código abierto — código fuente transferible a DGA)*
*Fecha actualización: 14-03-2026*
