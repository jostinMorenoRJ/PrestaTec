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

## Control de versiones

Inicialmente `git` no estaba instalado. Tras la autorización explícita del
usuario se instaló **Git 2.56.1.windows.1** mediante `winget` (paquete `Git.Git`,
con verificación de hash por el gestor).

- Repositorio inicializado en el workspace.
- Commit `8a92475 chore: linea base y gobernanza (C0)`.
- Configuración local de autor: `PrestaTec 2.0 <prestatec2@local.invalid>`.
- No se publicó en GitHub: no hay repositorio remoto ni autorización de publicación.

## Configuración para Visual Studio Code

El proyecto se preparó para abrir la carpeta directamente en VS Code:

- `.vscode/settings.json`: pytest habilitado sobre `tests/` y descubrimiento automático.
- `.vscode/launch.json`: depuración del servidor y de la suite pytest con el intérprete del entorno.
- `.vscode/tasks.json`: tareas "ejecutar pruebas" e "iniciar servidor" usando el intérprete activo.
- `README.md`: instrucciones de instalación, ejecución y pruebas adaptadas a este workspace.

## Estado del change C0

| Elemento | Estado |
|---|---|
| Estructura OpenSpec (Etapas 3–4) | Completada |
| Extracción sin pérdida ni sobrescritura | Completada |
| Configuración pytest | Completada |
| `AGENTS.md` | Completado (`AGENTS.md.txt` conservado) |
| Pruebas de caracterización | Completadas (7/7) |
| Suite completa | Completada (19/19) |
| Git inicializado y commit | Completado (`8a92475`) |
| Configuración VS Code | Completada |
