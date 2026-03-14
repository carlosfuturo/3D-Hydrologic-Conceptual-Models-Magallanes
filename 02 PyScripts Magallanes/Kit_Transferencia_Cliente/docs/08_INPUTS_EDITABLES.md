# Inputs editables para cliente

## Objetivo

Permitir que el cliente modifique insumos de modelos sin editar el codigo fuente.

## Como funciona

Los scripts del proyecto ahora revisan primero la carpeta `Editable_Inputs/` en la raiz de `01 Magallanes`.

Si encuentran ahi un archivo con la misma ruta relativa que el original, usan ese archivo editable.
Si no existe override, usan el insumo original del proyecto.

## Preparacion del workspace editable

```bash
cd "02 PyScripts Magallanes/Kit_Transferencia_Cliente"
bash scripts/prepare_editable_inputs.sh
```

Esto crea:
- `Editable_Inputs/`
- `Editable_Inputs/input_catalog.csv`
- `Editable_Inputs/input_inventory.csv`

## Preparacion selectiva por categoria

Para evitar copiar de una vez todos los raster pesados, se puede preparar por categoria:

```bash
bash scripts/prepare_editable_inputs.sh --category perhc
bash scripts/prepare_editable_inputs.sh --category sig3d
bash scripts/prepare_editable_inputs.sh --category datasets
bash scripts/prepare_editable_inputs.sh --category dem
```

Categorias disponibles: `perhc`, `raster`, `sig3d`, `pozos`, `datasets`, `dem`.

## Que puede editar el cliente

- SHP de cuencas, red hidrografica y lagunas
- SHP BOT de base de acuifero
- Rasters DEM y espesor de relleno
- XLSX y CSV de oferta hidrica, pozos y demanda
- `datos_cuencas.json`
- `pozos_acuifero.geojson`

## Regla clave

Mantener exactamente el mismo nombre de archivo y la misma ruta relativa dentro de `Editable_Inputs/`.

## Casos de uso tipicos

1. Ajustar `propsBOT_*_Proj.shp` y volver a correr `07_mapa_3d_leapfrog.py`.
2. Modificar `Lagunas.shp` o `red_hidro_*.shp` y regenerar el modelo 3D.
3. Editar `datos_cuencas.json` y volver a correr modelos conceptuales y balance.
4. Actualizar `pozos_acuifero.csv` o fuentes XLSX y regenerar pozos/mapas/3D.
