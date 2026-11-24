# Propuesta: persistencia SQLite y migración segura (C3)

## Problema
`data.json` se reescribe completo sin transacciones, bloqueos ni copia previa.
Además, se detectó que un JSON con claves legacy y nuevas pierde los registros
nuevos al migrar.

## Qué cambia
- Implementar el repositorio de C1 con SQLite local.
- Esquema versionado con integridad referencial.
- Migración desde `data.json` con copia previa, dry-run y rollback.
- Feature flag `json|sqlite` para alternar backend.

## Fuera de alcance
Respaldo programado (C4), auditoría (C6), Postgres, borrado de datos.

## Capacidades afectadas
- persistencia (nueva)
- prestamos

## Impacto esperado
Cierra PDF-RNF04 en su componente de integridad y prepara la base para auth,
auditoría y reportes.
