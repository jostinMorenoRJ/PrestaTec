# Propuesta: Sistema PrestaTec para préstamos universitarios

## Problema
El proceso descrito en el levantamiento de requisitos depende de hojas de cálculo, mensajes y verificaciones manuales. Esto dificulta conocer la disponibilidad real, identificar quién tiene un equipo y reconstruir su historial cuando aparece una falla.

## Objetivo
Construir una aplicación local, sencilla y adaptable, para centralizar el inventario y el ciclo de préstamo de computadores portátiles y proyectores.

## Alcance de esta versión
- Registrar estudiantes, docentes y personal autorizado.
- Registrar portátiles y proyectores con un código único.
- Consultar inventario, disponibilidad por fecha y horario y estados.
- Crear reservas, registrar entregas y devoluciones.
- Impedir reservas que se crucen para un mismo equipo.
- Registrar daños y bloquear el equipo en mantenimiento.
- Consultar el historial de movimientos por equipo.
- Validar en portería mediante código del equipo o documento del usuario.
- Consultar indicadores y exportar préstamos a CSV.

## Fuera del alcance actual
Autenticación real por cuentas institucionales, integración con el sistema académico, envío de correos/notificaciones, lectura QR desde cualquier cámara, sanciones automáticas y despliegue multiusuario en un servidor institucional. Se documentan como evolución, pues el levantamiento los deja pendientes de validación o no define sus reglas completas.

## Criterios de aceptación
1. Los registros se conservan al cerrar y volver a ejecutar el programa.
2. No se aceptan documentos duplicados ni equipos con tipo o nombre vacío.
3. Un equipo no puede reservarse dos veces en períodos que se solapen.
4. Un préstamo entregado mantiene el equipo ocupado incluso si se vence la hora de devolución.
5. Al devolver sin daños, el equipo vuelve a estar disponible.
6. Al devolver con daños, el equipo pasa a mantenimiento y no se puede reservar.
7. Portería informa si un documento tiene equipos activos a su cargo.
8. Las reglas críticas cuentan con pruebas automatizadas de pytest.
