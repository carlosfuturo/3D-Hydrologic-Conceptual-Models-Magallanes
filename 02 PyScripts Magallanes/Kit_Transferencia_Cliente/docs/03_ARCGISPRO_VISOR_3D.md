# Visor 3D en ArcGIS Pro

## Estrategia recomendada

Usar notebook con modelo embebido en `data:text/html;base64` y selector JavaScript en HTML.

Esto evita fallas de callbacks Python de widgets dentro del motor restringido de notebooks en ArcGIS Pro.

## Pasos de uso

1. Abrir ArcGIS Pro.
2. Abrir `3ds ArcGIS Pro/02_notebook_viewer.ipynb`.
3. Conectar al portal configurado (si aplica).
4. Ejecutar la celda principal (Shift+Enter).
5. Cambiar entre modelos con el selector HTML.

## Actualizacion de modelos

1. Regenerar HTML de modelos con `07_mapa_3d_leapfrog.py`.
2. Re-ejecutar la celda del notebook.
3. Si el notebook AGOL se usa como respaldo, actualizar con el script de update.

## Recomendaciones operativas

- No depender de callbacks de `ipywidgets` para selector.
- No usar `file://` en iframe.
- No usar enlaces `target="_blank"` para abrir modelos desde notebook.
