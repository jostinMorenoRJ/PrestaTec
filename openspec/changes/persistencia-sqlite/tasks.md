# Tareas: persistencia SQLite y migración segura

## RED → GREEN → REFACTOR — persistencia

- [x] Revisar y aprobar esta spec (SDD).
- [x] RED: crear `tests/test_persistencia.py` (4 pruebas). El fallo fue
      `ModuleNotFoundError: No module named 'prestatec.migracion'`.
- [x] La prueba de caracterización C0 ya documentaba la pérdida de `PT-050`
      con claves mixtas; no se repitió artificialmente aquí.
- [x] GREEN: implementar `SQLiteRepository` con esquema versionado, llaves
      foráneas, triggers y transacciones.
- [x] GREEN: implementar `migrar_desde_json` con copia, hash y normalización
      simultánea de formatos legacy y actual.
- [x] GREEN parcial: 3/4; la concurrencia produjo IDs duplicados.
- [x] REFACTOR: serializar las ocho mutaciones del dominio con `RLock`.
- [x] Verificar 4/4 en `tests/test_persistencia.py`.

## RED → GREEN — backend conmutable

- [x] RED: crear `tests/test_configuracion.py`; fallo por ausencia de
      `prestatec.config`.
- [x] GREEN: `Configuracion` con `PRESTATEC_BACKEND` / `PRESTATEC_DATA_FILE`.
- [x] GREEN: inyectar el repositorio desde `PrestaTecApp` sin tocar reglas.

## RED → GREEN — seguridad de datos

- [x] RED: añadir prueba de destino preexistente; la migración no lanzaba error.
- [x] GREEN: rechazar sobrescritura de destino/respaldo sin `sobrescribir=True`.
- [x] RED: crear `tests/test_migracion_cli.py`; fallo por ausencia de `migrar`.
- [x] GREEN: crear `migrar.py`, tarea de VS Code y documentación en `README.md`.
- [x] Suite completa: **35 passed in 0.90s**.

## Pendientes (fuera de este change)

- [ ] DAT-05/DAT-06: restauración completa — change `respaldo-restauracion`.
- [ ] Comprobación de recuperación ante fallo durante el reemplazo atómico.

## Commit

- [x] Commit `feat: persistencia sqlite con migracion segura (C3)` (ver `git log`).

> Evidencia detallada en `openspec/ejecucion-c3.md`.
