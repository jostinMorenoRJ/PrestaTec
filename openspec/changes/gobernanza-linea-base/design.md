# Diseño: gobernanza y línea base

## Enfoque
No tocar `prestatec/`, `web.py`, `static/` ni `data.json`. Solo crear
infraestructura de proyecto: Git, configuración de pruebas, `AGENTS.md` y
pruebas de caracterización en `tests/characterization/`.

## Decisiones técnicas
- `pyproject.toml` concentrará `[tool.pytest.ini_options]` con `testpaths = ["tests"]`,
  marcadores `unit|integration|acceptance|nfr|characterization` y `--strict-markers`.
- Las pruebas de caracterización usarán `tmp_path`; nunca `data.json` real.
- Se conservará `AGENTS.md.txt` como histórico y se creará `AGENTS.md` con el
  mismo contenido más la referencia a OpenSpec. No se eliminará el original sin
  aprobación (INT-03).

## Riesgos y mitigación
- Riesgo: confundir caracterización con spec definitiva. Mitigación: marcar cada
  prueba con `@pytest.mark.characterization` y documentar que describe el estado
  actual, aunque tenga defectos conocidos (por ejemplo, conflicto 400).

## Compatibilidad
Sin migración de datos. Sin cambios de runtime.
