# Índice de openspec

Para revisar **solo el núcleo pedido**, en este orden:

1. `specs/prestamos/spec.md` — requisitos RF01–RF09.
2. `changes/devolucion-responsable/` — ciclo 1 (DEV): spec → test → código.
3. `changes/devolucion-unica/` — ciclo 2 (DUP): spec → test → código → refactor.

Los dos deltas (`specs/` dentro de cada change) y sus `tasks.md` tienen las
casillas `[x]` de lo ya completado.

## Se puede ignorar

- `ejecucion-c0.md` … `ejecucion-c13.md`: evidencia de incrementos anteriores.
- Los changes C0–C13 y su índice en `changes/README.md`: extras opcionales
  (autenticación, SQLite, respaldos, perfiles, acceso local).
- `legacy/`: documentación original del proyecto previo.

La relación completa requisito → spec → prueba → implementación está en
`trazabilidad.md`. El detalle de los dos ciclos del núcleo está en
`ejecucion-nucleo-dev.md` y `ejecucion-devolucion-unica.md`.
