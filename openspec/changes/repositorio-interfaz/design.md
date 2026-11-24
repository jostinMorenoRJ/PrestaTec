# Diseño: repositorio e inversión de dependencias

## Enfoque
Extraer de `InventoryService` solo el acceso a datos. Las reglas de negocio
permanecen en el servicio/casos de uso y pasan a recibir un repositorio por
inyección de dependencias.

## Decisiones técnicas
- La interfaz expone operaciones de dominio, no sentencias de archivo.
- El adaptador JSON actual es la implementación por defecto durante este change.
- No se introduce ORM ni framework; la interfaz es una clase base abstracta
  o `Protocol` de Python estándar.

## Riesgos y mitigación
- Riesgo: change demasiado amplio y rompa las 12 pruebas. Mitigación: las pruebas de
  caracterización de C0 deben permanecer verdes sin cambiar aserciones.

## Compatibilidad
`data.json` conserva su formato exacto. Rollback: revertir el commit.
