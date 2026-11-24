# Propuesta: reportes y retención configurable (C10)

## Problema
El CSV actual exporta todos los préstamos con el ID del equipo en la columna
"Equipo", sin filtros y sin reporte de mantenimiento. La retención no está
definida (DEC-06), por lo que no se puede purgar nada sin inventar una regla.

## Qué cambia
- Reportes filtrables por fecha, estado, equipo y usuario.
- Inventario general, disponibles, prestados, mantenimiento, activos y devoluciones pendientes.
- Historial por estudiante y por equipo usando los eventos de C6.
- Exportación CSV con nombre de equipo y BOM; parámetro de retención sin valor por defecto.

## Fuera de alcance
PDF y Excel (FUN-A2, P3), notificaciones (O4) y purga automática sin DEC-06.

## Capacidades afectadas
- reportes (nueva)
- requisitos-institucionales (RF08, RES-03)

## Impacto esperado
Cierra RF08 y hace visible la trazabilidad construida en C6 y C8.
