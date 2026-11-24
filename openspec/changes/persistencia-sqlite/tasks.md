# Tareas: persistencia SQLite y migración segura

- [ ] Revisar y aprobar esta spec (SDD).
- [ ] RED: crear prueba de migración con JSON mixto `Equipos` + `equipos`.
- [ ] Ejecutar y confirmar que hoy se pierde `PT-050` (fallo esperado).
- [ ] GREEN: implementar esquema, normalización y transacción de migración.
- [ ] RED: crear prueba de rollback ante fallo de validación.
- [ ] GREEN: implementar copia y restauración del flag.
- [ ] RED: crear prueba de 20 escrituras concurrentes.
- [ ] GREEN: añadir transacciones y restricciones de unicidad.
- [ ] REFACTOR: ejecutar suite completa + caracterización.
- [ ] Commit `feat: persistencia sqlite con migracion segura`.
