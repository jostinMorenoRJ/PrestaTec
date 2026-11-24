# Propuesta: ciclo de préstamo trazable (C8)

## Problema
La devolución no registra quién la recibe, el estado físico es un booleano con
nota libre y `estadoEntrega` no se persiste. Una reserva vencida puede entregarse
sin control. Esto incumple INST-04, RF06, RF07 y EXC-02 parcialmente.

## Qué cambia
- Persistir responsable de entrega y de devolución con auditoría de C6.
- Daño estructurado: tipo, descripción y ticket de soporte opcional.
- Registrar la desviación de la ventana de entrega como dato, sin rechazar ni
  sancionar mientras DEC-01 no esté resuelta.
- Registro de accesorios entregados/recibidos como observación estructurada (FUN-14).

## Fuera de alcance
Sanciones automáticas (DEC-04), plazos máximos (DEC-01), aprobación de reservas (DEC-03).

## Capacidades afectadas
- prestamos
- seguridad (auditoría)

## Impacto esperado
Cierra la trazabilidad exigida en §7.4–7.6 y habilita reportes fiables en C10.
