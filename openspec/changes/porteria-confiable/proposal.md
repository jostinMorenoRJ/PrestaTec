# Propuesta: portería confiable (C9)

## Problema
La verificación responde rápido en la sonda (0,2 ms), pero no hay prueba del SLA
de <3 s extremo a extremo; el QR depende de un CDN y la cámara no se detiene al
cambiar de vista. Escanear un QR hoy no comprueba por sí solo la validez de la
operación (P4, P8, P11).

## Qué cambia
- Generación de QR con librería empaquetada o fallback offline.
- Cierre explícito de la cámara al salir de la vista.
- Auditoría de verificaciones correctas mediante C6.
- Verificación de préstamo válido y estado antes de cualquier salida.
- Medición del SLA <3 s.

## Fuera de alcance
Selección final de lectores/navegadores (DEC-07) y compra de hardware.

## Capacidades afectadas
- portería (nueva)
- seguridad

## Impacto esperado
Cierra RF09, RES-01 y PDF-RNF02, con funcionamiento garantizado sin conexión.
