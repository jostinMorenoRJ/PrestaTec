# Delta: persistencia SQLite y migración segura

## ADDED Requirements

### DAT-01 - Esquema versionado
El almacenamiento DEBE tener una versión de esquema y tablas con restricciones
de integridad para equipos, usuarios, préstamos y eventos.

#### Escenario: integridad
- DADO un préstamo que referencia un equipo inexistente
- CUANDO se intenta insertar
- ENTONCES la operación se rechaza por integridad referencial

### DAT-02 - Migración sin pérdida
La migración desde `data.json` DEBE conservar simultáneamente registros en
formato legacy y en formato actual.

#### Escenario: claves mixtas
- DADO un JSON con `Equipos: [PT-009]` y `equipos: [PT-050]`
- CUANDO se migra
- ENTONCES ambos códigos existen en SQLite y se crea copia previa del archivo

### DAT-03 - Mutaciones transaccionales
Toda mutación DEBE ser atómica y estar protegida contra acceso concurrente.

#### Escenario: concurrencia
- DADO 20 altas simultáneas de equipos
- CUANDO se ejecutan contra el repositorio
- ENTONCES las 20 quedan registradas con códigos únicos

### DAT-04 - Backend conmutable
El sistema DEBE poder ejecutarse con `json` o `sqlite` mediante configuración,
sin cambiar la lógica de negocio.

#### Escenario: rollback
- DADO un fallo durante la migración
- CUANDO se reinicia con flag `json`
- ENTONCES el sistema opera con el archivo original intacto
