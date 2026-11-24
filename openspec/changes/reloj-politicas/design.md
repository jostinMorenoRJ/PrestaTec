# Diseño: reloj UTC y políticas inyectables

## Enfoque
Sustituir llamadas directas a `datetime.now()` por un proveedor de tiempo.
Las políticas son objetos de configuración con campos opcionales; cuando no hay
valor institucional, el sistema NO aplica la regla.

## Decisiones técnicas
- Almacenar timestamps en UTC; convertir a zona local solo en la presentación.
- Los valores de política quedan a `None` hasta DEC-01..DEC-06.
- No se crea un módulo de reglas complejo; solo un contenedor simple.

## Riesgos y mitigación
- Riesgo: cambiar el criterio de atraso y romper caracterización. Mitigación:
  las pruebas existentes usan tiempo real; se añaden pruebas nuevas con reloj falso.

## Compatibilidad
Sin cambios visibles para el usuario; sin migración de datos.
