# Registro de ejecución — C1 (repositorio e inversión de dependencias)

Change: `openspec/changes/repositorio-interfaz`. Requisitos: ARQ-01, ARQ-02, INT-04.

## RED

Prueba creada primero: `tests/test_repositorio.py` (4 pruebas).

Comando: `python -m pytest tests/test_repositorio.py -v`.

Resultado: **error de recolección** —

```
ModuleNotFoundError: No module named 'prestatec.repository'
```

Evidencia de que el servicio aún no podía recibir un repositorio inyectado.

## GREEN

Cambio mínimo:

1. `prestatec/errors.py`: `BusinessError` extraído para evitar importación circular.
2. `prestatec/repository.py`: `Repository` (Protocol), `JsonFileRepository` y
   `estado_vacio()`. La lógica de lectura/legacy se trasladó sin cambiar su
   comportamiento, incluido el defecto P9.
3. `prestatec/service.py`: `InventoryService` acepta `repository`, delega en él
   y deja de importar `json` y `pathlib`. Se conservó el parámetro `data_file`
   por compatibilidad con las 19 pruebas existentes.
4. `BusinessError` se re-exporta desde `prestatec.service`, por lo que
   `web.py` y las pruebas originales siguen funcionando sin cambios.

Resultado: **4 passed in 0.17s**.

## REFACTOR

Se añadió la anotación `repository: Repository | None = None` para hacer
explícito el contrato en la firma del servicio. Sin cambios de comportamiento.

## Suite completa

- Tras GREEN: **23 passed in 0.29s**.
- Tras REFACTOR: **23 passed in 0.25s**.

Desglose: 7 caracterización + 9 dominio + 3 HTTP + 4 repositorio.

## Decisiones técnicas

- El contrato del repositorio es `load()` / `save()` del estado completo, no
  operaciones de dominio granulares. Esto mantiene C1 reversible y evita
  reescribir las reglas antes de introducir SQLite en C3.
- `JsonFileRepository(None)` resuelve a `data.json` en la raíz del proyecto.
- `BusinessError` vive en `errors.py` y se re-exporta desde `service.py` para
  no romper importaciones existentes.

## Estado

C1 completado. Sin migración de datos, sin cambios de esquema y sin cambios en
la interfaz. Rollback disponible revirtiendo el commit del change.
