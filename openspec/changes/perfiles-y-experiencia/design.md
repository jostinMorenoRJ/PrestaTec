# Diseño técnico — perfiles y experiencia (C12)

## Arquitectura

Se conserva la separación C0–C5: `repository.py` (persistencia), `service.py`
(reglas), `web.py` (HTTP), `identidad.py` (autenticación/RBAC) y `static/`
(interfaz). No se añaden dependencias externas de Python.

## Roles y matriz

| Permiso | Consulta | Guarda | Encargado |
|---|---|---|---|
| `SOLICITAR_PRESTAMO` | Sí | No | No |
| `VERIFICAR_PORTERIA` | No | Sí | Sí |
| `ENTREGAR_DEVOLVER` | No | Sí | Sí |
| `CREAR_RECURSO` | No | No | Sí |
| `REGISTRAR_DANO` | No | No | Sí |
| `HABILITAR` | No | No | Sí |
| `EXPORTAR` | Sí | No | Sí |
| `CONSULTAR_HISTORIAL` | Sí | No | Sí |
| `VER_RESUMEN` | No | Sí | Sí |
| `VER_USUARIOS` | No | No | Sí |

`Administrador` y `Soporte` desaparecen de `ROLES_LEGACY`, de la matriz, de la
CLI y de la documentación. La normalización `normalizar_rol()` devuelve `None`
para cualquier rol no permitido; `AlmacenCredenciales.crear()` lo rechaza y
`ProveedorIdentidadLocal.autenticar()` impide el ingreso si la credencial tiene
un rol inválido. Los archivos existentes no se eliminan: esas credenciales
simplemente dejan de resolver identidad.

## Vistas por perfil

| Rol | `vistaInicial` | Navegación | Acción principal |
|---|---|---|---|
| Consulta | `mis` | Mis préstamos | Buscar disponibilidad y reservar para su documento |
| Guarda | `porteria` | Portería, Préstamos | Validar QR/cédula; entregar y recibir |
| Encargado | `gestion` | Resumen, Inventario, Préstamos, Usuarios, Portería | Gestionar inventario, préstamos, daños y reportes |

La UI deriva la navegación de `/api/auth/me` y del rol. `show(v)` rechaza vistas
fuera de la lista del perfil, de modo que no queden botones ni acciones que
siempre fallan.

## Cambios por módulo

- `identidad.py`: roles permitidos, normalización, matriz reducida y
  `vistaInicial` calculada en `/api/auth/me`.
- `web.py`: autorización por permiso en cada ruta, `/api/mis-prestamos`, manejo
  de `ConflictoReserva` como `409` y CSV con nombre de equipo.
- `service.py`: `SOLICITAR_PRESTAMO`, `documento` en listados, persistencia de
  `estadoEntrega`, alternativas en el conflicto y auditoría de portería.
- `errors.py`: `ConflictoReserva` con `alternativas`.
- `repository.py`: normalización de legado sin descartar claves nuevas.
- `identificar.py`: roles explícitos en la CLI; `Encargado` por defecto.
- `static/`: nueva sección “Mis préstamos”, rediseño visual y consumo de
  `/api/disponibilidad`.

## Compatibilidad y migración

- `data.json`/SQLite no se modifican estructuralmente; se añaden campos
  opcionales (`estadoEntrega`) que el código antiguo ya ignoraba.
- `identidades.json` no se purga. La credencial `admin` actual tiene rol
  `Administrador` y dejará de funcionar; hay que crear una credencial con
  `Encargado`, `Guarda` o `Consulta` mediante `identificar.py`.
- Las pruebas de caracterización que documentaban los defectos P3/P5/P6/P8/P9
  se actualizan con nota de cambio deliberado y referencia a esta spec.

## Decisiones y límites

- No se purgan credenciales ni backups automáticamente.
- No se inventa aprobación de reservas: DEC-03 sigue abierta; la reserva nace
  `Confirmada` como en la línea base.
- No se configura `git remote`; el usuario eligió solo commit.
