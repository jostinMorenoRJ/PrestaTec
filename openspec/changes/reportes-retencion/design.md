# Diseño: reportes y retención configurable

## Enfoque
Los reportes son consultas de solo lectura sobre el repositorio con un conjunto
común de filtros. La exportación es una representación, no una lógica de negocio.

## Decisiones técnicas
- Un único objeto `FiltrosReporte` reutilizado por API y CSV.
- CSV con BOM UTF-8, cabeceras en español y columna `Equipo` con `codigo - nombre`.
- La retención es una opción de configuración: `None` = sin purga; nunca se borra nada por defecto.
- Los reportes respetan RBAC de C5 (Consulta puede exportar, Guarda no).

## Riesgos y mitigación
- Riesgo: filtros inconsistentes entre pantalla y exportación. Mitigación: mismo objeto de filtros y prueba compartida.

## Compatibilidad
El endpoint CSV actual sigue respondiendo; se añaden parámetros opcionales y se corrige el contenido de la columna `Equipo`.
