# Tareas: gobernanza y línea base

## Ejecutadas

- [x] Revisar y aprobar esta spec (SDD) — Etapas 3 y 4.
- [x] Extraer el ZIP original al workspace sin sobrescribir `AGENTS.md.txt`.
- [x] Preservar los OpenSpec originales del ZIP en `openspec/legacy/`.
- [x] Crear `pyproject.toml` con configuración pytest y marcadores.
- [x] Crear `AGENTS.md` a partir de `AGENTS.md.txt` y documentar la decisión.
- [x] Crear `tests/characterization/test_estado_actual.py` (7 pruebas).
- [x] Ejecutar la suite completa: **19 passed in 0.39s**.
- [x] Registrar evidencia y limitaciones en `openspec/ejecucion-c0.md`.

## Pendientes

- [ ] Inicializar repositorio Git — **bloqueado**: `git` no está instalado ni
      disponible en el PATH. No se creó `.git` ni el commit.
- [ ] Commit descriptivo `chore: línea base y gobernanza` una vez resuelto lo anterior.

> Nota: C0 es infraestructura. Las pruebas de caracterización documentan el
> comportamiento actual y nacen en verde; no se afirma una fase RED de
> comportamiento. RED → GREEN → REFACTOR se aplica desde C1.
