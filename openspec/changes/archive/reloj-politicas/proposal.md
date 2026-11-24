# Propuesta: reloj UTC y políticas inyectables (C2)

## Problema
`datetime.now()` ingenua y reglas de negocio hardcodeadas impiden probar atrasos,
solapes y zonas horarias de forma determinista. Además, los plazos y sanciones
aún no fueron decididos por la universidad.

## Qué cambia
- Inyectar un reloj UTC configurable.
- Representar políticas como parámetros sin valores institucionales inventados.

## Fuera de alcance
Definir plazos, anticipación, sanciones o retención. Eso depende de DEC-01 a DEC-06.

## Capacidades afectadas
- prestamos

## Impacto esperado
Pruebas deterministas y disposición para futuras reglas sin reescrituras.
