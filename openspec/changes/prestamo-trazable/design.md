# Diseño: ciclo de préstamo trazable

## Enfoque
Ampliar el modelo de préstamo con campos explícitos y escribirlos en la misma
transacción que el cambio de estado del equipo. La ventana de entrega se calcula
con el reloj UTC de C2.

## Decisiones técnicas
- `responsableEntregaId` y `responsableDevolucionId` referencian usuarios de C5.
- `danio` pasa de `bool` a objeto `{tipo, descripcion, ticket}`; valores antiguos se normalizan en la migración.
- `accesorios` es lista de texto libre (catálogo formal pendiente de decisión).
- Desviación: si `ahora > fin_reserva`, se guarda `entregaFueraDeVentana: true` y se emite evento, sin cambiar el estado.

## Riesgos y mitigación
- Riesgo: migrar booleanos antiguos. Mitigación: normalización en C3 con prueba específica.
- Riesgo: confundir "registrar desviación" con "aplicar sanción". Mitigación: spec explícita y sin reglas de DEC-04.

## Compatibilidad
Los préstamos existentes siguen legibles y devolubles; los campos nuevos son opcionales en lectura.
