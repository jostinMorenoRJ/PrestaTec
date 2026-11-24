# Propuesta: responsable de devolución (núcleo pedido)

## Problema

La especificación base `openspec/specs/prestamos/spec.md`, RF06, marca como
brecha conocida: *"falta responsable de devolución"*. Hoy
`InventoryService.devolver()` registra hora de devolución y observaciones, pero
no queda constancia de quién recibió físicamente el equipo.

## Alcance

- Guardar en el préstamo el nombre de quien recibe la devolución.
- Aceptar el responsable de forma explícita o tomarlo de la sesión autenticada.
- Mantener compatibilidad con las llamadas actuales que no pasan ni responsable
  ni actor.

## Fuera de alcance

- Tipo de falla, ticket de mantenimiento, ventana de entrega, plazos, sanciones
  y aprobaciones (DEC-01..DEC-09 siguen pendientes).
- Cambios de interfaz o de políticas institucionales.

## Criterios de aceptación

- **DEV-01:** si se pasa `responsable_devolucion`, queda guardado en el préstamo.
- **DEV-02:** si no se pasa pero la operación tiene actor autenticado, se guarda
  el nombre del actor.
- **DEV-03:** si no hay ninguno de los dos, la operación sigue funcionando y el
  campo queda vacío (sin romper las pruebas existentes).
- **DEV-04:** el evento del historial del equipo menciona a quien recibió el
  equipo cuando se conoce.

## Justificación

Cierra una brecha ya documentada del núcleo que pidió el usuario (prestar y
devolver) y permite demostrar un ciclo completo **Spec → Test → Código** con
tres commits separados y sus etiquetas, sin inventar políticas nuevas.
