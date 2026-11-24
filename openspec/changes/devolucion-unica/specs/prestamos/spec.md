# Delta de spec: préstamos — devolución única

## ADDED Requirements

### RF06b - Una sola devolución por préstamo

Un préstamo ya devuelto no puede volver a devolverse y el intento rechazado no
deja rastro.

#### Scenario: intento duplicado tras una devolución correcta

- **GIVEN** un préstamo en estado `Devuelta`
- **WHEN** se llama de nuevo a `devolver(pid, ...)`
- **THEN** se lanza `BusinessError` con un mensaje que contiene "ya fue devuelto"
- **AND** `devueltoEn` sigue con el valor de la primera devolución
- **AND** el historial del equipo no gana eventos nuevos

#### Scenario: otros estados no entregados

- **WHEN** se intenta devolver un préstamo en estado `Confirmada`, `Cancelada`
  o `No se presentó`
- **THEN** se mantiene el mensaje existente "Esta reserva no tiene un equipo
  entregado."

## Impacto en requisitos existentes

| Requisito | Cambio |
|---|---|
| RF06 Entrega y devolución | El error de devolución duplicada deja de ser ambiguo |
| RF08 Consultas e historial | El historial queda intacto tras un intento rechazado |
