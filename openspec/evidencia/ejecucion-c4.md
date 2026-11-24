# Registro de ejecución — C4 (respaldo y restauración verificable)

Change: `openspec/changes/respaldo-restauracion`. Requisitos: DAT-05, DAT-06.

## RED

Prueba creada primero: `tests/test_respaldo.py` (5 pruebas).

Resultado: **5 failed** con `ModuleNotFoundError: No module named 'prestatec.backup'`.

## GREEN

1. `prestatec/backup.py`: `BackupService.crear()` guarda una instantánea con
   nombre UTC único y escribe un manifiesto con `creadoEn` (ISO 8601 UTC),
   `sha256`, `conteos` por entidad, tamaño y backend. `validar()` recalcula hash
   y conteos; `restaurar()` valida antes y después de reemplazar el destino.
2. `prestatec/migracion.py`: la migración escribe el manifiesto del respaldo
   antes de poblar SQLite y lo expone en `informe['respaldo']`.
3. No se implementó ninguna operación de borrado de copias.

Resultado: **5 passed in 0.37s**; suite completa: **40 passed in 0.98s**.

## REFACTOR

Se añadieron dos pruebas antes de tocar código:

- `test_DAT06_copia_sqlite_corrupta_se_rechaza`: primero pasó por el hash; se
  ajustó para recalcularlo y exponer el fallo real `sqlite3.DatabaseError`.
- `test_cli_backup_y_restore`: falló con `ModuleNotFoundError: No module named
  'respaldar'`.

Correcciones:

- `_estado()` captura `sqlite3.Error` y lo convierte en `BusinessError`.
- `respaldar.py` expone `crear` y `restaurar` con `--directorio` y `--confirmar`.
- Nueva tarea de VS Code **PrestaTec: crear respaldo verificable** y sección
  "Respaldos" en `README.md`.

Resultado final: **42 passed in 0.96s**.

## Decisiones técnicas

- El manifiesto se guarda como `<instantánea>.manifest.json`. La ruta se guarda
  también dentro del diccionario devuelto para poder validar sin conocer el
  nombre del archivo.
- Para contar entidades en copias JSON se reutiliza `normalizar()` de C3, así
  una copia con claves `Equipos` y `equipos` no pierde registros en el conteo.
- La fecha de modificación del destino se compara con `creadoEn`; si el destino
  es más reciente, `restaurar()` exige `confirmar=True`. Es una salvaguarda,
  no una política institucional.
- `--confirmar` representa la autorización explícita del operador mientras no
  exista un flujo de aprobación por rol (C5).

## Límites

- No se crearon respaldos de datos reales: las pruebas usan `tmp_path`.
- No se probó corrupta una copia SQLite con el mismo hash; se probó el rechazo
  por `sqlite3.DatabaseError` tras igualar hashes.
- DEC-06 sigue abierta: no se define retención ni purga.

## Estado

C4 completado. Rollback disponible revirtiendo el commit del change.
