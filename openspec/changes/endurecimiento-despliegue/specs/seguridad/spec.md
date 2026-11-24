# Delta: endurecimiento y despliegue

## ADDED Requirements

### OPS-01 - Configuración por entorno
Toda credencial, ruta productiva y parámetro de despliegue DEBE configurarse por
entorno. DEBE existir un archivo de ejemplo sin valores reales.

#### Escenario: sin secretos versionados
- DADO el repositorio completo
- CUANDO se buscan contraseñas o claves
- ENTONCES solo aparecen nombres de variables en `.env.example`

### OPS-02 - Protección CSRF
TODA petición mutante DEBE exigir un token válido ligado a la sesión.

#### Escenario: mutación sin token
- DADO un usuario autenticado
- CUANDO envía un POST sin token CSRF
- ENTONCES recibe `403` y no se modifica ningún dato

### OPS-03 - Errores sin fuga de información
Las respuestas de error NO DEBEN incluir stack traces, rutas internas ni datos
de otros usuarios. El detalle DEBE quedar solo en logs del servidor.

#### Escenario: error interno
- DADO una falla inesperada en el servidor
- CUANDO el cliente recibe la respuesta
- ENTONCES ve un mensaje genérico y un código de correlación

### OPS-04 - Perfil de despliegue documentado
La decisión entre ejecución local e intranet institucional DEBE documentarse
como dependiente de DEC-07, sin asumir infraestructura no validada.

#### Escenario: decisión abierta
- DADO DEC-07 sin resolver
- CUANDO se prepara el despliegue
- ENTONCES el sistema funciona en perfil local y el perfil institucional queda documentado como pendiente
