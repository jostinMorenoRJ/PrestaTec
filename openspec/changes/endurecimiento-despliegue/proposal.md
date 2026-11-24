# Propuesta: endurecimiento y despliegue (C11)

## Problema
El servidor actual es un `ThreadingHTTPServer` local sin HTTPS, CSRF, secretos
gestionados ni logs centralizados. Trasladarlo a la intranet sin estas medidas
agrava las brechas de RNF01 y RNF04. La infraestructura definitiva depende de
DEC-07.

## Qué cambia
- Configuración por entorno con archivo de ejemplo.
- HTTPS/red invertida según decisión institucional; CSRF en mutaciones.
- Secretos fuera del repositorio y errores sin información sensible.
- Logs estructurados sin datos personales innecesarios.

## Fuera de alcance
Publicación en GitHub sin permisos, Postgres y SSO (DEC-05/DEC-07, O5).

## Capacidades afectadas
- seguridad
- persistencia

## Impacto esperado
Deja el sistema preparado para operación institucional sin fijar proveedor ni
arquitectura de red hasta la validación.
