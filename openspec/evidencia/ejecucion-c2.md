# Registro de ejecución — C2 (reloj UTC y políticas inyectables)

Change: `openspec/changes/reloj-politicas`. Requisitos: ARC-03, ARC-04.

## RED

Prueba creada primero: `tests/test_reloj.py` (4 pruebas).

Resultado: `ModuleNotFoundError: No module named 'prestatec.politicas'`.

## GREEN

1. `prestatec/reloj.py`: `a_utc()`, `Reloj` y `RelojFalso`.
2. `prestatec/politicas.py`: contenedor `Politicas` con todos los valores en `None`.
3. `prestatec/service.py`: `InventoryService` acepta `reloj` y `politicas`;
   toda lectura de hora pasa por `self.reloj.ahora()`; las fechas se normalizan
   a UTC antes de compararse y se almacenan como ISO 8601 con `+00:00`.

Resultado: **4 passed in 0.11s**.

## REFACTOR

- `resumen()` reescrito como diccionario multilínea y con guardas para valores
  `inicio`/`fin` ausentes en registros legacy.
- Verificación por grep: `prestatec/service.py` ya no contiene `datetime.now()`,
  `fromisoformat`, `import json` ni `write_text`.

Resultado: **27 passed in 0.27s** (7 caracterización + 12 originales +
4 repositorio + 4 reloj).

## Consecuencias controladas

- El formato de `data.json` cambia solo en que los timestamps nuevos incluyen
  `+00:00`. Los registros existentes siguen legibles porque `a_utc()` acepta
  cadenas naive y conscientes.
- Ninguna política tiene valor: DEC-01..DEC-06 continúan abiertas y no se
  aplica duración máxima, anticipación, sanción ni retención.

## Estado

C2 completado. Rollback disponible revirtiendo el commit del change.
