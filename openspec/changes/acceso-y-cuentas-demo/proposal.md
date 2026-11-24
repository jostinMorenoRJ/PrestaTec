# Cambio C13 — acceso visible y cuentas de demostración

## Problema

Al abrir la aplicación sin sesión, `body.sin-sesion main { display:none }` oculta
todo el contenido y deja únicamente un formulario pequeño dentro de la barra
superior. La pantalla parece una ventana vacía y no indica qué usuario o
contraseña usar. Además, las credenciales vigentes (documentos numéricos) no
son memorizables para una prueba rápida.

## Decisión del usuario

Tres cuentas fijas y conocidas:

| Usuario | Contraseña | Perfil operativo |
|---|---|---|
| `admin` | `admin123` | `Encargado` |
| `celador` | `celador123` | `Guarda` |
| `estudiante` | `estudiante123` | `Consulta` |

`admin` pasa a ser `Encargado`: el rol `Administrador` fue eliminado en C12 y
no se reincorpora. Los nombres de usuario son literales, no cédulas.

## Alcance

- Reemplazar esas tres credenciales en `identidades.json` (con respaldo previo).
- Dar de alta `estudiante` como usuario de negocio para que pueda reservar.
- Sustituir el formulario de la barra por una pantalla de acceso completa,
  con la lista de cuentas de demostración visible.

## Fuera de alcance

- Cambiar la matriz de permisos o los roles definidos en C12.
- Publicar credenciales en Git (`identidades.json` sigue ignorado).
- SSO, recuperación de contraseña o gestión de cuentas desde la UI.
