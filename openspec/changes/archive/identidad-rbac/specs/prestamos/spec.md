# Delta: identidad y control de acceso (spec de préstamos)

## MODIFIED Requirements

### RF01 - Usuarios autorizados
Un usuario registrado NO queda autorizado automáticamente. La autorización
depende de una identidad autenticada y de un rol con permiso vigente (SEC-01,
SEC-02). El registro sigue exigiendo documento único y rol válido.

#### Escenario: registro sin identidad autenticada
- DADO un cliente anónimo
- CUANDO intenta registrar un usuario
- ENTONCES recibe `401` y no se crea el registro

#### Escenario: rol sin permiso
- DADO un usuario autenticado con rol `Guarda`
- CUANDO intenta registrar un usuario
- ENTONCES recibe `403`, con independencia de que los datos sean válidos
