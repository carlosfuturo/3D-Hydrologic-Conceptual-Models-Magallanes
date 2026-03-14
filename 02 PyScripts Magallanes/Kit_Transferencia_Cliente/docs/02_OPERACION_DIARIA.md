# Operacion diaria

## Flujo corto (recomendado)

1. Activar entorno:

```bash
source ../.venv_cliente/bin/activate
```

2. Ejecutar pipeline completo:

```bash
bash scripts/run_full_pipeline.sh
```

3. Revisar log en `output/`.

## Flujo por etapas (si se requiere control)

Desde la carpeta `02 PyScripts Magallanes`:

```bash
python 01_extraccion_datos_cuencas.py
python 02_modelo_conceptual_subterraneo.py
python 03_modelo_conceptual_superficial.py
python 04_balance_hidrico_cuencas.py
python 05_texto_observaciones_67.py
python 08_descargar_dem_copernicus.py
python 09_digitalizar_espesor_relleno.py
python 10_pozos_acuifero.py
python 11_mapa_pozos.py
python 12_dataset_estratigrafico_UH.py
python 07_mapa_3d_leapfrog.py
```

## Control de integridad

Al finalizar, generar manifiesto:

```bash
bash scripts/generate_manifest.sh
```

Comparar el manifiesto con la version oficial de entrega.

## Edicion de insumos por parte del cliente

Cuando el cliente necesite ajustar entradas del modelo:

```bash
bash scripts/prepare_editable_inputs.sh
```

Editar los archivos generados en `Editable_Inputs/` y luego volver a correr los scripts necesarios.

## Paquete MASTER seguro

Para transferir la raiz completa `01 Magallanes`:

```bash
bash scripts/package_master_workspace.sh
```
