# Diseño: repositorio e inversión de dependencias

## Enfoque
Extraer de `InventoryService` solo el acceso a datos. Las reglas de negocio
permanecen en el servicio/casos de uso y pasan a recibir un repositorio por
inyección de dependencias.

## Decisiones técnicas
- La interfaz expone `load()` / `save()` del estado completo. Se eligió este
  contrato mínimo —y no operaciones de dominio granulares— para mantener C1
  pequeño, reversible y compatible con las 19 pruebas de la línea base. Las
  operaciones granulares se introducirán en C3 junto con SQLite.
- El adaptador JSON actual es la implementación por defecto durante este change.
- No se introduce ORM ni framework; la interfaz es una clase base abstracta
  o `Protocol` de Python estándar.

## Riesgos y mitigación
- Riesgo: change demasiado amplio y rompa las 12 pruebas. Mitigación: las pruebas de
  caracterización de C0 deben permanecer verdes sin cambiar aserciones.

## Compatibilidad
`data.json` conserva su formato exacto. Rollback: revertir el commit.
