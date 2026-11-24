# Diseño: identidad y control de acceso

## Enfoque
Un `IdentityProvider` resuelve la identidad de la petición y un `Authorizer`
centraliza la matriz de permisos. Ambos se inyectan en la capa de aplicación.

## Matriz de permisos (aprobada para esta iteración)

| Acción | Guarda | Encargado | Soporte | Administrador | Consulta |
|---|---|---|---|---|---|
| Verificar en portería | Sí | Sí | No | Sí | No |
| Entregar / devolver | Sí | Sí | No | Sí | No |
| Crear equipo / usuario | No | No | No | Sí | No |
| Registrar daño / mantenimiento | No | Sí | Sí | Sí | No |
| Habilitar reincorporación | No | Sí | Sí | Sí | No |
| Exportar reportes | No | Sí | No | Sí | Sí |
| Consultar historial | No | Sí | Sí | Sí | Sí |

> El usuario aprobó esta matriz como decisión técnica temporal el 2026-11-24,
> con el mapeo `Estudiante`/`Docente` → `Consulta`. Queda sujeta a confirmación
> institucional formal. Si la universidad define otra, se cambia la
> configuración (`Autorizador`), no el código de negocio.

> El endpoint de verificación de portería devuelve solo el resultado mínimo
> necesario (préstamo válido, equipo, titular y estado), no el historial completo.
> Así, el rol Guarda puede verificar sin obtener acceso al historial de C6/C10.

## Decisiones técnicas
- Hash: `hashlib.pbkdf2_hmac` con salt aleatorio por usuario (stdlib, sin dependencias nuevas).
- Sesiones: cookie con flag `HttpOnly` y `SameSite`; secretos leídos de entorno.
- Los errores de autorización no revelan si el recurso existe.

## Riesgos y mitigación
- Riesgo: romper las 12 pruebas actuales al exigir auth. Mitigación: C0 caracteriza el acceso anónimo actual como comportamiento a cambiar deliberadamente en este change, con nueva spec aprobada.

## Compatibilidad
El proveedor local es temporal y sustituible por SSO mediante adaptador.
