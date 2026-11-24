# Tareas: repositorio e inversión de dependencias

- [x] Revisar y aprobar esta spec (SDD).
- [x] RED: crear `tests/test_repositorio.py` (4 pruebas).
- [x] Ejecutar y confirmar fallo por ausencia de `prestatec.repository`.
- [x] GREEN: definir interfaz `Repository` y adaptador `JsonFileRepository`.
- [x] GREEN: inyectar el repositorio en `InventoryService`.
- [x] REFACTOR: eliminar imports de `json`/`Path` de los casos de uso; anotar el contrato.
- [x] Ejecutar suite completa + caracterización: **23 passed**.
- [x] Verificar que `data.json` no cambió de formato (ARQ-02).
- [x] Registrar evidencia en `openspec/evidencia/ejecucion-c1.md`.
- [x] Commit `refactor: repositorio sobre JSON (C1)` — `a9aef30` (verificado en `git log`).
