# Propuesta: respaldo y restauración verificable (C4)

## Problema
El ZIP original no incluye ningún mecanismo de copia de seguridad. Un fallo de
escritura, una migración incorrecta o un borrado accidental son irreversibles.
Esto incumple PDF-RNF04 directamente.

## Qué cambia
- Copias automáticas del estado antes de cada mutación estructural y de cada migración.
- Procedimiento de restauración con verificación de hash y conteo de registros.
- Política de retención de copias configurable, sin purga automática mientras DEC-06 esté abierta.

## Fuera de alcance
Borrado de datos, purga automática con valores inventados, almacenamiento remoto,
Postgres y cifrado de discos (C11).

## Capacidades afectadas
- persistencia
- requisitos-institucionales (PDF-RNF04, INT-03)

## Impacto esperado
Cierra la parte de "respaldo" de RNF04 y hace verificable la regla INT-03 de no
perder datos sin autorización.
