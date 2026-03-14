# Kit de Transferencia al Cliente - Proyecto Magallanes

Este kit permite instalar, validar y ejecutar el proyecto completo en el ambiente del cliente, incluyendo el flujo de scripts y el visor 3D en ArcGIS Pro.

## Contenido del kit

- `config/`: plantillas de configuracion local.
- `scripts/`: setup, smoke test, ejecucion full, manifiesto y empaquetado final.
- `docs/`: guias de instalacion, operacion y troubleshooting.
- `requirements_cliente.txt`: dependencias Python con pines minimos.
- `environment_cliente.yml`: alternativa con Conda.
- `Editable_Inputs/` (opcional): workspace editable para overrides de SHP, raster y datasets.

## Flujo recomendado de traspaso

1. Instalar entorno Python con `scripts/setup_env.sh`.
2. Completar `config/project_config.yaml` desde la plantilla.
3. Ejecutar validacion minima con `scripts/run_smoke_test.sh`.
4. Ejecutar corrida completa con `scripts/run_full_pipeline.sh`.
5. Generar manifiesto de integridad con `scripts/generate_manifest.sh`.
6. Preparar inputs editables con `scripts/prepare_editable_inputs.sh` si el cliente necesita modificar insumos.
7. Empaquetar entrega cliente con `scripts/package_delivery.sh`.
8. Generar paquete MASTER completo de `01 Magallanes` con `scripts/package_master_workspace.sh`.
9. Validar con checklist en `docs/05_CHECKLIST_ACEPTACION.md`.
10. Firmar acta de traspaso en `docs/07_ACTA_TRASPASO.md`.

## Ejecucion rapida

```bash
cd "02 PyScripts Magallanes/Kit_Transferencia_Cliente"
bash scripts/setup_env.sh
cp config/project_config.example.yaml config/project_config.yaml
bash scripts/run_smoke_test.sh
bash scripts/run_full_pipeline.sh
bash scripts/generate_manifest.sh
bash scripts/prepare_editable_inputs.sh
bash scripts/package_delivery.sh
bash scripts/package_master_workspace.sh
```

## Nota ArcGIS Pro

El visor 3D recomendado para cliente usa el notebook con `data:text/html;base64` + selector JavaScript, sin dependencia de callbacks Python de widgets.

Detalles en `docs/03_ARCGISPRO_VISOR_3D.md`.
