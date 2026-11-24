# Delta: respaldo y restauración verificable

## ADDED Requirements

### DAT-05 - Copia previa verificable
ANTES de cualquier migración o mutación estructural, el sistema DEBE crear una
copia verificable con timestamp UTC, hash SHA-256 y conteo de entidades.

#### Escenario: respaldo antes de migrar
- DADO un `data.json` con 6 equipos y 4 usuarios
- CUANDO se inicia la migración a SQLite
- ENTONCES existe una copia con hash válido y conteos 6 y 4

### DAT-06 - Restauración exacta
La restauración DEBE recuperar el estado completo y SOLO DEBE ejecutarse tras
validar la copia. NUNCA DEBE purgar copias sin una decisión aprobada.

#### Escenario: restaurar tras fallo
- DADO una copia validada del estado anterior
- CUANDO se restaura
- ENTONCES equipos, usuarios, préstamos y eventos son idénticos a la copia

#### Escenario: sin purga automática
- DADO DEC-06 sin resolver
- CUANDO se crean varias copias
- ENTONCES ninguna se elimina automáticamente
