# DiseÃ±o: acceso usable en el primer arranque

## DecisiÃ³n

Nuevo mÃ³dulo `prestatec/demo.py` con `preparar_demo(servicio, almacen)`:

- Recibe el `InventoryService` y el `AlmacenCredenciales` **ya construidos** por
  la aplicaciÃ³n, para que el usuario de negocio quede visible en la misma
  instancia que atiende las peticiones HTTP.
- Para cada cuenta, consulta `almacen.rol(documento)`; solo crea la credencial
  si devuelve `None`. Nunca llama a `crear()` sobre un documento existente.
- Comprueba `servicio.listar_usuarios()`; registra `estudiante` solo si falta.
- Devuelve un diccionario con lo creado, para que la salida sea auditable.

## ActivaciÃ³n

- `run.py --demo`: llama a `preparar_demo` con `app.service` y
  `app.identidad.almacen`, imprime el resumen y luego levanta el servidor.
- `scripts/crear_demo.py`: CLI dedicada para preparar los archivos sin iniciar el
  servidor. Acepta rutas propias para pruebas.
- `python run.py` sin bandera **no crea nada**: las claves conocidas nunca se
  escriben de forma silenciosa.

## Compatibilidad

- No cambia la firma de `PrestaTecApp`, `InventoryService` ni
  `AlmacenCredenciales`.
- Los archivos se escriben con los mismos formatos de siempre.
- Las pruebas existentes no dependen de credenciales del repositorio.

## VerificaciÃ³n

`tests/test_demo.py` comprueba los cuatro criterios con `tmp_path`, incluido un
login real mediante `app.dispatch`. Debe fallar antes de crear el mÃ³dulo.
