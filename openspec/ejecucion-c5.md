# Registro de ejecución — C5 (identidad y control de acceso)

Change: `openspec/changes/identidad-rbac`. Requisitos: SEC-01..SEC-04,
PDF-RNF01, RES-02. Matriz aprobada por el usuario como decisión técnica
temporal: `Estudiante`/`Docente` → `Consulta`.

## RED

Prueba creada primero: `tests/test_seguridad.py` (6 pruebas), antes de
`prestatec/identidad.py` y de exigir autenticación en `prestatec/web.py`.

Comando: `python -m pytest tests/test_seguridad.py -v`.

Resultado: **1 error de recolección** con
`ModuleNotFoundError: No module named 'prestatec.identidad'`.

Tras implementar el proveedor, una prueba falló por un artefacto de la prueba
(`db.json` no existía porque no se había escrito aún); se corrigió la prueba,
no el código de producción. Resultado: **6 passed**.

Al exigir autenticación, la suite existente mostró **9 failed** (7 de
caracterización y 2 de `test_web.py`) por peticiones anónimas. Ese fue el RED
del cambio deliberado de comportamiento documentado en C0.

## GREEN

1. `prestatec/identidad.py`: `Identidad`, `Autorizador`, matriz aprobada,
   `AlmacenCredenciales` con PBKDF2-SHA-256 (210000 iteraciones, salt aleatorio)
   y `ProveedorIdentidadLocal` con sesiones firmadas HMAC.
2. `prestatec/web.py`: `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`;
   toda ruta `/api/...` (excepto login) exige identidad y devuelve 401 si no
   hay sesión; las acciones sin permiso devuelven 403.
3. `prestatec/service.py`: el caso de uso vuelve a comprobar permisos cuando
   recibe `actor`; las pruebas de dominio sin actor permanecen válidas.
4. `run.py`: `crear_handler(app)`propaga cabeceras de petición y `Set-Cookie`.

Resultado intermedio: `tests/test_seguridad.py` **6 passed**.

## REFACTOR

Se añadieron pruebas antes de código:

- `tests/test_autorizacion_casos_uso.py` (3 pruebas): falló con
  `DID NOT RAISE SinPermiso` en registro de usuario y cambio de estado.
- `tests/test_seguridad.py::test_RNF01_perfil_de_sesion_expone_permisos`: falló
  con `404 != 200`.
- `tests/test_run_http.py`: falló con
  `ImportError: cannot import name 'crear_handler' from 'run'`.
- `tests/test_identificar_cli.py`: falló con
  `ModuleNotFoundError: No module named 'identificar'`.
- `test_RNF01_rol_explicito_de_credencial_prevalece_sobre_rol_historico`: falló
  con `AssertionError: 'Consulta' != 'Administrador'`.

Resultado RED acumulado: **4 failed, 7 passed** + 1 error de recolección;
después, **1 failed, 8 passed** en `test_seguridad.py`.

Correcciones:

- `InventoryService` recibe un `Autorizador` inyectable y aplica la matriz en
  registro de recursos, entrega, devolución, daño, cambio de estado,
  cancelación y verificación de portería.
- `/api/auth/me` devuelve identidad y lista de permisos; la interfaz oculta
  acciones sin permiso en lugar de dejar botones que siempre fallan.
- `run.py` envía `Set-Cookie` y reenvía la cookie de la petición al enrutador.
- `identificar.py` crea credenciales con contraseña pedida por consola o desde
  `PRESTATEC_ADMIN_PASSWORD`, sin imprimirla y sin sobrescribir una credencial
  existente.
- `ProveedorIdentidadLocal.identidad()` prioriza el rol explícito de la
  credencial sobre el rol histórico del usuario de negocio; `test_RNF01_token_invalido_recibe_401`
  confirma que un token malformado devuelve 401.
- `tests/helpers.py` centraliza la autenticación de pruebas; `test_web.py`,
  `test_configuracion.py` y la caracterización usan archivos de identidad en
  `tmp_path` y cabeceras de sesión.
- La caracterización de acceso anónimo cambió de 200 a 401 por la spec C5.

Resultado final: **57 passed in 4.34s**.

## Verificación en navegador

Servidor iniciado con `PRESTATEC_IDENTITY_FILE` y `PRESTATEC_DATA_FILE` en
`C:\Users\spect\AppData\Local\Temp\opencode\`, sin tocar `data.json` real.

- Sin sesión: solo se mostró el formulario de ingreso; `/api/auth/me` respondió
  401 y el panel quedó oculto.
- `Administrador`: panel visible, reporte y Portería visibles; en Inventario
  tenía 6 selectores de estado, 6 botones de historial y formulario de alta.
- `Guarda`: panel y Portería visibles, reporte oculto; en Inventario 0
  formularios de alta, 0 historiales y 0 selectores de estado; 6 etiquetas QR.
- Cierre de sesión volvió al formulario de ingreso.

No se probaron lectores de hardware ni SSO (DEC-07).

## Decisiones técnicas

- El token de sesión se envía en cookie `HttpOnly; SameSite=Lax`; el secreto se
  lee de `PRESTATEC_SESSION_SECRET` o se genera al arrancar. Sin variable, un
  reinicio invalida las sesiones: es aceptable en local y evita guardar un
  secreto en el repositorio.
- La contraseña nunca se escribe en `data.json` ni en `identidades.json`; solo
  se guardan `salt`, `hash`, `iteraciones` y `rol`.
- Las credenciales se guardan en `identidades.json`, ignorado por Git.
- El proveedor local es intercambiable: `PrestaTecApp(identidad=...)` acepta
  cualquier objeto con `autenticar()` y `resolver()`.

## Límites

- No se implementó SSO, recuperación de contraseña ni expiración configurable.
- La duración de la sesión (8 h) es un valor técnico, no una política
  institucional.
- La matriz quedó aprobada para esta iteración; si la universidad define otra,
  se cambia `MATRIZ`/`Autorizador`, no las reglas de negocio.

## Estado

C5 completado. Rollback disponible revirtiendo el commit del change.
