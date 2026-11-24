# Delta: identidad y control de acceso

## ADDED Requirements

### SEC-01 - Autenticación obligatoria
Toda ruta `/api/...` DEBE exigir identidad autenticada. Una petición anónima
DEBE recibir `401` y no revelar datos.

#### Escenario: anónimo
- DADO un cliente sin sesión
- CUANDO consulta `/api/usuarios`
- ENTONCES recibe `401` y ningún documento de usuario

### SEC-02 - Autorización en lógica de negocio
Los permisos DEBEN comprobarse en los casos de uso, además de en la interfaz.
Un rol sin permiso DEBE recibir `403`.

#### Escenario: Guarda intenta registrar usuario
- DADO un usuario autenticado con rol `Guarda`
- CUANDO intenta crear un usuario
- ENTONCES recibe `403` y no se crea el registro

#### Escenario: Encargado entrega equipo
- DADO un usuario con rol `Encargado`
- CUANDO registra una entrega
- ENTONCES la operación se permite y queda asociada a su identidad

### SEC-03 - Contraseñas protegidas
NINGUNA contraseña DEBE almacenarse en texto plano ni incluirse en el repositorio.

#### Escenario: hash
- DADO un usuario registrado con contraseña
- CUANDO se inspecciona el almacenamiento
- ENTONCES solo existe un hash con salt, nunca el texto original

### SEC-04 - Proveedor intercambiable
La autenticación DEBE estar detrás de un adaptador para permitir SSO futuro sin
modificar el dominio ni los casos de uso.

#### Escenario: cambio de proveedor
- DADO el proveedor local temporal
- CUANDO se sustituye por un adaptador institucional
- ENTONCES las reglas de negocio y las pruebas de roles permanecen válidas
