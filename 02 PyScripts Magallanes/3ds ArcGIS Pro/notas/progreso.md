# Progreso — 3D Magallanes en ArcGIS Online

Proyecto: Hidrogeología Magallanes — IDIEM  
Portal: `idiem.maps.arcgis.com` | Usuario: `carlos_hidrofuturo`

---

## Fase 1 — Notebook con IFrame

- [ ] Verificar tamaños de los 4 archivos HTML en `Figuras_3D_Leapfrog/`
- [ ] Instalar dependencias: `pip install arcgis ipywidgets`
- [ ] Correr `01_upload_htmls_agol.py` → se genera `notas/agol_item_urls.json`
- [ ] Verificar los 4 ítems en AGOL Content (`Magallanes_3D`)
- [ ] Subir `02_notebook_viewer.ipynb` a AGOL Content
- [ ] Abrir el notebook en AGOL → verificar que los 4 modelos cargan en IFrame
- [ ] Compartir notebook con cliente DGA (compartir ítem con grupos o usuario)

---

## Fase 2 — Scene Layers nativos (pendiente ArcGIS Pro)

- [ ] Confirmar nombres exactos de los GeoTIFF DEM en `DEM_Copernicus_30m/`
- [ ] Confirmar nombre del shapefile Lagunas en `03 SIG Magallanes/`
- [ ] Ejecutar `03_publish_scene_layers.py` desde entorno Python de ArcGIS Pro
- [ ] Publicar DEMs como ElevationLayer
- [ ] Publicar pozos como FeatureLayer 3D
- [ ] Publicar lagunas como FeatureLayer 3D
- [ ] Crear Web Scene 3D combinando todas las capas
- [ ] Compartir Web Scene con cliente DGA

---

## Problemas conocidos

| Problema | Causa probable | Solución |
|----------|---------------|----------|
| IFrame en blanco | CORS bloqueado en AGOL | Abrir HTML localmente |
| HTML > 40 MB | DEM alta resolución | Reducir resolución en `07_mapa_3d_leapfrog.py` |
| `arcgis` no instala | Conflicto de entorno | Usar entorno conda aparte |
| Item ID vacío | Script de subida no corrido | Correr `01_upload_htmls_agol.py` primero |

---

## URLs y referencias

*Se completan automáticamente al correr `01_upload_htmls_agol.py`.*  
Ver `notas/agol_item_urls.json` para los IDs y URLs de cada ítem.

---

*Última actualización: 2026-03-13*
