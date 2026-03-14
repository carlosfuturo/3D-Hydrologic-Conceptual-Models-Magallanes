# Instalacion en ambiente cliente

## 1. Prerrequisitos

- Sistema operativo: Windows 11 (ArcGIS Pro) o macOS/Linux (procesamiento).
- Python 3.11 recomendado.
- ArcGIS Pro instalado para visualizacion notebook 3D.
- Acceso a datos del proyecto y, si aplica, portal ArcGIS Online.

## 2. Preparacion

1. Copiar la carpeta completa `02 PyScripts Magallanes` al equipo del cliente.
2. Entrar a `Kit_Transferencia_Cliente`.
3. Ejecutar setup:

```bash
bash scripts/setup_env.sh
```

## 3. Configuracion

1. Editar `config/project_config.yaml`.
2. Editar `config/.env` (credenciales solo por variable de entorno).
3. Activar entorno:

```bash
source ../.venv_cliente/bin/activate
```

## 4. Validacion minima

```bash
bash scripts/run_smoke_test.sh
```

Si el smoke test pasa, el ambiente esta listo para ejecutar el proyecto.

## 5. Workspace editable de insumos

Si el cliente necesita modificar SHP, raster, CSV, XLSX o JSON sin tocar los scripts:

```bash
bash scripts/prepare_editable_inputs.sh
```

Luego editar los archivos dentro de `Editable_Inputs/` manteniendo la misma ruta relativa.
