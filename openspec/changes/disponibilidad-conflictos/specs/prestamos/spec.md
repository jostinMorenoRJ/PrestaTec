# Delta: disponibilidad en UI y conflictos con alternativas

## MODIFIED Requirements

### RF05 - No duplicidad
El conflicto por solapado DEBE responderse con `409` y un listado de
alternativas libres del mismo tipo. El comportamiento anterior (`400`) queda
registrado únicamente como caracterización histórica de C0.

#### Escenario: conflicto con alternativas
- DADO un proyector `PR-001` reservado de 10:00 a 12:00
- CUANDO se solicita de 11:00 a 13:00
- ENTONCES se responde `409` con `PR-002` y `PR-003` como alternativas libres

## ADDED Requirements

### DIS-01 - Una sola regla de disponibilidad
La API, el caso de uso y la interfaz DEBEN usar la misma definición de
disponibilidad: sin mantenimiento, sin baja, sin solape de reservas ni de
préstamos activos.

#### Escenario: regla compartida
- DADO un equipo en mantenimiento con un rango libre
- CUANDO se consulta por API y desde el formulario
- ENTONCES ambos lo excluyen

### DIS-02 - Filtrado previo en la interfaz
El formulario de reserva DEBE consultar `/api/disponibilidad` con el rango
elegido y mostrar solo los equipos resultantes.

#### Escenario: rango ocupado
- DADO un usuario que elige un rango donde solo `PT-003` está libre
- CUANDO se abre el selector de equipos
- ENTONCES aparece únicamente `PT-003`
