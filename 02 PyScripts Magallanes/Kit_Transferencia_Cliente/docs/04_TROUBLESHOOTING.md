# Troubleshooting

## 1) Error de rutas base

Sintoma: scripts no encuentran shapefiles o rasters.

Accion:

- Revisar `config/project_config.yaml`.
- Confirmar estructura de carpetas original.
- Verificar permisos de lectura.

## 2) Error de dependencias geoespaciales

Sintoma: falla import de `geopandas`, `rasterio` o `pyproj`.

Accion:

- Reinstalar entorno con `scripts/setup_env.sh`.
- Si persiste, usar `environment_cliente.yml` con Conda.

## 3) 3D incompleto o con huecos

Sintoma: superficies parciales o vacias.

Accion:

- Ejecutar en orden: 08 -> 09 -> 07.
- Verificar `propsBOT_*_Proj.shp` y campo `Bottom1`.
- Confirmar CRS EPSG:32719.

## 4) ArcGIS Pro no cambia modelo con widgets

Sintoma: selector Python no responde.

Accion:

- Usar selector HTML+JavaScript del notebook oficial.
- Evitar callbacks Python de `ipywidgets`.

## 5) Falla autenticacion AGOL

Sintoma: scripts AGOL retornan error de login.

Accion:

- Validar `AGOL_USERNAME`, `AGOL_PASSWORD`, `AGOL_PORTAL`.
- Probar login en navegador con la misma cuenta.
- Verificar permisos sobre la carpeta de contenido.
