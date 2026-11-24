# Matriz de trazabilidad — PrestaTec 2.0

Relación verificable entre requisito institucional, especificación OpenSpec,
prueba pytest (a crear en Etapa 5) e implementación (a partir de Etapa 7).

**Estado:** la columna "Prueba" contiene el nombre planificado. Ninguna de estas
pruebas existe todavía: se crearán y ejecutarán en RED en la Etapa 5–6. La
columna "Implementación" permanecerá vacía hasta la Etapa 7.

| Requisito | Change / Spec | Prueba planificada (Etapa 5) | Implementación |
|---|---|---|---|
| INST-01 Registrar equipos | `gobernanza-linea-base`, `repositorio-interfaz` | `test_INST01_codigo_unico` | — |
| INST-02 Registrar estudiantes | `gobernanza-linea-base`, `identidad-rbac` | `test_INST02_documento_duplicado` | — |
| INST-03 Prestar disponibles | `reloj-politicas`, `disponibilidad-conflictos` | `test_INST03_rechaza_prestado` | — |
| INST-04 Registrar devolución | `prestamo-trazable` | `test_INST04_devolucion_registra_responsable` | — |
| INST-05 Consultar disponibles | `disponibilidad-conflictos` | `test_INST05_filtro_rango_comparte_regla_con_api` | — |
| INST-06 Consultar prestados | `reloj-politicas` | `test_INST06_atrasado_desde_reloj_utc` | — |
| PDF-RNF01 Autenticación/RBAC | `identidad-rbac` (`seguridad/spec.md` SEC-01..04) | `test_RNF01_anonimo_recibe_401`, `test_RNF01_guarda_no_registra_usuarios` | — |
| PDF-RNF02 Operaciones rápidas | `porteria-confiable` (POR-01) | `test_RF09_verificacion_menos_3s` | — |
| PDF-RNF03 Interfaz clara | `disponibilidad-conflictos` (DIS-02) | `test_RNF03_ui_llama_disponibilidad_antes_de_listar` | — |
| PDF-RNF04 Almacenamiento y respaldo | `persistencia-sqlite` + `respaldo-restauracion` (DAT-01..06) | `test_RNF04_migracion_mixta_sin_perdida`, `test_RNF04_restore_devuelve_estado_exacto` | — |
| RES-01 Sin CDN | `porteria-confiable` (POR-02) | `test_RF09_qr_offline_sin_cdn` | — |
| RES-02 Acceso por tipo | `identidad-rbac` (SEC-02) | `test_RNF01_encargado_entrega_y_devuelve` | — |
| RES-03 Conservación/trazabilidad | `auditoria` (AUD-01..03) + `reportes-retencion` (REP-03) | `test_RES03_toda_mutacion_genera_un_evento`, `test_RES03_historial_inmutable` | — |
| EXC-01 No se presentó | spec base RF04/RF05 (ya implementado) | `test_EXC01_no_se_presento_registrado` (caracterización) | — |
| EXC-02 Atraso y daño | `prestamo-trazable` (PRE-01, RF07) | `test_RF06_entrega_fuera_de_ventana_se_registra_sin_sancionar` | — |
| EXC-03 Falla sobre reservado | `auditoria` (AUD-01) | `test_EXC03_falla_no_elimina_reserva` | — |
| INT-01 SDD | `gobernanza-linea-base` (GOV-02) | Verificación de artefactos OpenSpec | — |
| INT-02 TDD RED→GREEN→REFACTOR | todos los changes | Evidencia de ejecución RED registrada en cada `tasks.md` | — |
| INT-03 No borrar datos | `persistencia-sqlite` (DAT-02/04), `respaldo-restauracion` (DAT-05/06) | `test_RNF04_migracion_mixta_sin_perdida` | — |
| INT-04 Separación de capas | `repositorio-interfaz` (ARQ-01) | `test_ARQ01_servicio_con_repositorio_falso` | — |
| INT-05 Sin botones muertos | `disponibilidad-conflictos` (DIS-02) | `test_RNF03_ui_llama_disponibilidad_antes_de_listar` | — |
| INT-06 Ejecutar pruebas | `gobernanza-linea-base` (GOV-01) | `pytest` en cada commit | — |
| INT-07 Git y decisiones | `gobernanza-linea-base` (INT-07) | `git log` + `openspec/` completo | — |
| RF08 Reportes | `reportes-retencion` (REP-01..04) | `test_RF08_csv_muestra_codigo_y_nombre_de_equipo` | — |
| RF09 Portería | `porteria-confiable` (POR-01..04) | `test_RF09_escaneo_no_autoriza_sin_prestamo_valido` | — |

## Reglas de decisión pendiente

| Decisión | Efecto en la trazabilidad |
|---|---|
| DEC-01 Plazo máximo | PRE-01 registra desviación; no hay prueba de rechazo por duración. |
| DEC-02 Anticipación | No hay prueba de rechazo por anticipación. |
| DEC-03 Aprobación / expiración | No hay prueba de aprobación ni de expiración automática. |
| DEC-04 Sanciones | No hay prueba de sanción; PRE-01 verifica explícitamente que no se aplica. |
| DEC-05 Correo / académico | Sin pruebas de notificación ni integración. |
| DEC-06 Retención | REP-04 verifica que no se purga nada. |
| DEC-07 SSO / red / lectores | SEC-04 verifica adaptador; POR-01 usa entorno de prueba, no hardware real. |
| DEC-08 Dueño / hojas / códigos | DAT-02 cubre solo `data.json` y formatos presentes. |
| DEC-09 Umbral de otras operaciones | No hay prueba de SLA fuera de portería; POR-01 mide solo RF09. |

## Criterio de "terminado"

Un requisito solo se marca como terminado cuando:

1. Su spec OpenSpec está aprobada y archivada.
2. Su prueba pytest fue vista fallar en RED y luego pasar en GREEN.
3. La suite completa pasa tras REFACTOR.
4. La celda "Implementación" de esta matriz contiene la ruta del módulo y el commit.
