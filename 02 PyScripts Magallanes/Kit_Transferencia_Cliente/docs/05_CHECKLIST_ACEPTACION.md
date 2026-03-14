# Checklist de aceptacion cliente

## A. Integridad de entrega

- [ ] Se recibio carpeta completa del proyecto.
- [ ] Se verifico manifiesto SHA256.
- [ ] Se validaron tamanos de carpetas criticas (SIG, DEM, figuras, texto).

## B. Entorno y dependencias

- [ ] Setup completado con `scripts/setup_env.sh`.
- [ ] Entorno virtual activable sin errores.
- [ ] Smoke test completado con `scripts/run_smoke_test.sh`.

## C. Ejecucion funcional

- [ ] Pipeline completo ejecutado con `scripts/run_full_pipeline.sh`.
- [ ] Se generan salidas en carpetas de figuras y texto.
- [ ] No hay errores criticos en log de ejecucion.

## D. Visor 3D ArcGIS Pro

- [ ] Notebook abre en ArcGIS Pro.
- [ ] Carga inicial de 4 modelos correcta.
- [ ] Selector de modelos funciona (HTML/JavaScript).
- [ ] Hover/leyenda/elementos 3D se visualizan correctamente.

## E. Portales y permisos (si aplica)

- [ ] Cuenta cliente con permisos correctos.
- [ ] Item IDs y URLs validados.
- [ ] Flujo de actualizacion AGOL probado.

## F. Cierre de traspaso

- [ ] Manual de instalacion entregado.
- [ ] Manual de operacion entregado.
- [ ] Troubleshooting entregado.
- [ ] Capacitacion realizada.
- [ ] Acta de aceptacion firmada.

## Registro de validacion

- Fecha:
- Responsable cliente:
- Responsable IDIEM:
- Observaciones:
- Resultado final: APROBADO / OBSERVADO
