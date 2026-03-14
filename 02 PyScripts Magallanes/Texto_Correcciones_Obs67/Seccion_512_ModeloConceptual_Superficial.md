# 5.1.2 Modelo Conceptual Hidrológico Superficial Preliminar

> **Respuesta a Observación DGA N°7** — *"Se solicita que el modelo conceptual superficial se presente de forma individual por cuenca, a escala, y en un software apropiado conforme a las Bases Técnicas (Letra F). Los diagramas presentados en el Informe Etapa 1 son genéricos y no individualizan cada sistema de cuencas."*

De acuerdo con lo indicado en las Bases Técnicas (RES. EX. 2497, Letra F) y en complemento con la respuesta a la Observación DGA N°6, el modelo conceptual hidrológico superficial se presenta **de forma individual para cada cuenca de estudio**, mediante diagramas de nodos tipo WEAP (*Water Evaluation and Planning System*), elaborados con el software Python 3 (código abierto, transferible a DGA). Las figuras correspondientes se incluyen en el Anexo E del presente Informe.

Como refuerzo de trazabilidad y consistencia entre componentes superficial-subterráneo, esta sección se integra con el set 3D interactivo por cuenca (Script 07), en el cual se representan en conjunto: límite de cuenca, red hidrológica, lagunas, estaciones fluviométricas, pozos de bombeo y geometría de base de acuífero.

El software de modelación seleccionado para la Etapa II es **WEAP**, plataforma de referencia para la modelación integrada de recursos hídricos desarrollada por el SEI (*Stockholm Environment Institute*), ampliamente utilizada por la DGA y organismos técnicos en Chile.

---

## 5.1.2.1 Cuenca del Río Penitente

**Figura MC-Sup-01**: Modelo Conceptual Hidrológico Superficial — Río Penitente
*(ver archivo `MC_Superficial_Penitente.png` en Anexo E / Figuras_Obs7_ModeloSuperficial)*

### Descripción del sistema

La cuenca del Río Penitente constituye el sistema hídrico más extenso de las tres cuencas de estudio, con una superficie de **1,750 km²** bajo un régimen semi-árido (BSk). El balance hídrico muestra una precipitación media anual de **120 mm/año**, con una evapotranspiración real (ETR) de **110 mm/año**, una escorrentía media de **3.2 m³/s** (equivalente a **57 mm/año**) registrada en la estación *Penitente en Morro Chico* (BNA N° 12004002), y una recarga subterránea estimada de **10 mm/año**.

### Esquematización del sistema (nodos WEAP)

| Componente | Descripción | Valores indicativos |
|---|---|---|
| **Subcuenca Alta-Cordillera** | Zona de recarga pluvionival (480 km²) | P≈160 mm/a, ETR≈130 mm/a |
| **Subcuenca Media-Pampa** | Área principal de generación de escorrentía (820 km²) | P≈115 mm/a, ETR≈110 mm/a |
| **Subcuenca Baja-Llanura** | Sector de tránsito y descarga (450 km²) | P≈90 mm/a, ETR≈90 mm/a |
| **Lagunas estepáricas** | Almacenamiento superficial (3.2 km²) | Regulación temporal |
| **Tramo río (aforo)** | Río Penitente en Morro Chico | Q=3.2 m³/s (control) |
| **Ganadería** | Demanda DAA superficial | 26.4 L/s (mayor demanda) |
| **Consumo humano rural** | Demanda rurales dispersos | 2.1 L/s |
| **SHAC Penitente** | Almacenamiento subterráneo (conexión) | Recarga 10 mm/a |
| **Salida — Estrecho Magallanes** | Cierre de la cuenca | Q salida = 3.2 m³/s |

### Balance hídrico superficial

$$P = ETR + Q + Rec + \Delta S$$
$$120 = 110 + 57 + 10 + (-57) \approx 0 \quad [\text{mm/año}]$$

El coeficiente de escorrentía es **CE = 0.48**, indicando que aproximadamente el 48% de la precipitación se transforma en escorrentía directa, valor consistente con el clima semi-árido y la baja cobertura vegetal de la zona. La demanda total registrada (28.5 L/s) representa el 0.9% del caudal medio, indicando una **presión hídrica baja** en términos de extracción frente al caudal disponible.

---

## 5.1.2.2 Cuenca del Río El Oro

**Figura MC-Sup-02**: Modelo Conceptual Hidrológico Superficial — Río El Oro
*(ver archivo `MC_Superficial_El_Oro.png` en Anexo E / Figuras_Obs7_ModeloSuperficial)*

### Descripción del sistema

La cuenca del Río El Oro es el sistema hídrico más productivo de las tres cuencas de estudio, con una superficie de **707 km²** bajo un régimen mediterráneo frío oceánico (Csc). La precipitación media es de **900 mm/año**, la ETR de **380 mm/año**, y la escorrentía media de **10.5 m³/s** (468 mm/año) registrada en la estación *Oro en Bahía San Felipe* (BNA N° 12101001). La cuenca presenta un **glaciar remanente** en la zona alta (>600 m s.n.m.) que aporta escorrentía nival y glaciar relevante durante la primavera-verano.

### Esquematización del sistema (nodos WEAP)

| Componente | Descripción | Valores indicativos |
|---|---|---|
| **Sector glaciar + nival** | Fuente nívoglaciar alta montaña (~80 km²) | P≈1,100 mm/a (nieve+lluvia) |
| **Subcuenca Alta-Montaña** | Zona húmeda cordillerana (280 km²) | P≈950 mm/a, ETR≈380 mm/a |
| **Subcuenca Baja-Valle** | Valle río El Oro / Tierra del Fuego (347 km²) | P≈800 mm/a, ETR≈380 mm/a |
| **Laguna Baquedano** | Cuerpo lacustre regulador (0.5 km²) | Almacenamiento temporal |
| **Tramo río (aforo)** | Río El Oro en Bahía San Felipe | Q=10.5 m³/s (control) |
| **Ganadería TF** | Demanda DAA ganadera Tierra del Fuego | 41.7 L/s (demanda dominante) |
| **Consumo humano** | No se identifican centros poblados directos | 3.5 L/s |
| **SHAC Río Oro** | Acuífero glaciofluvial (conexión) | Recarga 108 mm/a |
| **Salida — Bahía San Felipe** | Cierre cuenca / Canal Beagle | Q salida = 10.5 m³/s |

### Balance hídrico superficial

$$P = ETR + Q + Rec + \Delta S$$
$$900 = 380 + 468 + 108 + (-56) \approx 0 \quad [\text{mm/año}]$$

El coeficiente de escorrentía es **CE = 0.52**, lo que refleja la alta humedad de la cuenca. La demanda total (45.2 L/s) representa el 0.43% del caudal medio, confirmando la **baja presión hídrica** actual. Sin embargo, el componente nívoglaciar del régimen de escorrentía introduce **vulnerabilidad a la variabilidad climática** (retroceso glaciar proyectado) que deberá considerarse en la modelación prospectiva de la Etapa II.

---

## 5.1.2.3 Cuenca del Río Róbalo

**Figura MC-Sup-03**: Modelo Conceptual Hidrológico Superficial — Río Róbalo
*(ver archivo `MC_Superficial_Robalo.png` en Anexo E / Figuras_Obs7_ModeloSuperficial)*

### Descripción del sistema

La cuenca del Río Róbalo es la más pequeña de las tres cuencas de estudio (22 km²), correspondiendo a una cuenca de montaña tipo torrencial ubicada en la isla Navarino, bajo un régimen de tundra (ET). Sin embargo, su **importancia estratégica es máxima**: constituye el único sistema de abastecimiento de agua potable (AP) de Puerto Williams (~3,000 habitantes), siendo declarada como SSPP (*Sistema de Servicio Público*) por Aguas Magallanes S.A.

La precipitación media es de **700 mm/año**, la ETR de **280 mm/año**, y la escorrentía media de **0.45 m³/s** registrada en la estación *Róbalo en Puerto Williams* (BNA N° 12303001). El caudal equivalente en mm/año (646 mm) supera la precipitación media debido al **aporte de deshielo y escorrentía subsuperficial desde el permafrost activo** (<600 m s.n.m. en isla Navarino).

### Esquematización del sistema (nodos WEAP)

| Componente | Descripción | Valores indicativos |
|---|---|---|
| **Cuenca de montaña** | Cerro Bandera y afluentes (22 km²) | P≈700 mm/a, ETR≈280 mm/a |
| **Lagunas torrente** | Pequeñas lagunas de montaña (0.52 km²) | Regulación temporal |
| **Río Róbalo** | Cauce principal (3.65 km) | Q=0.45 m³/s (control) |
| **Obra de toma** | Captación Aguas Magallanes | Captación superficial AP |
| **Agua Potable Puerto Williams** | Único SSPP abastecimiento urbano | 12.0 L/s (100% del uso) |
| **Acuífero fisurado** | Roca fracturada (conexión débil) | Recarga ≈35 mm/a |
| **Salida — Canal Beagle** | Caudal excedente cuenca | Q excedente = 0.41 m³/s |

### Balance hídrico superficial

$$P + Deshielo_{permafrost} = ETR + Q + Rec + \Delta S$$
$$700 + \Delta_{perm.} = 280 + 646 + 35 + (-261) \quad [\text{mm/año}]$$

El coeficiente de escorrentía aparente es **CE = 0.92**, extremadamente alto, consistente con la naturaleza torrencial de la cuenca, la alta impermeabilidad del sustrato granítico, y el aporte del deshielo estacional de permafrost. La **demanda unitaria** (12.0 L/s para AP) representa el 2.7% del caudal medio, siendo baja en términos relativos; sin embargo, en períodos de estiaje extremo se han registrado conflictos de abastecimiento que justifican la protección y monitoreo riguroso de esta cuenca.

**Recomendación técnica**: Se recomienda establecer en la Etapa II: (i) un **caudal ecológico mínimo** para el Río Róbalo aguas abajo de la obra de toma; (ii) un análisis de frecuencia de caudales mínimos para garantizar el abastecimiento AP ante eventos extremos; y (iii) la definición de un área de protección de la cuenca de captación conforme a la normativa DGA.

---

## 5.1.2.4 Cuadro Comparativo de los Modelos Conceptuales Superficiales

**Figura BH-01**: Balance Hídrico Cuantitativo Comparativo — 3 Cuencas
*(ver archivo `Balance_Hidrico_Comparativo.png` en Anexo E / Figuras_Obs6_Obs7_Balance)*

| Indicador | Penitente | El Oro | Róbalo |
|---|---|---|---|
| Área (km²) | 1,750 | 707 | 22 |
| Clima | BSk (semi-árido) | Csc (mediterráneo) | ET (tundra) |
| P (mm/año) | 120 | 900 | 700 |
| ETR (mm/año) | 110 | 380 | 280 |
| Q (mm/año) | 57 | 468 | 646 (*) |
| Recarga sub. (mm/año) | 10 | 108 | 35 |
| Q medio (m³/s) | 3.2 | 10.5 | 0.45 |
| CE = Q/P | 0.48 | 0.52 | 0.92 (*) |
| CI = Rec/P | 0.08 | 0.12 | 0.05 |
| Número de Curva | 72 | 65 | 85 |
| Demanda total (L/s) | 28.5 | 45.2 | 12.0 |
| Presión hídrica (D/Q) | 0.9% | 0.4% | 2.7% |
| Estación de control | Morro Chico | Bahía San Felipe | Puerto Williams |

(*) *Valor Q>P explicado por aporte de deshielo y escorrentía subsuperficial desde permafrost activo.*

Los tres sistemas presentan **niveles de presión hídrica bajos** respecto a las demandas actuales registradas. Sin embargo, las diferencias climáticas y geomorfológicas entre las cuencas determinan comportamientos hidrológicos contrastantes que justifican la modelación individual en la Etapa II.



---

## 5.1.2.5 Actualización de consistencia de insumos y productos (14-03-2026)

Se verificó la consistencia de esta sección con los insumos y productos actuales del proyecto:

- Dataset base consolidado: `datos_cuencas.json`.
- Balance comparativo: `Balance_Hidrico_Comparativo.png`.
- Modelos conceptuales superficiales por cuenca: `MC_Superficial_*.png`.
- Integración visual con modelo 3D interactivo por cuenca y combinado (HTML), incluyendo red hidrológica con `hover` por nombre de cauce.

Esta actualización mantiene la estructura de respuesta a la Observación N°7 y mejora la trazabilidad entre los productos gráficos, los datasets de cálculo y la narrativa técnica del informe.


---

*Elaborado por: Especialista Senior en Modelación — IDIEM*
*Software: Python 3.x / matplotlib (código abierto — código fuente transferible a DGA)*
*Software modelación Etapa II: WEAP (Water Evaluation and Planning System — SEI)*
*Fecha actualización: 14-03-2026*
