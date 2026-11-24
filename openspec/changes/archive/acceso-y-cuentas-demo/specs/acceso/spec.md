# Delta de spec: acceso (C13)

Los identificadores `ACC-*` se añaden a la especificación vigente. No modifican
los requisitos PER-01..PER-07 de C12.

## ADDED Requirements

### Requirement: ACC-01 Cuentas de demostración

El sistema debe aceptar exactamente estas credenciales locales y resolver el
perfil indicado:

| Usuario | Contraseña | Perfil | Vista inicial |
|---|---|---|---|
| `admin` | `admin123` | `Encargado` | `gestion` |
| `celador` | `celador123` | `Guarda` | `porteria` |
| `estudiante` | `estudiante123` | `Consulta` | `mis` |

`admin` debe resolver `Encargado`; el rol `Administrador` sigue sin ser válido.
`estudiante` debe estar registrado como usuario de negocio para poder
solicitar préstamos.

#### Scenario: Ingreso con cada cuenta

- **GIVEN** el archivo de identidades del proyecto
- **WHEN** se autentica con usuario y contraseña de la tabla
- **THEN** se emite sesión y `/api/auth/me` devuelve el perfil y la vista inicial esperados

#### Scenario: Estudiante solicita préstamo

- **GIVEN** la cuenta `estudiante` con sesión `Consulta`
- **WHEN** solicita un equipo disponible
- **THEN** la reserva se registra con el documento `estudiante`

### Requirement: ACC-02 Pantalla de acceso completa

Sin sesión, la aplicación debe mostrar una pantalla de acceso a pantalla
completa con marca PrestaTec, título, campo `Usuario`, campo `Contraseña` y
botón `Ingresar`. La barra superior y el contenido de gestión deben permanecer
ocultos. Con sesión válida, la pantalla de acceso debe desaparecer.

#### Scenario: Apertura sin sesión

- **GIVEN** un navegador sin cookie de sesión
- **WHEN** se abre la raíz de la aplicación
- **THEN** se ve `#acceso` con el formulario y no se ve `header` ni `main`

#### Scenario: Ingreso correcto

- **GIVEN** el formulario de acceso visible
- **WHEN** se envían credenciales válidas
- **THEN** `#acceso` se oculta y se muestra la vista inicial del perfil

### Requirement: ACC-03 Cuentas visibles en la pantalla

La pantalla de acceso debe enumerar las tres cuentas de demostración con su
usuario, contraseña y perfil, e indicar que son credenciales locales de prueba.

#### Scenario: Usuario necesita saber con qué entrar

- **GIVEN** la pantalla de acceso sin sesión
- **WHEN** el usuario lee la tarjeta de acceso
- **THEN** encuentra `admin`/`admin123`, `celador`/`celador123` y `estudiante`/`estudiante123` con sus perfiles

### Requirement: ACC-04 Errores y accesibilidad

Un intento fallido debe mostrar el mensaje dentro de la tarjeta de acceso, sin
ocultar el formulario. Los campos deben tener etiquetas accesibles y foco
visible.

#### Scenario: Contraseña incorrecta

- **GIVEN** el formulario de acceso visible
- **WHEN** se envía una contraseña incorrecta
- **THEN** `#error-acceso` muestra "Credenciales inválidas." y el formulario sigue visible
