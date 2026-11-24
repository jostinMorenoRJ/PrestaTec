# Diseño: disponibilidad en UI y conflictos con alternativas

## Enfoque
Extraer la regla de solapado a una función de dominio pura (ya presente en la
spec base) y usarla tanto en `/api/disponibilidad` como en la creación de
reservas y en el cálculo de alternativas.

## Decisiones técnicas
- `409 Conflict` con cuerpo `{ "mensaje": "...", "alternativas": [ {id, codigo, nombre, tipo} ] }`.
- Alternativas: mismos tipo y rango, estado `Disponible`, sin solape; máximo 5.
- La petición sin parámetros de rango sigue siendo `400` (comportamiento actual documentado en C0).
- Reloj y zona horaria de C2 se usan para interpretar `datetime-local`.

## Riesgos y mitigación
- Riesgo: romper la caracterización del `400`. Mitigación: C0 documenta ese valor como estado actual; este change lo cambia deliberadamente con spec aprobada y actualiza la prueba.

## Compatibilidad
Sin cambios de esquema. El listado actual de equipos sigue funcionando.
