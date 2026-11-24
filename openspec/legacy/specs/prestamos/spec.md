# Especificación: préstamos e inventario

## Requisitos

### RF01 — Usuarios autorizados
El sistema permite registrar usuarios con nombre, documento único y rol (Estudiante, Docente, Encargado o Guarda). El documento es obligatorio y no se puede repetir.

### RF02 — Inventario
El sistema permite registrar y consultar portátiles y proyectores. Cada equipo recibe un código único, conserva su ubicación y tiene un estado operativo.

### RF03 — Disponibilidad
El sistema permite consultar equipos por tipo y rango de fecha/hora. Un equipo en mantenimiento, fuera de servicio, reservado en el mismo intervalo o actualmente prestado no se ofrece como disponible.

### RF04 — Solicitud / reserva
El sistema permite crear una reserva asociada a un usuario registrado, un equipo y un intervalo. La fecha final debe ser posterior a la inicial.

### RF05 — No duplicidad
El sistema rechaza reservas cuyos intervalos se solapen para el mismo equipo. Un préstamo entregado continúa ocupando el equipo hasta registrar su devolución.

### RF06 — Entrega y devolución
El sistema registra quién entrega y la hora de entrega. La devolución registra hora y observaciones, y libera el equipo cuando no hay daños.

### RF07 — Daños y mantenimiento
Si se reporta un daño en la devolución, el equipo pasa a mantenimiento y no se ofrece para nuevos préstamos hasta que un encargado lo habilite.

### RF08 — Consultas e historial
El sistema muestra indicadores de inventario, préstamos activos, atrasos y reservas del día; permite consultar movimientos de un equipo y descargar un reporte CSV.

### RF09 — Validación de portería
El sistema acepta el código del equipo o el documento del usuario y responde si existe un préstamo activo, mostrando el titular y los equipos asociados cuando corresponde.

## Requisitos no funcionales
- RNF01: los roles se guardan, pero la autenticación institucional y los permisos por cuenta están pendientes para una siguiente versión.
- RNF02: las consultas locales se resuelven desde un archivo JSON sin depender de un servicio externo.
- RNF03: la interfaz se adapta a pantallas de escritorio y móviles.
- RNF04: los datos permanecen en `data.json`; el respaldo automatizado y el despliegue seguro institucional quedan pendientes.

## Escenarios de aceptación
- **Dado** un usuario registrado y un equipo disponible, **cuando** se crea una reserva con fechas válidas, **entonces** queda en estado Confirmada.
- **Dado** un equipo con una reserva en un horario, **cuando** se solicita otra reserva que se cruza, **entonces** el sistema la rechaza.
- **Dado** un préstamo entregado, **cuando** se devuelve sin daños, **entonces** el equipo vuelve a estar Disponible.
- **Dado** un préstamo entregado, **cuando** se devuelve con daños, **entonces** el equipo pasa a Mantenimiento.
- **Dado** un usuario con un préstamo entregado, **cuando** portería consulta su documento, **entonces** el sistema confirma los equipos que tiene a cargo.
