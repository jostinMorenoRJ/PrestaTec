# Propuesta: repositorio e inversión de dependencias (C1)

## Problema
`service.py` mezcla reglas de negocio con lectura/escritura de `data.json`.
Cambiar a SQLite obligaría a reescribir las reglas, con alto riesgo.

## Qué cambia
- Definir una interfaz de repositorio con operaciones de equipos, usuarios,
  préstamos y eventos.
- Hacer que los casos de uso dependan de la interfaz, no del archivo.
- Mantener el adaptador JSON actual funcionando sin cambio de formato.

## Fuera de alcance
Cambio de formato de almacenamiento, SQLite ni integridad transaccional.

## Capacidades afectadas
- prestamos
- requisitos-institucionales (INT-04)

## Impacto esperado
Aísla el riesgo de la futura migración a SQLite: el dominio no se toca.
