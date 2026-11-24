# Diseño: portería confiable

## Enfoque
La validación en portería es un caso de uso con tres pasos: resolver identificador
(QR/código/documento), comprobar préstamo activo y estado del equipo, y emitir
evento. La UI solo muestra el resultado.

## Decisiones técnicas
- QR: generar SVG localmente con una librería Python añadida a dependencias y
  servida como estático; sin `cdnjs.cloudflare.com`. Si no hay librería, fallback
  a código legible + botón manual (nunca dependencia remota).
- Cámara: guardar el `MediaStream` y llamar `getTracks().forEach(t => t.stop())`
  en el evento de cambio de vista y al cerrar el diálogo.
- SLA: medir desde la petición hasta el render; objetivo <3 s con 100 equipos de prueba.
- El QR NO autoriza: siempre se valida el préstamo en backend.

## Riesgos y mitigación
- Riesgo: `BarcodeDetector` no disponible. Mitigación: entrada manual siempre visible.
- Riesgo: falso positivo de SLA en entorno local. Mitigación: prueba con datos representativos y documento de entorno.

## Compatibilidad
El endpoint actual de verificación mantiene su contrato de éxito; se añade el evento y la medición.
