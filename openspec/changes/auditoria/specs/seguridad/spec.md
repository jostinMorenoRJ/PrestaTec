# Delta: auditoría base

## ADDED Requirements

### AUD-01 - Registro inmutable
TODA mutación relevante DEBE generar exactamente un evento inmutable con actor,
acción, entidad, timestamp UTC y origen, en la misma transacción que el cambio.

#### Escenario: alta de equipo
- DADO un administrador autenticado
- CUANDO registra el equipo `PT-007`
- ENTONCES existe un evento con actor, acción `equipo.creado`, entidad `PT-007` y timestamp UTC

### AUD-02 - Histórico persistente
Los eventos NO DEBEN desaparecer al editar, dar de baja o eliminar información
operativa. Las correcciones DEBEN añadir eventos, no sobrescribirlos.

#### Escenario: baja lógica
- DADO un equipo con 3 eventos previos
- CUANDO se da de baja
- ENTONCES los 3 eventos siguen consultables y aparece uno nuevo

### AUD-03 - Verificación de portería auditada
TODA verificación exitosa en portería DEBE registrarse, además de los rechazos.

#### Escenario: verificación correcta
- DADO un guarda que verifica un préstamo válido
- CUANDO la verificación responde correctamente
- ENTONCES se emite un evento `porteria.verificada` con el actor
