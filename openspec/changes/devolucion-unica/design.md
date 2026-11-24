# Diseño: devolución única

## Decisión

En `InventoryService.devolver()`, comprobar el estado `Devuelta` antes de la
validación genérica de estado y lanzar `BusinessError('El préstamo ya fue
devuelto.')`. El resto de estados no entregados conservan el mensaje actual.

La comprobación va antes de cualquier mutación (`p.update`, `_log`, `_save`),
por lo que un intento duplicado no altera la hora de devolución ni el historial.

## Compatibilidad

- Firma sin cambios: no hay parámetros nuevos.
- Ninguna prueba existente comprueba el texto del error genérico.
- `web.py` ya traduce `BusinessError` a `400` con el mensaje, sin cambios.

## Verificación

Una prueba nueva en `tests/test_prestamos.py`: devolver, intentar devolver de
nuevo, verificar mensaje, timestamp y longitud del historial. Debe fallar antes
del cambio y pasar después.
