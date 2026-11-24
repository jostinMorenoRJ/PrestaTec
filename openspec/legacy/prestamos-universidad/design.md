# Diseño técnico

## Arquitectura

La aplicación se divide en tres partes pequeñas:

- `prestatec/service.py`: reglas del negocio y persistencia JSON.
- `prestatec/web.py`: rutas HTTP y conversión de solicitudes/respuestas JSON.
- `static/`: interfaz HTML, CSS y JavaScript.
- `run.py`: inicia el servidor local en `127.0.0.1:5080`.

Se utiliza `http.server`, `json`, `csv`, `datetime` y otras bibliotecas estándar de Python. No se necesita una base de datos ni un framework web externo.

## Modelo de información

- **Usuario:** id, nombre, documento y rol.
- **Equipo:** id, tipo, nombre, ubicación y estado.
- **Préstamo:** id, equipo, usuario, inicio, fin, estado, fechas de entrega/devolución, responsable y nota.
- **Evento:** fecha, equipo y descripción del movimiento.

Los datos se almacenan en `data.json`. Los códigos se generan por tipo: `PT-001` para portátiles y `PR-001` para proyectores.

## Estados

- Equipo: `Disponible`, `Mantenimiento` o `Fuera de servicio`. La interfaz muestra `Prestado` cuando existe una entrega activa.
- Préstamo: `Confirmada`, `Entregada`, `Devuelta`, `Cancelada` o `No se presentó`. La interfaz calcula `Atrasada` cuando una entrega activa supera su fecha de devolución.

## Regla de cruce de horarios
Dos intervalos se cruzan cuando `inicio_existente < fin_nuevo` y `inicio_nuevo < fin_existente`. Una entrega activa que ya venció sigue ocupando el equipo hasta que se registre su devolución.

## Decisiones y límites
- Los roles se registran para clasificar usuarios, pero esta versión no implementa inicio de sesión ni permisos por cuenta.
- El módulo de portería permite digitar o escanear con un lector que escriba el código. La generación de etiqueta QR está en la interfaz; el lector de cámara depende del navegador y de la librería QR externa.
- La aplicación está pensada para una demostración local y no ofrece todavía controles de concurrencia, copias de seguridad automáticas ni endurecimiento para Internet.
- Los plazos máximos, anticipación de reserva, sanciones y retención histórica requieren decisión de la universidad.
