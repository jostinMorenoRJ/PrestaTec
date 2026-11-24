# Propuesta: devolución única (núcleo pedido)

## Problema

El enunciado pide *devolver equipos prestados*. Hoy llamar dos veces a
`devolver()` sobre el mismo préstamo se rechaza, pero con el mensaje genérico
"Esta reserva no tiene un equipo entregado.", que no distingue el caso de ya
devuelto de otros estados inválidos.

## Alcance

- Dar un error específico cuando el préstamo ya está `Devuelta`.
- Garantizar que el intento rechazado no muta `devueltoEn` ni el historial.
- Conservar el mensaje anterior para el resto de estados inválidos.

## Fuera de alcance

- Políticas de plazos, sanciones o aprobaciones (DEC-01..DEC-09).
- Cambios en la interfaz o en los permisos.

## Criterios de aceptación

- **DUP-01:** el segundo `devolver()` sobre un préstamo `Devuelta` lanza
  `BusinessError` con un mensaje que indique "ya fue devuelto".
- **DUP-02:** el rechazo no cambia `devueltoEn` ni añade eventos al historial.
- **DUP-03:** los estados `Confirmada`, `Cancelada` y `No se presentó` siguen
  dando el mensaje existente.

## Justificación

Segundo ciclo corto y verificable de Spec → Test → Código sobre una regla del
núcleo, para que el método no quede como caso aislado del cambio DEV anterior.
