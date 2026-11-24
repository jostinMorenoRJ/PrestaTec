# Tareas: gobernanza y línea base

## Ejecutadas

- [x] Revisar y aprobar esta spec (SDD) — Etapas 3 y 4.
- [x] Extraer el ZIP original al workspace sin sobrescribir `AGENTS.md.txt`.
- [x] Preservar los OpenSpec originales del ZIP en `openspec/legacy/`.
- [x] Crear `pyproject.toml` con configuración pytest y marcadores.
- [x] Crear `AGENTS.md` a partir de `AGENTS.md.txt` y documentar la decisión.
- [x] Crear `tests/characterization/test_estado_actual.py` (7 pruebas).
- [x] Ejecutar la suite completa: **19 passed in 0.39s**.
- [x] Registrar evidencia y limitaciones en `openspec/evidencia/ejecucion-c0.md`.

- [x] Instalar Git 2.56.1 con autorización explícita (`winget`, paquete `Git.Git`).
- [x] Inicializar repositorio Git en el workspace.
- [x] Commit descriptivo `8a92475 chore: linea base y gobernanza (C0)`.
- [x] Preparar `.vscode/` y `README.md` para ejecutar el proyecto en Visual Studio Code.
- [x] Verificar la suite completa tras la configuración: **19 passed**.

> Nota: C0 es infraestructura. Las pruebas de caracterización documentan el
> comportamiento actual y nacen en verde; no se afirma una fase RED de
> comportamiento. RED → GREEN → REFACTOR se aplica desde C1.
