# Delta: portería confiable

## ADDED Requirements

### POR-01 - SLA de verificación
TODA verificación en portería DEBE completarse en menos de 3 segundos, con un
inventario de prueba de al menos 100 equipos. La medición automatizada con pytest
cubre petición y respuesta de API. La medición con render de navegador y lector
físico queda documentada como limitación dependiente de DEC-07.

#### Escenario: medición automatizada
- DADO 100 equipos y 50 préstamos activos
- CUANDO un guarda verifica un código válido
- ENTONCES la respuesta de la API ocurre en menos de 3 segundos

### POR-02 - Funcionamiento sin CDN
La generación y lectura de códigos QR NO DEBEN depender de recursos remotos.
DEBE existir siempre una alternativa manual de entrada.

#### Escenario: sin conexión
- DADO un navegador sin acceso a Internet
- CUANDO se abre el diálogo de portería
- ENTONCES el QR se genera localmente o se ofrece entrada manual funcional

### POR-03 - El QR no autoriza por sí solo
La verificación DEBE comprobar la existencia de un préstamo válido y el estado
del equipo. Un código leído sin operación activa DEBE rechazarse y auditarse.

#### Escenario: código sin préstamo
- DADO un equipo disponible sin préstamo activo
- CUANDO se escanea su QR en portería
- ENTONCES se rechaza la salida con mensaje claro y se registra el rechazo

### POR-04 - Cámara liberada
Los recursos de cámara DEBEN liberarse al cambiar de vista o cerrar el diálogo.

#### Escenario: cambio de vista
- DADO una cámara activa en portería
- CUANDO el usuario navega a Inventario
- ENTONCES todas las pistas del `MediaStream` están detenidas
