# Ejecución C13 — acceso visible y cuentas de demostración

**Fecha:** 2026-11-24
**Commit:** `2be8cd9` (implementación), `docs:` (referencias de trazabilidad)
**Change:** `openspec/changes/acceso-y-cuentas-demo/`
**Spec:** `openspec/changes/acceso-y-cuentas-demo/specs/acceso/spec.md` (ACC-01..ACC-04)
**Decisión del usuario:** `admin`/`admin123` → Encargado, `celador`/`celador123`
→ Guarda, `estudiante`/`estudiante123` → Consulta; además, cambiar el front de
inicio de sesión porque parecía una ventana vacía.

## RED

Se creó `tests/test_acceso.py` **antes** de modificar `static/` o las
credenciales. Comando:

```powershell
$env:PYTHONPATH='C:\Users\spect\AppData\Local\Temp\opencode\pytest-libs'
python -m pytest tests/test_acceso.py -q
```

Resultado observado: `FFFFF` — 5 pruebas, 5 fallos. Confirmaron que `admin`
seguía con rol `Administrador`, que no existía `#acceso`, que el formulario
estaba en la barra superior y que no había etiquetas ni mensaje de error.
No se volvió a ejecutar la fase RED tras corregir un error del propio test: la
respuesta de `POST /api/reservas` no incluye `documento`, así que ahora se
verifica el préstamo persistido (igual que en PER-03).

## GREEN

- **Datos:** respaldo previo de `identidades.json` y `data.json` en
  `C:\Users\spect\AppData\Local\Temp\opencode\`
  (`*-antes-c13-20261124T202950Z.json`). Se sustituyeron `admin`,
  `1001234567`, `900001` y `52111222` por las tres cuentas pedidas, con
  `AlmacenCredenciales.crear()` (PBKDF2, roles validados). Se añadieron los
  usuarios de negocio `admin`, `celador` y `estudiante`; este último es
  necesario para que la cuenta `Consulta` pueda reservar.
- **Interfaz:** nuevo `<section id="acceso">` con dos columnas (marca y
  beneficios / tarjeta de acceso). `#fl` salió del `header`; conserva
  `name="documento"` y `name="contraseña"` para no cambiar el contrato de
  `/api/auth/login`. La tarjeta lista usuario, clave y perfil de las tres
  cuentas.
- **Estado:** `aplicarPermisos()` oculta `#acceso` cuando hay sesión y enfoca
  `#usuario` cuando no la hay; `body.sin-sesion` oculta `header` y `main`.
- **Errores:** `#error-acceso` muestra `Credenciales inválidas.` dentro de la
  tarjeta, sin ocultar el formulario.

Resultado:

```
5 passed in 0.38s
```

## REFACTOR

No fue necesario modificar pruebas antiguas: las de C5/C12 siguen usando
archivos temporales y no dependen del formulario de la barra. La suite completa:

```
77 passed in 4.26s
```

## Verificación en navegador

Servidor temporal en el puerto 5082 con los archivos reales del proyecto, sin
modificar datos durante la navegación (solo sesiones en memoria).

| Comprobación | Resultado |
|---|---|
| Abrir raíz sin sesión | `#acceso` visible; `header` y `main` ocultos; título “Iniciar sesión” |
| Cuentas mostradas | `Encargado admin admin123`, `Guarda celador celador123`, `Consulta estudiante estudiante123` |
| Contraseña incorrecta | `#error-acceso` visible con “Credenciales inválidas.”; formulario sigue visible |
| `admin` / `admin123` | “Panel general”, perfil `EncargadoAdmin`, `#acceso` oculto, vista `v-panel` |
| `celador` / `celador123` | “Control de portería”, perfil `GuardaCelador`, vista `v-porteria` |
| `estudiante` / `estudiante123` | “Mi espacio”, perfil `ConsultaEstudiante`, vista `v-mis` |
| Cerrar sesión | La pantalla de acceso vuelve a aparecer para cada cuenta |

Los únicos errores de consola fueron los esperados: `/api/auth/me` sin cookie
al abrir y el `/api/auth/login` con contraseña incorrecta de prueba. No hubo
errores durante los tres ingresos válidos ni al cambiar de vista.

## Decisiones técnicas

- `admin` se mapea a `Encargado`, no a `Administrador`: ese rol fue eliminado en
  C12 por decisión del usuario y no se reincorpora.
- Las contraseñas aparecen en la pantalla solo por ser credenciales locales de
  demostración. Si se despliega el sistema, debe retirarse el bloque
  `.acceso-cuentas` y cambiar las claves.
- No se configuró remoto ni se hizo push: sigue vigente la decisión de solo
  commit local.
- DEC-01..DEC-09, SSO y hardware real de lectores siguen pendientes y sin
  inventar políticas.

## Credenciales anteriores

Quedaron registradas en los respaldos indicados arriba. Las credenciales
temporales anteriores (`1001234567`/`Consulta2026!`, `900001`/`Guarda2026!`,
`52111222`/`Encargado2026!`)
fueron sustituidas por decisión del usuario; no se borraron otros datos.
