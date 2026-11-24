# Delta: reloj UTC y políticas inyectables

## ADDED Requirements

### ARC-03 - Reloj inyectable
Toda regla que dependa del tiempo DEBE obtener la hora de un proveedor
inyectable. El almacenamiento DEBE ser UTC.

#### Escenario: atraso determinista
- DADO un reloj falso fijo en `2026-11-24T15:00:00Z`
- DADO un préstamo con fin `2026-11-24T14:00:00Z`
- CUANDO se consulta el estado
- ENTONCES se marca como atrasado

#### Escenario: zona horaria distinta
- DADO el mismo préstamo consultado desde dos zonas horarias
- CUANDO se calcula el solape
- ENTONCES el resultado es idéntico porque ambos usan UTC

### ARC-04 - Políticas sin valores inventados
Los parámetros de plazo, anticipación, aprobación, sanción y retención DEBEN
existir como configuración vacía hasta que la universidad decida su valor.

#### Escenario: política no definida
- DADO `DEC-01` aún sin resolver
- CUANDO se valida la duración de un préstamo
- ENTONCES no se rechaza por duración y la incertidumbre queda documentada
