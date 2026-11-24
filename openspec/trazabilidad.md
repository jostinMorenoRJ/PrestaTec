# Matriz de trazabilidad — PrestaTec 2.0

Relación verificable entre requisito institucional, especificación OpenSpec,
prueba pytest (a crear en Etapa 5) e implementación (a partir de Etapa 7).

**Estado:** C0–C5 ejecutados. La columna "Prueba" conserva el nombre planificado
cuando aún no se ha creado; donde existe una prueba real se indica su ruta. La
columna "Implementación" solo se completa con módulos y commits verificados.
Los requisitos marcados como *parcial* tienen otros changes pendientes.

| Requisito | Change / Spec | Prueba planificada (Etapa 5) | Implementación |
|---|---|---|---|
| INST-01 Registrar equipos | `gobernanza-linea-base`, `repositorio-interfaz` | `test_INST01_codigo_unico` | — |
| INST-02 Registrar estudiantes | `gobernanza-linea-base`, `identidad-rbac` | `tests/test_web.py::test_api_rechaza_documento_repetido` | `prestatec/service.py` (C1/C5) |
| INST-03 Prestar disponibles | `reloj-politicas`, `disponibilidad-conflictos` | `test_INST03_rechaza_prestado` | — |
| INST-04 Registrar devolución | `prestamo-trazable` | `test_INST04_devolucion_registra_responsable` | — |
| INST-05 Consultar disponibles | `disponibilidad-conflictos` | `test_INST05_filtro_rango_comparte_regla_con_api` | — |
| INST-06 Consultar prestados | `reloj-politicas` | `test_INST06_atrasado_desde_reloj_utc` | — |
| PDF-RNF01 Autenticación/RBAC | `identidad-rbac` (`seguridad/spec.md` SEC-01..04) | `tests/test_seguridad.py` (9), `tests/test_autorizacion_casos_uso.py` (3), `tests/test_run_http.py` (1) | `prestatec/identidad.py`, `prestatec/web.py`, `prestatec/service.py`, `run.py`, `identificar.py` (C5, `c70206e`) |
| PDF-RNF02 Operaciones rápidas | `porteria-confiable` (POR-01) | `test_RF09_verificacion_menos_3s` | — |
| PDF-RNF03 Interfaz clara | `disponibilidad-conflictos` (DIS-02) | `test_RNF03_ui_llama_disponibilidad_antes_de_listar` | — |
| PDF-RNF04 Almacenamiento y respaldo | `persistencia-sqlite` + `respaldo-restauracion` (DAT-01..06) | `tests/test_persistencia.py` (5), `tests/test_configuracion.py` (2), `tests/test_migracion_cli.py` (1), `tests/test_respaldo.py` (7) | `prestatec/sqlite_repository.py`, `prestatec/migracion.py`, `prestatec/config.py`, `prestatec/backup.py`, `migrar.py`, `respaldar.py` (C3–C4) |
| RES-01 Sin CDN | `porteria-confiable` (POR-02) | `test_RF09_qr_offline_sin_cdn` | — |
| RES-02 Acceso por tipo | `identidad-rbac` (SEC-02) | `test_RNF01_encargado_entrega_y_devuelve_asociado_a_identidad`, `test_RNF01_permisos_de_reporte_y_historial` | `prestatec/identidad.py`, `prestatec/web.py`, `static/app.js` (C5, `c70206e`) |
| RES-03 Conservación/trazabilidad | `auditoria` (AUD-01..03) + `reportes-retencion` (REP-03) | `test_RES03_toda_mutacion_genera_un_evento`, `test_RES03_historial_inmutable` | — |
| EXC-01 No se presentó | spec base RF04/RF05 (ya implementado) | `test_EXC01_no_se_presento_registrado` (caracterización) | — |
| EXC-02 Atraso y daño | `prestamo-trazable` (PRE-01, RF07) | `test_RF06_entrega_fuera_de_ventana_se_registra_sin_sancionar` | — |
| EXC-03 Falla sobre reservado | `auditoria` (AUD-01) | `test_EXC03_falla_no_elimina_reserva` | — |
| INT-01 SDD | `gobernanza-linea-base` (GOV-02) | Verificación de artefactos OpenSpec | — |
| INT-02 TDD RED→GREEN→REFACTOR | todos los changes | Evidencia de ejecución RED registrada en cada `tasks.md` | — |
| INT-03 No borrar datos | `persistencia-sqlite` (DAT-02/04), `respaldo-restauracion` (DAT-05/06) | `test_DAT02_migracion_mixta_conserva_legacy_y_nuevo`, `test_DAT02_rechaza_sobrescribir_destino_sin_autorizacion`, `test_DAT06_no_purga_copias` | `prestatec/migracion.py` (C3), `prestatec/backup.py` (C4) |
| INT-04 Separación de capas | `repositorio-interfaz` (ARQ-01) | `tests/test_repositorio.py` (4 pruebas, `a9aef30`) | `prestatec/repository.py`, `prestatec/service.py` (`a9aef30`) |
| INT-05 Sin botones muertos (*parcial*) | `identidad-rbac` (SEC-02) + `disponibilidad-conflictos` (DIS-02) | verificación en navegador registrada en `ejecucion-c5.md`; falta `test_RNF03_ui_llama_disponibilidad_antes_de_listar` | `static/app.js` (C5, `c70206e`) |
| INT-06 Ejecutar pruebas | `gobernanza-linea-base` (GOV-01) | suite completa ejecutada: 19 → 23 → 27 → 35 → 42 → 57 pruebas | `pyproject.toml`, `openspec/ejecucion-c0.md` … `ejecucion-c5.md` |
| INT-07 Git y decisiones | `gobernanza-linea-base` (INT-07) | `git log --oneline`: `8a92475`, `96038a3`, `a9aef30`, `57aaf28`, `170c221`, `88560ef` | repo local inicializado; sin remoto ni publicación |
| ARC-01/02 Repositorio inyectado | `repositorio-interfaz` | `tests/test_repositorio.py` | `prestatec/repository.py` (`a9aef30`) |
| ARC-03 Reloj UTC | `reloj-politicas` | `tests/test_reloj.py` (4 pruebas) | `prestatec/reloj.py`, `prestatec/service.py` (`57aaf28`) |
| ARC-04 Políticas inyectables | `reloj-politicas` | `test_ARC04_politica_sin_valor_no_rechaza_por_duracion` | `prestatec/politicas.py` (`57aaf28`) |
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
| DEC-07 SSO / red / lectores | SEC-04 verifica adaptador; C5 implementa el proveedor local, no SSO. POR-01 usará entorno de prueba, no hardware real. |
| DEC-08 Dueño / hojas / códigos | DAT-02 cubre solo `data.json` y formatos presentes. |
| DEC-09 Umbral de otras operaciones | No hay prueba de SLA fuera de portería; POR-01 mide solo RF09. |

## Criterio de "terminado"

Un requisito solo se marca como terminado cuando:

1. Su spec OpenSpec está aprobada y archivada.
2. Su prueba pytest fue vista fallar en RED y luego pasar en GREEN.
3. La suite completa pasa tras REFACTOR.
4. La celda "Implementación" de esta matriz contiene la ruta del módulo y el commit.
