# Registro de ejecución — C3 (persistencia SQLite y migración segura)

Change: `openspec/changes/persistencia-sqlite`. Requisitos: DAT-01..DAT-04, INT-03.

## RED 1 — persistencia y migración

Prueba creada primero: `tests/test_persistencia.py` (4 pruebas).

Comando: `python -m pytest tests/test_persistencia.py -v`.

Resultado: error de recolección —

```
ModuleNotFoundError: No module named 'prestatec.migracion'
```

## GREEN 1

1. `prestatec/sqlite_repository.py`: esquema versionado (`meta.schema_version = 1`),
   tablas `equipos`, `usuarios`, `prestamos`, `eventos`, llaves foráneas,
   `PRAGMA foreign_keys = ON` y triggers que garantizan integridad también en
   conexiones externas. `load()`/`save()` respetan el contrato de C1; `save()`
   usa `BEGIN IMMEDIATE` y un cerrojo reentrante por archivo.
2. `prestatec/migracion.py`: normaliza `Equipos`/`equipos`, `Usuarios`/`usuarios`,
   `Reservas`/`prestamos` y `Eventos`/`eventos` sin descartar registros. Copia
   el original antes de escribir y devuelve SHA-256 del respaldo. Escribe en un
   archivo temporal y solo después lo reemplaza atómicamente.

Resultado: **3 passed, 1 failed**. El fallo de concurrencia fue `IntegrityError:
integridad: equipo inexistente`, causado por códigos `PT-###` duplicados entre
hilos y eventos huérfanos.

## REFACTOR 1

`prestatec/service.py` incorpora `RLock` y el decorador `@_transaccional` en las
ocho operaciones que mutan estado. Así la generación de códigos, la modificación
y el guardado quedan dentro de la misma sección crítica.

Resultado: **4 passed in 0.58s**.

## RED 2 — backend conmutable

Prueba creada primero: `tests/test_configuracion.py` (2 pruebas).

Resultado: `ModuleNotFoundError: No module named 'prestatec.config'`.

## GREEN 2

1. `prestatec/config.py`: `Configuracion(backend, ruta_datos)` lee
   `PRESTATEC_BACKEND` (`json` por defecto) y `PRESTATEC_DATA_FILE`, y expone
   `repositorio()`.
2. `prestatec/web.py`: `PrestaTecApp` acepta `configuracion` e inyecta el
   repositorio en `InventoryService`. La lógica de negocio no cambió.

Resultado: **2 passed in 0.24s**.

## RED 3 — sobrescritura segura

Prueba añadida: `test_DAT02_rechaza_sobrescribir_destino_sin_autorizacion`.

Resultado: `Failed: DID NOT RAISE Exception`: la migración reemplazaba una base
preexistente.

## GREEN 3

`migrar_desde_json(..., sobrescribir=False)` verifica destino y respaldo antes de
copiar cualquier archivo y lanza `BusinessError` si existen sin autorización.

Resultado suite completa: **34 passed in 0.67s**.

## RED 4 — proceso explícito

Prueba creada primero: `tests/test_migracion_cli.py`.

Resultado: `ModuleNotFoundError: No module named 'migrar'`.

## GREEN 4

`migrar.py` expone `main(argv)` con `origen`, `destino`, `respaldo` y `--forzar`;
imprime el informe JSON con el hash del respaldo. Se añadió la tarea de VS Code
**PrestaTec: migrar data.json a SQLite** y la documentación en `README.md`.

Resultado final: **35 passed in 0.90s** (Python 3.14.10, pytest 9.2.0).

## Decisiones técnicas

- El número de versión se guarda en la tabla `meta` como `schema_version = '1'`;
  el diseño mencionaba una tabla aparte, pero esta forma evita una tabla de una
  sola fila y es equivalente para futuros chequeos.
- La integridad referencial se duplica en llaves foráneas y triggers porque
  `PRAGMA foreign_keys` es propio de cada conexión; así una herramienta externa
  también queda protegida (verificado en `test_DAT01`).
- El repositorio SQLite sigue guardando el estado completo, como el adaptador
  JSON de C1. La atomicidad y el bloqueo global por archivo compensan este
  diseño sin forzar una reescritura de reglas en este change.
- En claves mixtas prevalece el registro en formato actual cuando coincide el
  ID con uno legacy; ambos se conservan cuando los IDs son distintos.

## Límites

- No se ejecutó una migración sobre datos reales: no existe autorización para
  modificar `data.json` del workspace. Las pruebas usan directorios temporales.
- DAT-05/DAT-06 (restauración completa) pertenecen al change
  `respaldo-restauracion` y siguen pendientes.
- No se verificó recuperación ante un corte de energía durante `os.replace`.

## Estado

C3 completado para DAT-01..DAT-04. Rollback disponible revirtiendo el commit del
change; el backend por defecto continúa siendo `json`.
