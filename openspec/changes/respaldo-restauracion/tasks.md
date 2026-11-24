# Tareas: respaldo y restauración verificable

- [x] Revisar y aprobar esta spec (SDD).
- [x] RED: crear `tests/test_respaldo.py` (5 pruebas); fallo por ausencia de
      `prestatec.backup`.
- [x] GREEN: implementar `BackupService` con timestamp UTC, SHA-256 y conteos.
- [x] GREEN: añadir manifiesto verificable a la migración de C3.
- [x] GREEN: verificar 5/5; suite completa 40/40.
- [x] RED: añadir prueba de copia SQLite corrupta y de CLI respaldar.
- [x] REFACTOR: capturar `sqlite3.Error`; crear `respaldar.py`, tarea de VS Code
      y documentación en `README.md`.
- [x] REFACTOR: verificar que ninguna copia se purga (3 copias → 6 archivos).
- [x] Suite completa: **42 passed in 0.96s**.
- [x] Registrar evidencia en `openspec/ejecucion-c4.md`.
- [x] Commit `feat: respaldo y restauracion verificable (C4)` (ver `git log`).
