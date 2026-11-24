# Propuesta: disponibilidad en UI y conflictos con alternativas (C7)

## Problema
`/api/disponibilidad` funciona, pero el formulario de reservas nunca lo llama: el
usuario elige un equipo y solo después descubre que está ocupado. Además, el
conflicto responde `400` con `mensaje`, mientras la interfaz ya contiene una rama
muerta que espera `409` con `alternativas` (P3 y P5).

## Qué cambia
- La UI consulta disponibilidad con el rango elegido antes de mostrar opciones.
- El conflicto pasa a `409` con una lista de equipos libres del mismo tipo.
- Se mantiene una única regla de solapado compartida por API y caso de uso.

## Fuera de alcance
Calendario visual (O3), aprobación de reservas (DEC-03) y anticipación mínima (DEC-02).

## Capacidades afectadas
- prestamos

## Impacto esperado
Cierra INST-03, INST-05, RF03, RF05 y RNF03, y elimina la rama muerta de `app.js`.
