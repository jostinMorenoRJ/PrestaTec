# Propuesta: auditoría base (C6)

## Problema
El histórico actual guarda eventos en memoria y no registra quién ejecuta cada
operación. Las verificaciones de portería correctas no dejan rastro (P8). Esto
incumple RES-03 y la exigencia de trazabilidad del master prompt §7.6.

## Qué cambia
- Evento inmutable con actor, acción, entidad, timestamp UTC y origen.
- Registro de todas las mutaciones relevantes y de las verificaciones exitosas.
- Consulta de historial por equipo, usuario y período.

## Fuera de alcance
Sanciones, notificaciones, retención numérica (DEC-04, DEC-06) y reportes (C10).

## Capacidades afectadas
- seguridad
- prestamos

## Impacto esperado
Proporciona el "quién" que necesitan C8 y C9 sin duplicar modelos de identidad.
