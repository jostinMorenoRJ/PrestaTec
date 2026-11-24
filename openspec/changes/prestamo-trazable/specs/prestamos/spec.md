# Delta: ciclo de préstamo trazable

## MODIFIED Requirements

### RF06 - Entrega y devolución
La entrega DEBE registrar responsable, hora real y ventana prevista. La
devolución DEBE registrar responsable, hora real, observaciones y estado físico.
Un préstamo inexistente o ya devuelto DEBE rechazarse.

#### Escenario: devolución completa
- DADO un préstamo entregado y un Encargado autenticado
- CUANDO se devuelve con accesorios y sin daño
- ENTONCES el equipo vuelve a `Disponible` y el evento identifica al responsable

#### Escenario: devolución duplicada
- DADO un préstamo ya devuelto
- CUANDO se intenta devolver de nuevo
- ENTONCES se rechaza sin cambiar el estado del equipo

### RF07 - Daños y mantenimiento
Un daño DEBE registrarse con tipo, descripción y ticket opcional. El equipo NO
DEBE volver a estar disponible sin autorización de Soporte o Encargado.

#### Escenario: daño reportado
- DADO una devolución con daño tipo `Pantalla`
- CUANDO se registra
- ENTONCES el equipo pasa a `Mantenimiento` y se emite el evento correspondiente

## ADDED Requirements

### PRE-01 - Desviación sin sanción
Si la entrega ocurre fuera de la ventana prevista, el sistema DEBE registrar la
desviación como dato. NO DEBE rechazarla ni aplicar sanción mientras DEC-01/DEC-04 estén abiertas.

#### Escenario: entrega tardía
- DADO un préstamo con fin `14:00Z` y entrega `15:00Z`
- CUANDO se registra la entrega
- ENTONCES se guarda `entregaFueraDeVentana: true` y no se aplica ninguna sanción

### PRE-02 - Accesorios estructurados
Los accesorios entregados y recibidos DEBEN persistirse como lista de texto y
aparecer en el comprobante y en el historial.

#### Escenario: accesorios
- DADO una entrega con cargador y mouse
- CUANDO se consulta el historial del préstamo
- ENTONCES aparecen ambos accesorios con quién los entregó y quién los recibió
