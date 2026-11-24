# Delta de spec: préstamos — responsable de devolución

Este delta cierra la brecha RF06 documentada en
`openspec/specs/prestamos/spec.md` ("falta responsable de devolución").

## ADDED Requirements

### RF06a - Responsable de la devolución

El sistema debe guardar quién recibió físicamente el equipo al registrar una
devolución, sin inventar un nombre cuando no se informe.

#### Scenario: responsable indicado explícitamente

- **WHEN** se llama a `devolver(pid, danio, nota, responsable_devolucion='Celador Méndez')`
  sobre una reserva entregada
- **THEN** el préstamo queda con `responsableDevolucion == 'Celador Méndez'`
- **AND** el evento del historial del equipo menciona a "Celador Méndez"

#### Scenario: responsable tomado de la sesión

- **WHEN** se llama a `devolver(pid, danio, nota, actor=<Identidad nombre='Guarda Ruiz'>)`
  sin responsable explícito
- **THEN** el préstamo queda con `responsableDevolucion == 'Guarda Ruiz'`

#### Scenario: llamada heredada sin responsable ni actor

- **WHEN** se llama a `devolver(pid, danio, nota)` como en el código anterior
- **THEN** la devolución se completa igual
- **AND** `responsableDevolucion` queda como cadena vacía

## Impacto en requisitos existentes

| Requisito | Cambio |
|---|---|
| RF06 Entrega y devolución | La brecha "falta responsable de devolución" pasa a cumplida en este delta |
| RF08 Consultas e historial | El historial incluye al responsable de la recepción cuando se conoce |
