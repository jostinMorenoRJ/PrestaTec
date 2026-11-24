# Diseño: persistencia SQLite y migración segura

## Enfoque
Nueva implementación del repositorio sobre SQLite. La migración es un proceso
explícito, no implícito en el arranque: primero valida, luego copia, luego escribe.

## Decisiones técnicas
- SQLite para instalación local; Postgres queda diferido a DEC-07.
- Tablas: `equipos`, `usuarios`, `prestamos`, `eventos`, `schema_version`.
- Transacciones para cada mutación; unicidad en código de equipo y documento.
- Feature flag para mantener JSON como fallback durante la transición.

## Riesgos y mitigación
- Riesgo alto de pérdida de datos. Mitigación: copia verificable antes de migrar,
  preservación explícita de claves `Equipos`/`equipos`, y prueba de rollback.

## Migración
1. Leer `data.json`.
2. Normalizar ambos formatos sin descartar registros.
3. Validar unicidad y tipos.
4. Escribir copia de seguridad con hash.
5. Poblar SQLite en transacción.
6. Verificar conteos; si falla, restaurar y mantener flag en `json`.
