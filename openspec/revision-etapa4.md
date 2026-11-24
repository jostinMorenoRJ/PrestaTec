# Revisión — Etapa 4

Fecha: 24/11/2026. Alcance: los 12 changes, las 2 specs base, `config.yaml`,
`project.md` y `trazabilidad.md`. Resultado: **aprobado con correcciones**.

No se crearon pruebas ni se modificó código de producción. Todas las correcciones
fueron de documentación OpenSpec.

## 1. Hallazgos corregidos

| # | Hallazgo | Corrección aplicada |
|---|---|---|
| R1 | `PDF-RNF02` incluía una meta inventada de "<1 s para consultas comunes", no exigida por el taller. | Eliminada del criterio de aceptación. Solo se mide el SLA de portería (<3 s). Se creó `DEC-09` para documentar que no hay umbral para otras operaciones. |
| R2 | `identidad-rbac` añadía SEC-01..04 pero no declaraba la modificación de `RF01` ("usuarios autorizados" por el hecho de estar registrados). | Nuevo `changes/identidad-rbac/specs/prestamos/spec.md` con `MODIFIED RF01` y dos escenarios (`401` anónimo, `403` sin permiso). |
| R3 | El índice de changes decía que `reloj-politicas` atendía `DEC-01..DEC-06`, cuando solo prepara contenedores sin resolverlos. | Reformulado: "prepara DEC-01..DEC-06 sin resolverlos". |
| R4 | `POR-01` prometía medir "respuesta visible" con pytest, lo que incluiría render de navegador y lector físico (no verificable con pytest por sí solo). | Reformulado: pytest mide petición/respuesta de API; render y hardware quedan documentados como limitación ligada a `DEC-07`. Escenario renombrado a "medición automatizada". |
| R5 | `reportes-retencion` citaba `O2` para PDF/Excel, pero `O2` corresponde a sanciones. | Corregido a `FUN-A2`. |
| R6 | `config.yaml` afirmaba "9 páginas" del PDF sin verificación en esta etapa. | Eliminado el número de páginas. |
| R7 | Los estados `Verificado`/`Parcial` de la spec normativa podían leerse como estado final, y las pruebas `INST-##` no existen aún. | Añadida nota de línea base: las 12 pruebas originales tienen otros nombres; las pruebas con prefijo se crean en Etapa 5. |
| R8 | La matriz RBAC permitía al Guarda verificar en portería pero no consultar historial; no se había acotado qué datos devuelve la verificación. | Añadida nota en `design.md`: respuesta mínima (préstamo, equipo, titular, estado), sin historial completo. |
| R9 | Anglicismo "copia opportunistica" en el diseño de respaldo. | Corregido a "copia oportunista". |
| R10 | `trazabilidad.md` no reflejaba `DEC-09`. | Añadida la fila correspondiente. |

## 2. Comprobaciones que pasaron sin cambios

- **Orden de dependencias:** C0 → C1 → C2 → C3 → C4 → C5 → C6 → C7 → C8 → C9 → C10 → C11 respeta el grafo de la Etapa 1. C5 va después de C3; C6 después de C5; C7–C9 después de C5/C6; C10 después de C8.
- **Prevalencia institutional:** ningún change contradice `INST-##`, `PDF-RNF##`, `RES-##`, `EXC-##` ni `INT-##`. El único cambio deliberado de comportamiento (`400 → 409`) está documentado como caracterización en C0 y modificado con spec en C7.
- **Decisiones pendientes:** ninguna spec fija plazos, anticipación, aprobación, sanciones, retención, SSO ni infraestructura. `PRE-01` y `REP-04` verifican explícitamente que no se aplican.
- **Atomicidad de changes:** los 12 son reversibles por commit y tienen spec, diseño, tareas y al menos un escenario DADO/CUANDO/ENTONCES.
- **Cobertura de trazabilidad:** los 6 requisitos mínimos, 4 RNF, 3 restricciones, 3 excepciones, 7 reglas internas y RF08/RF09 tienen fila en la matriz.
- **Sin secretos ni datos reales:** no hay credenciales, rutas productivas ni registros institucionales en los artefactos.

## 3. Riesgos residuales que permanecen abiertos

| Riesgo | Origen | Tratamiento |
|---|---|---|
| Matriz RBAC no validada por la universidad | DEC-07 / gobernanza | Está en `design.md` como propuesta; cambiará como configuración, no como código. |
| SLA extremo a extremo sin navegador ni lector real | DEC-07 | Se mide API con pytest; la prueba con hardware se declara pendiente, no aprobada. |
| Historial inmutable vs. derecho a corrección de datos personales | DEC-06 | Las correcciones se registran como eventos nuevos; la purga sigue desactivada. |
| Migración de hojas de cálculo reales | DEC-08 | Fuera de alcance; solo se migra `data.json` y formatos presentes. |
| UI accesible y sin `prompt()` | RNF03 | La spec exige mensajes y estados vacíos; el rediseño visual se ejecuta en Etapa 10, después de la lógica. |
| Sin repositorio Git aún | C0, INT-07 | La Etapa 5 puede empezar con la infraestructura de C0; no se ha inicializado `.git` en esta revisión. |

## 4. Conclusión

Las specs están **listas para la Etapa 5 (Pruebas)**. El alcance de la primera
iteración de pruebas será `gobernanza-linea-base` (C0): caracterizar el
comportamiento actual y crear el andamiaje de pytest. No se creará código de
negocio hasta que esa prueba haya sido vista fallar en RED.
