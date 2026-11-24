# Propuesta: perfiles por rol y experiencia de usuario (C12)

## Problema

C5 dejó autenticación y RBAC, pero con cinco roles (`Consulta`, `Guarda`,
`Encargado`, `Soporte`, `Administrador`) y una única interfaz para todos. Eso
genera tres problemas observables:

1. Un estudiante ve pestañas de gestión, puede reservar para terceros y consulta
   los préstamos de todos.
2. Guarda y Encargado comparten la misma pantalla, sin una entrada clara a su
   tarea principal (portería o entrega/devolución).
3. Quedan defectos documentados en la caracterización: conflicto `400` sin
   alternativas (P3), CSV con el ID en la columna “Equipo” (P3),
   `/api/disponibilidad` sin uso en la UI (P5), JSON mixto que descarta claves
   nuevas (P9), `estadoEntrega` no persistido (P6) y verificación exitosa de
   portería sin auditoría (P8).

## Objetivo

Reducir el sistema a los tres perfiles operativos acordados y ofrecer una
interfaz distinta, intuitiva y visualmente clara para cada uno, corrigiendo los
defectos anteriores dentro de una sola spec verificable.

## Decisiones del usuario (2026-11-24)

- Restringir los roles a **Consulta**, **Guarda** y **Encargado**.
  `Estudiante`/`Docente` siguen traduciéndose a `Consulta`.
- **Eliminar por completo** `Administrador` y `Soporte`: no se aceptan en el alta
  de credenciales y una credencial existente con esos roles deja de autenticar.
  No se borran archivos ni datos; se documenta la migración.
- La solicitud de préstamo es **solo para el propio documento** de la sesión.
- Publicación: **solo commit local**. No hay remoto configurado y el usuario
  decidió no hacer push en esta iteración.

## Alcance

- Matriz de permisos reducida a tres roles, con `CREAR_RECURSO` transferido a
  `Encargado`.
- `/api/auth/me` expone `vistaInicial` (`mis`, `porteria`, `gestion`).
- Vistas por perfil: “Mis préstamos” (Consulta), “Portería” (Guarda) y
  “Gestión” (Encargado), con navegación y acciones filtradas.
- `POST /api/reservas` restringido a `Consulta` y al documento de la sesión;
  conflicto devuelto como `409` con `alternativas`.
- `GET /api/mis-prestamos` para Consulta; `/api/reservas`, `/api/usuarios` y
  `/api/resumen` restringidos a roles de gestión.
- Persistencia de `estadoEntrega`, auditoría de verificaciones de portería, CSV
  con nombre de equipo y conservación de claves nuevas en JSON mixto.
- UI rediseñada: estados vacíos, feedback, foco, responsive y sin botones
  muertos.

## Fuera del alcance

- SSO, correo/notificaciones, lectores físicos reales y sanciones (DEC-03,
  DEC-05, DEC-07).
- Definir plazos, anticipación, aprobación o retención (DEC-01, DEC-02, DEC-06).
- Configurar remoto o publicar en GitHub.

## Criterios de aceptación

1. Solo existen tres roles efectivos; una credencial `Administrador` o `Soporte`
   no puede crear préstamos ni iniciar sesión.
2. Cada perfil entra en su propia vista y no ve navegación de otros perfiles.
3. Consulta solo puede reservar para su documento y solo ve sus préstamos.
4. Un conflicto de horario responde `409` con alternativas reales.
5. El CSV muestra el nombre del equipo; `estadoEntrega` queda guardado y toda
   verificación de portería genera evento de auditoría.
6. Un JSON con claves legado y nuevas conserva ambos conjuntos sin pérdida.
7. La suite completa se ejecuta en verde y la UI se verifica en navegador.
