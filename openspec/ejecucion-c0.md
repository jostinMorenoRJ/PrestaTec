# Registro de ejecución — C0 (gobernanza y línea base)

Fecha: 24/11/2026. Change: `openspec/changes/gobernanza-linea-base`.

## Acciones realizadas

1. Extracción del ZIP original `PrestaTec_Python.zip` al workspace.
   - `AGENTS.md.txt` conservado sin cambios.
   - Los documentos OpenSpec originales del ZIP se preservaron en `openspec/legacy/`:
     `prestamos-universidad/{proposal,design,tasks}.md` y `specs/prestamos/spec.md`.
   - No se sobrescribió `openspec/specs/prestamos/spec.md` creado en la Etapa 3.
2. Creación de `pyproject.toml` con `testpaths`, `--strict-markers` y los marcadores
   `unit`, `integration`, `acceptance`, `nfr`, `characterization`.
3. Creación de `AGENTS.md` a partir de `AGENTS.md.txt`, conservando las reglas
   originales íntegramente y añadiendo la sección OpenSpec/trazabilidad.
4. Creación de 7 pruebas de caracterización en
   `tests/characterization/test_estado_actual.py`.

## Evidencia de ejecución

Comando: `python -m pytest -v` (Python 3.14.10, pytest 9.2.0,
`PYTHONPATH` apuntando a la instalación temporal de pytest).

Resultado: **19 passed in 0.39s**.

| Grupo | Pruebas | Resultado |
|---|---|---|
| Caracterización C0 | 7 | 7 PASSED |
| Dominio original | 9 | 9 PASSED |
| HTTP original | 3 | 3 PASSED |

## Nota sobre RED en C0

C0 es un cambio de infraestructura, no de comportamiento. Las 7 pruebas de
caracterización describen el estado real del código original, por lo que nacen
en verde: **no se afirma que existió una fase RED de comportamiento en C0**.
La disciplina RED → GREEN → REFACTOR se aplicará desde C1 en adelante, donde
cada prueba nueva se ejecutará antes de escribir la implementación y se registrará
su fallo.

La condición RED de C0 fue únicamente la ausencia de andamiaje: antes de este
change no existían `pyproject.toml`, `AGENTS.md` ni `tests/characterization/`.

## Limitación bloqueante

**No se pudo inicializar Git.** El ejecutable `git` no está en el PATH y no se
encontró instalación local en las rutas habituales (`Program Files\Git`,
`Program Files (x86)\Git`, `AppData\Local\Programs\Git`).

En consecuencia:

- No existe `.git` en el workspace.
- No se creó el commit `chore: línea base y gobernanza`.
- El requisito `INT-07` y la tarea Git de C0 permanecen **pendientes**, no aprobadas.

No se instaló software ni se descargó Git sin autorización.

## Estado del change C0

| Elemento | Estado |
|---|---|
| Estructura OpenSpec (Etapas 3–4) | Completada |
| Extracción sin pérdida ni sobrescritura | Completada |
| Configuración pytest | Completada |
| `AGENTS.md` | Completado (`AGENTS.md.txt` conservado) |
| Pruebas de caracterización | Completadas (7/7) |
| Suite completa | Completada (19/19) |
| Git inicializado y commit | **Pendiente: Git no instalado** |
