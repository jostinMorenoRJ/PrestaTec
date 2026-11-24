# Delta: perfiles por rol y experiencia (C12)

## ADDED Requirements

### PER-01 - Roles permitidos

El sistema DEBE operar únicamente con los roles `Consulta`, `Guarda` y
`Encargado`. `Estudiante` y `Docente` DEBEN traducirse a `Consulta`.
`Administrador` y `Soporte` NO DEBEN aceptarse al crear credenciales ni
resolver una sesión.

#### Escenario: alta de rol eliminado
- DADO el comando `identificar.py crear ... --rol Administrador`
- CUANDO se intenta crear la credencial
- ENTONCES se rechaza con un error que lista los roles permitidos

#### Escenario: credencial heredada inválida
- DADO un `identidades.json` con una credencial de rol `Administrador`
- CUANDO se intenta iniciar sesión con ella
- ENTONCES se responde `401` y no se emite token

### PER-02 - Vista por perfil

`/api/auth/me` DEBE incluir `vistaInicial` con valor `mis`, `porteria` o
`gestion` según el rol. La interfaz DEBE mostrar solo la navegación y las
acciones correspondientes a ese perfil.

#### Escenario: ingreso de cada perfil
- DADO un usuario autenticado
- CUANDO carga la aplicación
- ENTONCES ve “Mis préstamos”, “Portería” o “Gestión” según su rol, sin
  pestañas de otros perfiles

### PER-03 - Solicitud propia

Solo `Consulta` PUEDE crear reservas, y el documento DEBE ser el de la sesión.
Un documento distinto DEBE recibir `403`. Un solapamiento DEBE responder `409`
con un campo `alternativas` con equipos libres del mismo tipo.

#### Escenario: estudiante reserva para otro
- DADO un usuario `Consulta` con documento `1001`
- CUANDO envía `POST /api/reservas` con documento `1002`
- ENTONCES recibe `403` y no se crea la reserva

#### Escenario: conflicto con alternativas
- DADO un equipo ya reservado en el intervalo
- CUANDO `Consulta` solicita ese mismo equipo
- ENTONCES recibe `409`, un `mensaje` y una lista `alternativas`

### PER-04 - Ámbito de datos

`Consulta` SOLO PUEDE consultar sus préstamos mediante `/api/mis-prestamos`.
`/api/reservas`, `/api/usuarios` y `/api/resumen` DEBEN exigir permisos de
gestión. La interfaz de Consulta DEBE invocar `/api/disponibilidad` antes de
ofrecer equipos para reservar.

#### Escenario: consulta ajena
- DADO un usuario `Consulta`
- CUANDO solicita `GET /api/reservas` o `GET /api/usuarios`
- ENTONCES recibe `403`

#### Escenario: disponibilidad en la interfaz
- DADO el formulario de solicitud de préstamo
- CUANDO se eligen tipo y fechas
- ENTONCES la interfaz consulta `/api/disponibilidad` y muestra solo equipos
  libres

### PER-05 - Trazabilidad y reportes

La entrega DEBE persistir `estadoEntrega` en el préstamo. Toda verificación de
portería (autorizada, alerta o desconocida) DEBE registrar un evento. El reporte
CSV DEBE mostrar el nombre del equipo en la columna “Equipo”.

#### Escenario: entrega con estado
- DADO un préstamo entregado con `estadoEntrega: "Regular"`
- CUANDO se inspecciona el préstamo
- ENTONCES conserva `estadoEntrega: "Regular"`

#### Escenario: auditoría de portería
- DADO un equipo con préstamo activo
- CUANDO portería valida su código correctamente
- ENTONCES se añade un evento con la identidad del verificador

### PER-06 - Compatibilidad de datos

Un archivo JSON que contenga simultáneamente claves legado (`Equipos`,
`Reservas`) y nuevas (`equipos`, `prestamos`) NO DEBE descartar ninguna de las
dos colecciones. Las entradas duplicadas por identificador DEBEN resolverse a
favor de la clave nueva.

#### Escenario: JSON mixto
- DADO un JSON con `Equipos: [PT-009]` y `equipos: [PT-050]`
- CUANDO se carga el inventario
- ENTONCES aparecen `PT-009` y `PT-050`

### PER-07 - Calidad de interfaz

La interfaz DEBE ofrecer estados vacíos, mensajes de éxito/error, indicación de
carga, foco visible y diseño adaptable a móvil. NO DEBE contener botones sin
controlador asociado.

#### Escenario: sin resultados
- DADO una búsqueda de disponibilidad sin equipos libres
- CUANDO se muestra el resultado
- ENTONCES se explica el motivo y se sugiere cambiar fechas

## Modified Requirements

Ninguno. Los requisitos RF01..RF09 y SEC-01..SEC-04 permanecen vigentes salvo
por la restricción explícita de roles de PER-01.
