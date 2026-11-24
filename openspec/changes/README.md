# Índice de changes de PrestaTec 2.0

Cada change es un incremento pequeño, reversible y verificable. El orden evita
reescritos: gobernanza → abstracción de datos → seguridad → funcionalidad →
despliegue. Los IDs `C0`..`C11` corresponden al plan priorizado de la Etapa 1.

| Orden | Change | IDs del plan | Requisitos atendidos | Estado |
|---|---|---|---|---|
| 1 | `gobernanza-linea-base` | C0 | INT-01..INT-07 | pendiente |
| 2 | `repositorio-interfaz` | C1 | INT-04 | pendiente |
| 3 | `reloj-politicas` | C2 | INST-03; prepara DEC-01..DEC-06 sin resolverlos | pendiente |
| 4 | `persistencia-sqlite` | C3 | PDF-RNF04, RES-03 | pendiente |
| 5 | `respaldo-restauracion` | C4 | PDF-RNF04 | pendiente |
| 6 | `identidad-rbac` | C5 | PDF-RNF01, RES-02 | pendiente |
| 7 | `auditoria` | C6 | RES-03 | pendiente |
| 8 | `disponibilidad-conflictos` | C7 | INST-03, INST-05, RF03, RF05 | pendiente |
| 9 | `prestamo-trazable` | C8 | INST-04, RF06, RF07, EXC-02 | pendiente |
| 10 | `porteria-confiable` | C9 | RF09, RES-01, PDF-RNF02 | pendiente |
| 11 | `reportes-retencion` | C10 | RF08, RES-03 | pendiente |
| 12 | `endurecimiento-despliegue` | C11 | PDF-RNF04, PDF-RNF02, DEC-07 | pendiente |

**Estado:** todos pendientes. Ningún change ha pasado a implementación; el
trabajo continúa en la Etapa 4 (Revisión) y Etapa 5 (Pruebas).
