# Especificación base: préstamos e inventario

Estado: **línea base verificada en la Etapa 1**. Describe el comportamiento que
hoy existe, no el estado final deseado. Las mejoras se registrarán como deltas
en los changes de `openspec/changes/`.

## Requisitos vigentes

### RF01 - Usuarios autorizados
El sistema registra usuarios con nombre, documento único y rol. El documento es
obligatorio y no se puede repetir. Estado: **cumplido**.

### RF02 - Inventario
El sistema registra y consulta portátiles y proyectores con código único,
ubicación y estado. Estado: **cumplido**.

### RF03 - Disponibilidad
El sistema consulta equipos por tipo y rango de fecha/hora. Excluye
mantenimiento, fuera de servicio, reservas solapadas y préstamos activos.
Estado: **parcial** (funciona en `/api/disponibilidad`, no en la interfaz).

### RF04 - Solicitud / reserva
El sistema crea reservas asociadas a usuario registrado, equipo e intervalo,
con `fin > inicio`. Estado: **cumplido**.

### RF05 - No duplicidad
No se aceptan reservas solapadas para el mismo equipo. Un préstamo entregado
ocupa el equipo hasta su devolución. Estado: **cumplido en la regla**, con
contrato de error pendiente: hoy responde `400`, no `409` con alternativas.

### RF06 - Entrega y devolución
Se registra responsable de entrega, hora de entrega, hora de devolución y
observaciones. Estado: **parcial**: falta responsable de devolución y estado
físico estructurado; la ventana de entrega no se valida.

### RF07 - Daños y mantenimiento
Un daño reportado en la devolución pasa el equipo a mantenimiento y no se ofrece
hasta habilitación manual. Estado: **parcial**: falta tipo de falla y ticket.

### RF08 - Consultas e historial
Indicadores de inventario, atrasos y reservas del día; historial por equipo y
exportación CSV. Estado: **parcial**: CSV sin filtros y columna "Equipo" con ID.

### RF09 - Validación en portería
Acepta código de equipo o documento de usuario e informa si existe préstamo
activo. Estado: **parcial**: respuesta rápida en proceso, sin auditoría de
verificaciones correctas y con QR dependiente de CDN.

## Reglas de negocio vigentes

- Solape: `inicio_existente < fin_nuevo` y `inicio_nuevo < fin_existente`.
- Entrega vencida sigue ocupando el equipo hasta registrar devolución.
- Estados de equipo: `Disponible`, `Mantenimiento`, `Fuera de servicio`; la UI
  muestra `Prestado` cuando hay entrega activa.
- Estados de préstamo: `Confirmada`, `Entregada`, `Devuelta`, `Cancelada`,
  `No se presentó`, más el indicador calculado `Atrasada`.
- Códigos por tipo: `PT-###`, `PR-###`.

## Brechas conocidas (deltas previstos)

| Brecha | Change que la cierra |
|---|---|
| Sin autenticación ni RBAC | `identidad-rbac` |
| Persistencia sin transacciones ni respaldo | `persistencia-sqlite`, `respaldo-restauracion` |
| Disponibilidad ausente en UI y conflicto 400 | `disponibilidad-conflictos` |
| Trazabilidad incompleta de préstamo | `prestamo-trazable`, `auditoria` |
| Portería sin QR offline ni auditoría | `porteria-confiable` |
| Reportes limitados | `reportes-retencion` |

## Fuente

Diagnóstico de la Etapa 1 y archivo original
`openspec/changes/prestamos-universidad/spec.md` del ZIP `PrestaTec_Python.zip`.
