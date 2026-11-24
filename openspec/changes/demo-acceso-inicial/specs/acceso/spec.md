# Delta de spec: acceso — demostración explícita

## ADDED Requirements

### DEMO-01 Cuentas visibles que funcionan

Las tres cuentas mostradas en la pantalla de acceso deben poder iniciar sesión
después de ejecutar la preparación explícita de la demostración.

#### Scenario: primer arranque con preparación

- **GIVEN** un clon limpio sin `identidades.json` ni usuario de negocio
  `estudiante`
- **WHEN** se ejecuta la preparación explícita
- **THEN** las credenciales `admin`, `celador` y `estudiante` verifican con las
  claves mostradas en pantalla
- **AND** sus roles son `Encargado`, `Guarda` y `Consulta`

### DEMO-02 Usuario de negocio para `estudiante`

#### Scenario: reserva con la cuenta de consulta

- **GIVEN** la preparación explícita ya se ejecutó
- **WHEN** se consultan los usuarios de negocio
- **THEN** existe un usuario con documento `estudiante`

### DEMO-03 Sin sobrescritura

#### Scenario: preparación repetida o datos propios previos

- **GIVEN** una credencial ya creada con otra contraseña, o un usuario
  `estudiante` ya registrado con otro nombre
- **WHEN** se ejecuta la preparación
- **THEN** la contraseña y el nombre anteriores se conservan
- **AND** el informe solo lista lo que realmente se creó

### DEMO-04 Login en la app que sirve la interfaz

#### Scenario: petición HTTP real tras la preparación

- **GIVEN** una instancia de `PrestaTecApp` construida antes de la preparación
- **WHEN** se prepara la demo con esos mismos objetos y se envía
  `POST /api/auth/login` con `admin` / `admin123`
- **THEN** la respuesta es `200` y contiene un token

## Impacto en requisitos existentes

| Requisito | Cambio |
|---|---|
| ACC-02 Pantalla de acceso | Las cuentas anunciadas dejan de ser engañosas tras la preparación |
| PDF-RNF01 Autenticación | La creación sigue siendo explícita; no se abre una puerta automática |
