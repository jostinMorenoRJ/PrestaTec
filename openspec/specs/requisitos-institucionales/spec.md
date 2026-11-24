# Especificación: requisitos institucionales de PrestaTec 2.0

Esta spec es el registro normativo derivado del taller y de las reglas internas.
Los cambios en `openspec/changes/` añaden o modifican capacidades referenciando
estos IDs. Ningún requisito marcado como `P0` puede declararse terminado sin su
prueba pytest correspondiente.

> Los estados `Verificado`, `Parcial` e `Incumplido` describen la **línea base de
> la Etapa 1**, no un estado final. Las 12 pruebas originales tienen otros nombres;
> las pruebas con prefijo `INST-##` de `openspec/evidencia/trazabilidad.md` se crearán en la
> Etapa 5 y deberán pasar en RED→GREEN antes de marcar el requisito como terminado.

## Convención de IDs

- `INST-##`: alcance mínimo funcional (master prompt §6.A).
- `PDF-RNF##`: requisitos no funcionales del taller.
- `RES-##`, `EXC-##`: restricciones y excepciones del taller (§5.4-5.5).
- `INT-##`: reglas internas de `AGENTS.md.txt`.
- `DEC-##`: decisiones institucionales pendientes.

## A. Alcance mínimo funcional

| ID | Prioridad | Estado | Criterio de aceptación |
|---|---|---|---|
| INST-01 | P0 | Verificado | Registrar equipo con código único; rechazar nombre vacío, tipo inválido o duplicado; persistir tras reinicio. |
| INST-02 | P0 | Verificado | Registrar usuario con documento único y rol válido; rechazar duplicados; persistir. |
| INST-03 | P0 | Parcial | Prestar solo equipo disponible a usuario registrado; `fin > inicio`; sin solape; responsable de entrega; rechazar con alternativas. |
| INST-04 | P0 | Parcial | Devolver solo préstamo entregado; fecha real, observaciones y responsable; daño bloquea el equipo. |
| INST-05 | P0 | Parcial | Consultar disponibles por estado y por rango; excluir mantenimiento, fuera de servicio, prestados y reservados. |
| INST-06 | P0 | Verificado | Consultar préstamos activos, titular, equipo, fecha prevista y atrasos. |

## B. Requisitos no funcionales

| ID | Prioridad | Estado | Criterio de aceptación |
|---|---|---|---|
| PDF-RNF01 | P0 | Incumplido | Autenticación y RBAC en API y lógica de negocio; anónimo recibe 401; roles Guarda/Encargado/Soporte/Administrador/Consulta; contraseñas con hash; sin secretos en repo. |
| PDF-RNF02 | P1 | Parcial | Verificación en portería <3 s, único umbral establecido por el taller. No se fija meta numérica para otras operaciones (DEC-09). |
| PDF-RNF03 | P1 | Parcial | Interfaz clara, responsive, con etiquetas, mensajes y estados vacíos; ningún botón sin función. |
| PDF-RNF04 | P0 | Incumplido | Persistencia segura, transaccional, con copia y restauración verificables; migración sin pérdida; no borrar datos sin autorización. |

## C. Restricciones y excepciones

| ID | Prioridad | Criterio de aceptación |
|---|---|---|
| RES-01 | P1 | Funciones críticas operan sin CDN; QR empaquetado o con fallback. |
| RES-02 | P0 | Acceso limitado por tipo de usuario; cubierto por PDF-RNF01. |
| RES-03 | P0 | Histórico inmutable ante ediciones o bajas; actor y timestamp en cada evento. |
| EXC-01 | P1 | Registro manual de "No se presentó"; automatización supeditada a DEC-03. |
| EXC-02 | P1 | Atraso detectado desde datos reales; daño bloquea equipo; sanciones supeditadas a DEC-04. |
| EXC-03 | P1 | Falla sobre equipo reservado se registra sin eliminar reservas; reprogramación supeditada a DEC-03. |

## D. Reglas internas obligatorias

| ID | Prioridad | Criterio de aceptación |
|---|---|---|
| INT-01 | P0 | Ningún cambio de código sin spec aprobada en OpenSpec. |
| INT-02 | P0 | Prueba pytest ejecutada en RED antes de implementar; evidencia registrada. |
| INT-03 | P0 | Migración con copia previa y rollback; sin borrado sin autorización. |
| INT-04 | P1 | API no accede directamente al almacenamiento; UI no contiene reglas de negocio. |
| INT-05 | P1 | Trazabilidad UI → endpoint → caso de uso → prueba. |
| INT-06 | P1 | Suite pytest ejecutada tras cada cambio; sin afirmaciones no verificadas. |
| INT-07 | P1 | Git inicializado, commits descriptivos y decisiones técnicas documentadas. |

## E. Decisiones pendientes

| ID | Decisión | Efecto mientras no se resuelva |
|---|---|---|
| DEC-01 | Tiempo máximo de préstamo por tipo | No se valida duración, solo se registra fecha. |
| DEC-02 | Anticipación de reservas | No se rechaza reserva por anticipación. |
| DEC-03 | Quién aprueba/cancela/modifica y expiración | No hay aprobación ni expiración automática. |
| DEC-04 | Sanciones por atraso/daño | Solo se registra novedad, sin sanción. |
| DEC-05 | Correo / sistema académico | Notificaciones e integración fuera de alcance. |
| DEC-06 | Retención histórica | No se purga nada; retención configurable sin valor por defecto. |
| DEC-07 | SSO, red, HTTPS, lectores y navegadores | Proveedor local temporal y QR offline. |
| DEC-08 | Dueño de datos, hojas reales y códigos | Migración solo desde `data.json` y formatos presentes. |
| DEC-09 | Umbral de respuesta para operaciones distintas de portería | No se define meta numérica; solo se mide el SLA de portería. |

## F. Regla de prevalencia

Si una mejora propuesta contradice `INST-##`, `PDF-RNF##`, `RES-##`, `EXC-##` o
`INT-##`, prevalece el requisito. Si un requisito depende de `DEC-##`, se documenta
la incertidumbre y no se establece una regla definitiva.
