# Diseño: auditoría base

## Enfoque
El repositorio de C3 ya contempla la tabla `eventos`. Este change define el
contrato del evento y su emisión desde los casos de uso, usando el actor que
resuelve C5.

## Decisiones técnicas
- Evento: `id`, `actor_id`, `accion`, `entidad_tipo`, `entidad_id`, `timestamp_utc`, `origen`, `detalle`.
- Inmutable: no se actualiza ni se elimina; las correcciones se registran como eventos nuevos.
- Se persiste en la misma transacción que la mutación (atomicidad).
- El reloj inyectado de C2 provee el timestamp.

## Riesgos y mitigación
- Riesgo: evento huérfano si la mutación falla. Mitigación: misma transacción.
- Riesgo: volumen creciente. Mitigación: índice por entidad y timestamp; purga solo con DEC-06.

## Compatibilidad
No modifica datos existentes: los eventos antiguos en memoria se migran como
eventos de tipo `legado` si están presentes en `data.json`.
