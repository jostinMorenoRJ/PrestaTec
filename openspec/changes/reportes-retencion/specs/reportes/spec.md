# Delta: reportes y retención configurable

## ADDED Requirements

### REP-01 - Reportes con datos reales
Los indicadores y reportes DEBEN calcularse desde el repositorio. NO DEBEN
existir valores estáticos ni contadores manuales.

#### Escenario: inventario general
- DADO 6 equipos, 2 prestados y 1 en mantenimiento
- CUANDO se consulta el reporte de inventario
- ENTONCES total=6, prestados=2, mantenimiento=1, disponibles=3

### REP-02 - Exportación legible y filtrable
El CSV DEBE incluir código y nombre del equipo, respetar los filtros aplicados e
indicar claramente las columnas de fechas y responsables.

#### Escenario: exportar filtrado
- DADO un filtro por estado `Devuelta` y rango de fechas
- CUANDO se exporta
- ENTONCES solo aparecen esos préstamos con `PT-003 - Proyector aula 2` en la columna Equipo

### REP-03 - Historial resistente a bajas
El historial por estudiante y por equipo DEBE seguir disponible tras dar de baja
o editar cualquiera de ellos.

#### Escenario: baja de estudiante
- DADO un estudiante con 4 préstamos históricos
- CUANDO se da de baja
- ENTONCES su historial sigue consultable con los mismos 4 eventos

### REP-04 - Retención sin valor inventado
La purga de registros SOLO DEBE activarse con una decisión institucional
aprobada. Por defecto NO se elimina ningún registro.

#### Escenario: DEC-06 abierta
- DADO registros históricos antiguos
- CUANDO se ejecuta el reporte
- ENTONCES todos siguen presentes y la configuración de retención indica `sin purga`
