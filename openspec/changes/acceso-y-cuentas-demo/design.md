# Diseño C13 — acceso visible y cuentas de demostración

## Enfoque

1. **Datos:** se hace un respaldo con marca de tiempo de `identidades.json`, se
   eliminan solo las credenciales `admin`, `1001234567`, `900001` y `52111222`,
   y se crean las tres cuentas nuevas con `AlmacenCredenciales.crear()`, que
   aplica PBKDF2 y valida el rol. `data.json` se enriquece de forma aditiva con
   tres usuarios de negocio (`admin`, `celador`, `estudiante`) para que la UI
   muestre nombres y `estudiante` pueda solicitar préstamos.
2. **Interfaz:** nuevo `<section id="acceso">` fuera de `main` y de `header`,
   con diseño de dos columnas (marca/beneficios + tarjeta de acceso). El
   formulario `#fl` se mueve dentro de la tarjeta; mantiene `name="documento"`
   y `name="contraseña"` para no tocar el contrato de `/api/auth/login`.
3. **Estado:** `aplicarPermisos()` pasa a ocultar `#acceso` en vez de `#fl`;
   `body.con-sesion #acceso { display:none }` y `body.sin-sesion .topbar, main
   { display:none }` garantizan que solo se vea una pantalla a la vez.
4. **Errores:** `#error-acceso` muestra el mensaje de credenciales inválidas
   dentro de la tarjeta; se limpia al enviar y al cerrar sesión.

## Decisiones

- No se guardan contraseñas en texto plano: las de demostración aparecen en la
  UI porque son credenciales locales de prueba, no secretos de producción.
- No se purgan otros usuarios ni préstamos: solo se añaden los tres usuarios
  necesarios y se sustituyen las credenciales acordadas.
- La interfaz sigue dependiendo de `/api/auth/me`; no se introduce lógica de
  roles en el cliente más allá de `PERFILES` (C12).

## Riesgos

- Mostrar contraseñas en pantalla es inaceptable en un despliegue real. Queda
  registrado como decisión temporal de demostración; si se publica la app,
  debe eliminarse el bloque `acceso-cuentas` y cambiar las claves.
