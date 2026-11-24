# Índice de changes de PrestaTec 2.0

Cada change es un incremento pequeño, reversible y verificable. El orden evita
reescritos: gobernanza → abstracción de datos → seguridad → funcionalidad →
despliegue. Los IDs `C0`..`C11` corresponden al plan priorizado de la Etapa 1.

**Ubicación:** los changes terminados (filas 1–6, 13 y 14) están en
`archive/`; en la raíz quedan los pendientes (7–12) y los tres ciclos formales
(15–17): dos del núcleo de préstamo y uno de acceso. Son los que interesan para
la entrega.

| Orden | Change | IDs del plan | Requisitos atendidos | Estado |
|---|---|---|---|---|
| 1 | `gobernanza-linea-base` | C0 | INT-01..INT-07 | completado (`8a92475`, `96038a3`) |
| 2 | `repositorio-interfaz` | C1 | INT-04 | completado (`a9aef30`) |
| 3 | `reloj-politicas` | C2 | INST-03; prepara DEC-01..DEC-06 sin resolverlos | completado (`57aaf28`) |
| 4 | `persistencia-sqlite` | C3 | PDF-RNF04, RES-03 | completado (`170c221`) |
| 5 | `respaldo-restauracion` | C4 | PDF-RNF04 | completado (`88560ef`) |
| 6 | `identidad-rbac` | C5 | PDF-RNF01, RES-02 | completado (`1b25d73`) |
| 7 | `auditoria` | C6 | RES-03 | pendiente |
| 8 | `disponibilidad-conflictos` | C7 | INST-03, INST-05, RF03, RF05 | pendiente |
| 9 | `prestamo-trazable` | C8 | INST-04, RF06, RF07, EXC-02 | pendiente |
| 10 | `porteria-confiable` | C9 | RF09, RES-01, PDF-RNF02 | pendiente |
| 11 | `reportes-retencion` | C10 | RF08, RES-03 | pendiente |
| 12 | `endurecimiento-despliegue` | C11 | PDF-RNF04, PDF-RNF02, DEC-07 | pendiente |
| 13 | `perfiles-y-experiencia` | C12 (adicional) | PER-01..PER-07; REFACTOR de defectos P3/P5/P6/P8/P9 | completado (`9eef23d`) |
| 14 | `acceso-y-cuentas-demo` | C13 (adicional) | ACC-01..ACC-04; pantalla de acceso y cuentas locales | completado (`2be8cd9`) |
| 15 | `devolucion-responsable` | Núcleo (RF06) | DEV-01..DEV-04; responsable de la devolución | completado (`a76091e` → `9fc38c1` → `9695bde`) |
| 16 | `devolucion-unica` | Núcleo (RF06) | DUP-01..DUP-03; segunda devolución rechazada | completado (`131d82c` → `d002ae0` → `6907506`) |
| 17 | `demo-acceso-inicial` | Acceso (DEMO) | DEMO-01..DEMO-04; login usable en el primer arranque | completado (`54c5d08` → `89b6938` → `4ab6f17`) |

**Estado:** C0–C5, C12, C13 y los tres changes principales —dos del núcleo de
préstamo (`devolucion-responsable`, `devolucion-unica`) y uno de acceso
(`demo-acceso-inicial`)— completados con evidencia
Spec → RED → GREEN (y REFACTOR en DUP) en `openspec/evidencia/ejecucion-c0.md` … `ejecucion-c5.md`,
`ejecucion-c12.md`, `ejecucion-c13.md`, `ejecucion-nucleo-dev.md`,
`ejecucion-devolucion-unica.md` y `ejecucion-demo.md`. El núcleo (`service.py` y
`test_prestamos.py`) proviene de la línea base `8a92475`, documentada en
`openspec/legacy/`; los tres changes principales son los ciclos formales
aplicados desde ahí, sin reescritura del historial. C6–C11 permanecen pendientes
y requieren autorización/decisiones institucionales según cada proposal. C12,
C13 y estos tres changes no sustituyen a los incrementos anteriores: corrigen defectos
documentados y aplican decisiones del usuario sobre perfiles, acceso local y
trazabilidad del núcleo.
