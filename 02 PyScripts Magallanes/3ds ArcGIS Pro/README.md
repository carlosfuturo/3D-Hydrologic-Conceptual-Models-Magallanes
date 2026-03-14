# 3D Magallanes → ArcGIS Online

Scripts y documentación para publicar los modelos 3D del proyecto Magallanes
en el portal ArcGIS Online `idiem.maps.arcgis.com`.

---

## Estructura de carpetas

```
3ds ArcGIS Pro/
├── README.md                    ← Este archivo
├── 01_upload_htmls_agol.py      ← Sube los HTMLs Plotly al portal AGOL
├── 02_notebook_viewer.ipynb     ← Notebook AGOL con selector IFrame
├── 03_publish_scene_layers.py   ← (Fase 2) Scene Layers nativos ArcGIS
└── notas/
    ├── progreso.md              ← Checklist de avance
    └── agol_item_urls.json      ← (auto-generado) IDs y URLs de items subidos
```

---

## Fase 1 — Notebooks con IFrame (implementado)

### Flujo

1. Los archivos HTML en `../Figuras_3D_Leapfrog/` son modelos Plotly autocontenidos.
2. `01_upload_htmls_agol.py` los sube como ítems tipo `"HTML"` al portal AGOL
   y guarda los URLs en `notas/agol_item_urls.json`.
3. `02_notebook_viewer.ipynb` carga ese JSON, muestra un dropdown ipywidgets
   y renderiza cada modelo en un IFrame de 900 px de altura.
4. El notebook se sube manualmente a AGOL Content como ítem tipo `"Notebook"`.

### Archivos HTML fuente

| Figura | Archivo |
|--------|---------|
| DEM Penitente | `DEM_Penitente_3D.html` |
| DEM El Oro | `DEM_El_Oro_3D.html` |
| Modelo combinado | `Modelo_Combinado_3D.html` |
| Vista extra | *(verificar en Figuras_3D_Leapfrog/)* |

### Requisitos

```bash
pip install arcgis ipywidgets
```

---

## Fase 2 — Scene Layers nativos (pendiente ArcGIS Pro)

`03_publish_scene_layers.py` es un placeholder que documenta las capas a publicar:

| Capa | Formato fuente | Tipo AGOL |
|------|---------------|-----------|
| DEM Penitente | GeoTIFF | ElevationLayer |
| DEM El Oro | GeoTIFF | ElevationLayer |
| Pozos acuífero | `pozos_acuifero.geojson` | FeatureLayer 3D |
| Lagunas | `Lagunas.shp` | FeatureLayer 3D |

Requiere ArcGIS Pro instalado localmente + módulo `arcpy`.

---

## Portal AGOL

- **URL:** `https://idiem.maps.arcgis.com`
- **Usuario:** `carlos_hidrofuturo`
- **Carpeta de contenido:** `Magallanes_3D`

---

## Notas importantes

- Los HTMLs Plotly son ≈ 5–40 MB. AGOL acepta ítems HTML de hasta 1 GB.
- El IFrame en el Notebook puede bloquearse por CORS en algunos navegadores.
  En ese caso, descargar el HTML y abrirlo localmente.
- `notas/agol_item_urls.json` se genera automáticamente al correr
  `01_upload_htmls_agol.py`. No se incluye en git (puede contener URLs sensibles).
