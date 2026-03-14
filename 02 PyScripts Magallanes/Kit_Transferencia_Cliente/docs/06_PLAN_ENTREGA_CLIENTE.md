# Plan de entrega cliente (ejecucion guiada)

## Objetivo

Entregar el proyecto en un formato que el cliente pueda instalar y ejecutar sin depender del ambiente original del equipo IDIEM.

## Paso 1: preparar entorno

```bash
cd "02 PyScripts Magallanes/Kit_Transferencia_Cliente"
bash scripts/setup_env.sh
```

## Paso 2: configurar rutas y credenciales

1. Copiar `config/project_config.example.yaml` como `config/project_config.yaml`.
2. Copiar `config/.env.example` como `config/.env`.
3. Completar valores reales en ambos archivos.

## Paso 3: validar entorno

```bash
bash scripts/run_smoke_test.sh
```

## Paso 4: ejecutar pipeline completo

```bash
bash scripts/run_full_pipeline.sh
```

## Paso 5: generar manifiesto de integridad

```bash
bash scripts/generate_manifest.sh
```

## Paso 6: empaquetar para envio cliente

```bash
bash scripts/package_delivery.sh
bash scripts/package_master_workspace.sh
```

Resultado: carpeta `output/delivery_YYYYMMDD_HHMMSS` con:
- ZIP CORE
- ZIP FULL
- checksums SHA256

Resultado adicional: carpeta `output/master_YYYYMMDD_HHMMSS` con:
- ZIP MASTER de toda la raiz `01 Magallanes`
- checksum SHA256

## Paso 6b: preparar insumos editables para cliente

```bash
bash scripts/prepare_editable_inputs.sh
```

Esto habilita la modificacion controlada de SHP, raster y datasets sin alterar el codigo fuente.

## Paso 7: cierre formal

1. Ejecutar checklist de aceptacion.
2. Completar y firmar acta de traspaso.
3. Registrar observaciones de puesta en marcha.
