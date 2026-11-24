# Ejecución C12 — perfiles por rol y experiencia de usuario

**Fecha:** 2026-11-24
**Commit:** `9eef23d` (implementación), `docs:` (referencias de trazabilidad)
**Change:** `openspec/changes/perfiles-y-experiencia/`
**Spec:** `openspec/changes/perfiles-y-experiencia/specs/perfiles/spec.md` (PER-01..PER-07)
**Decisiones del usuario:** tres roles (`Consulta`, `Guarda`, `Encargado`),
eliminación de `Administrador`/`Soporte`, reserva solo para el documento propio
y commit local sin push.

## RED

Se creó `tests/test_perfiles.py` **antes** de modificar código de producción.
Comando (pytest instalado fuera del proyecto, en la ruta temporal indicada):

```powershell
$env:PYTHONPATH='C:\Users\spect\AppData\Local\Temp\opencode\pytest-libs'
python -m pytest tests/test_perfiles.py -q
```

Resultado observado: `FF.FFFFFFFFFFFF` — 15 pruebas, 14 fallos y 1 pase.
Los fallos confirmaron: roles eliminados aceptados, login de `Administrador`
permitido, ausencia de `vistaInicial`, reservas para terceros, ausencia de
`/api/mis-prestamos`, acceso de Consulta a resumen/usuarios, conflictos `400`
sin alternativas, CSV con el ID en vez del nombre, `estadoEntrega` no
persistido, verificación de portería sin auditoría y JSON mixto incompleto.

Nota de honestidad: la prueba `test_PER02` tenía un error en el propio test
(`for documento, rol in esperado` sobre un diccionario). Se corrigió antes de
seguir; no se volvió a ejecutar la fase RED tras esa corrección, por lo que el
fallo real de `vistaInicial` se confirmó en la fase GREEN siguiente.

## GREEN

Cambios mínimos para satisfacer las pruebas:

- `prestatec/errors.py`: `ConflictoReserva` con `alternativas`.
- `prestatec/identidad.py`: `ROLES_PERMITIDOS`, `ROLES_LEGACY`, `VISTAS_INICIALES`,
  matriz de 10 permisos, `normalizar_rol()` y rechazo de roles eliminados.
- `prestatec/service.py`: `SOLICITAR_PRESTAMO`, alternativas en el conflicto,
  `estadoEntrega` persistido, `documento` en los listados y auditoría de toda
  verificación de portería.
- `prestatec/repository.py`: normalización de claves legado sin descartar las
  claves nuevas; duplicados resueltos a favor de la clave nueva.
- `prestatec/web.py`: `/api/mis-prestamos`, `vistaInicial`, permisos por ruta,
  documento de sesión en `POST /api/reservas`, `409` y CSV con nombre de equipo.
- `identificar.py`: roles explícitos, `Encargado` por defecto.
- `static/index.html`, `static/app.js`, `static/styles.css`: vistas por perfil.

Resultado:

```
15 passed in 0.96s
```

## REFACTOR

La suite completa mostró 21 fallos en pruebas anteriores que todavía usaban
`Administrador` o documentaban defectos ya corregidos. Se actualizaron con
trazación a la nueva spec:

- `tests/helpers.py`: perfil por defecto `Encargado`; `Consulta` explícita para
  solicitar préstamos.
- `tests/test_autorizacion_casos_uso.py`, `tests/test_seguridad.py`,
  `tests/test_web.py`, `tests/test_run_http.py`, `tests/test_configuracion.py`,
  `tests/test_identificar_cli.py`: sustitución de `Administrador` y separación
  entre solicitante (`Consulta`) y operador (`Encargado`).
- `tests/characterization/test_estado_actual.py`: los casos P3/P6/P8/P9 pasan a
  documentar el nuevo comportamiento con nota del cambio deliberado y referencia
  a PER-03/PER-05/PER-06. No se borró ninguna prueba: se renombró y explicó.
- `prestatec/identidad.py`: se restauró la inferencia de rol desde el usuario de
  negocio cuando la credencial no especifica rol (comportamiento C5 que la
  validación estricta de C12 había roto).

Resultado final de la suite completa:

```
72 passed in 3.81s
```

## Verificación en navegador

Servidor temporal con rutas explícitas a archivos de prueba (no se tocaron
`data.json` ni `identidades.json` del proyecto). Credenciales temporales:
`1001234567` (Consulta), `ui-guarda` (Guarda) y `52111222` (Encargado).

| Perfil | Navegación observada | Vista inicial | Comprobación |
|---|---|---|---|
| Consulta | `Mis préstamos` | `v-mis`, título “Mi espacio” | El formulario llamó a `/api/disponibilidad?...` (200) y mostró 3 equipos libres |
| Guarda | `Préstamos`, `Portería` | `v-porteria`, título “Control de portería” | `PT-002` → “Autorizado … Ana Torres”, registro en el log y evento de auditoría |
| Encargado | `Resumen`, `Inventario`, `Préstamos`, `Portería`, `Usuarios` | `v-panel`, título “Panel general” | Inventario 6 filas; Préstamos, Portería, Usuarios y Resumen renderizan sin errores de consola |

**Defecto detectado y corregido durante esta verificación:** los botones de la
barra de navegación no tenían controlador (`show()` existía pero no estaba
enlazado). Se añadió `$$('nav button').forEach(b => b.onclick = ...)` y una
prueba de regresión en `test_PER07_ui_tres_perfiles_y_disponibilidad`. Tras el
arreglo, la navegación entre todas las vistas funciona y no hay errores de
consola. Este hallazgo confirma que la verificación en navegador es necesaria
además de las pruebas estáticas.

## Decisiones técnicas

- No se purgan credenciales heredadas: dejan de resolver identidad, sin borrar
  archivos. `admin` con rol `Administrador` ya no autentica.
- No se inventan aprobación, plazos, sanciones ni notificaciones: DEC-01..DEC-09
  siguen pendientes.
- No se configura remoto ni se hace push: el usuario eligió solo commit local.
- Se conserva la separación de capas y el proveedor de identidad intercambiable
  (SEC-04).

## Pendiente que no cambió

SSO institucional, hardware real de QR/lectores, notificaciones y decisiones
DEC-01..DEC-09 permanecen fuera de alcance, documentados en
`openspec/specs/requisitos-institucionales/spec.md` y `openspec/legacy/`.
