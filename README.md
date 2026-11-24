# PrestaTec — sistema de préstamo de portátiles y proyectores

Aplicación web local desarrollada en Python. Permite administrar inventario, usuarios, reservas, entregas, devoluciones, daños, historial y validación rápida en portería. La interfaz está diseñada como un panel tipo landing page y funciona en el navegador.

## Núcleo pedido

| Lo solicitado | Dónde encontrarlo |
|---|---|
| **Especificación (SDD)** | `openspec/specs/prestamos/spec.md` (RF01–RF09) y el delta `openspec/changes/devolucion-responsable/specs/prestamos/spec.md` (RF06a) |
| **Pruebas (pytest)** | `tests/test_prestamos.py` — 11 pruebas de registro, préstamo, devolución, disponibilidad, daño, portería y persistencia |
| **Programa Python** | `prestatec/service.py` — `InventoryService`: `registrar_equipo`, `registrar_usuario`, `crear_prestamo`, `entregar`, `devolver`, `listar_equipos` |

**Ciclo Spec → Test → Código verificable en el historial:**

| Paso | Commit | Etiqueta |
|---|---|---|
| Spec (antes de la prueba) | `a76091e` | `nucleo-1-spec` |
| Prueba RED — 2 fallos, 77 en verde | `9fc38c1` | `nucleo-2-red` |
| Código GREEN — 79 en verde | `9695bde` | `nucleo-3-green` |

```powershell
git log --oneline --decorate -4
git show 9fc38c1    # la prueba todavía falla
git show 9695bde    # la implementación que la hace pasar
```

Etiqueta general del entregable: `nucleo`.

## Extras opcionales

Todo lo demás no exigido por el enunciado mínimo: autenticación y permisos
(`prestatec/identidad.py`), repositorio inyectado y SQLite
(`prestatec/repository.py`, `prestatec/migracion.py`), respaldos verificables
(`prestatec/backup.py`), perfiles e interfaz (`static/`), cuentas de
demostración C13, evidencias en `openspec/ejecucion-*.md` y el informe Word en
`documentacion/`. Cada extra tiene su propuesta en `openspec/changes/` y se
puede ignorar sin afectar al núcleo.

## 1. Requisitos

- Python 3.10 o superior.
- Visual Studio Code (recomendado: extensión **Python** de Microsoft).
- Conexión a Internet solo si se desea cargar las fuentes y el generador QR desde sus CDN. El sistema y sus funciones principales funcionan localmente.

No requiere Flask, Django ni una base de datos externa. Los datos se guardan en `data.json`.

## 2. Abrir y ejecutar en Visual Studio Code (Windows)

1. El proyecto ya está extraído en esta carpeta (contiene `run.py` en la raíz).
2. Abre Visual Studio Code y selecciona **Archivo → Abrir carpeta**. Escoge esta carpeta (`Proyecto`). VS Code detectará la configuración de `.vscode/`: pytest habilitado, tarea de pruebas y dos configuraciones de depuración.
3. Abre una terminal en VS Code: **Terminal → Nuevo terminal**.
4. Comprueba Python:

   ```powershell
   py --version
   ```

5. Crea el entorno virtual:

   ```powershell
   py -m venv .venv
   ```

6. Actívalo:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación, puedes ejecutar el programa directamente con `py run.py`, o usar CMD y ejecutar `.venv\Scripts\activate.bat`.

7. Instala pytest para ejecutar las pruebas:

   ```powershell
   py -m pip install -r requirements.txt
   ```

8. Inicia la aplicación:

   ```powershell
   py run.py
   ```

9. Abre en el navegador: **http://127.0.0.1:5080**.
10. Para apagar el servidor, vuelve a la terminal y pulsa **Ctrl + C**.

## 3. Ejecutar las pruebas TDD

Con la terminal situada en la carpeta del proyecto y pytest instalado:

```powershell
py -m pytest -v
```

La suite tiene **79 pruebas**: las 77 anteriores (dominio y HTTP, caracterización y cambios C1–C5, C12 y C13) más las 2 del ciclo `DEV-01`/`DEV-02` del núcleo. Las de caracterización documentan el comportamiento real: en C5 se actualizó la de acceso anónimo y en C12 las de los defectos P3/P6/P8/P9 corregidos por spec. En VS Code también puedes usar el panel **Testing** o la tarea **PrestaTec: ejecutar pruebas** (`Ctrl+Shift+B`).

Para ver solo el ciclo Spec → Test → Código del núcleo:

```powershell
py -m pytest tests/test_prestamos.py -v
```


Los marcadores configurados en `pyproject.toml` son `unit`, `integration`, `acceptance`, `nfr` y `characterization`. Por ejemplo:

```powershell
py -m pytest -m characterization -v
```

## 4. Datos de demostración

La primera ejecución crea `data.json` con seis equipos y cuatro usuarios de ejemplo.

| Tipo | Código | Nombre |
|---|---|---|
| Portátil | PT-001 | Lenovo ThinkPad E14 |
| Portátil | PT-002 | Dell Latitude 3420 |
| Portátil | PT-003 | HP ProBook 440 |
| Portátil | PT-004 | Acer Aspire 5 |
| Proyector | PR-001 | Epson X49 |
| Proyector | PR-002 | BenQ MS550 |

Documentos de ejemplo:

- Estudiante Ana Torres: `1001234567`
- Docente Brayan Ruiz: `79876543`
- Docente Omar Díaz: `80123456`
- Encargada Laura Gómez: `52111222`

Además, esta instalación tiene tres usuarios de acceso rápido (C13): `admin`, `celador` y `estudiante`. El último está dado de alta como usuario de negocio para poder solicitar préstamos.

**Decisión sobre datos:** `data.json` e `identidades.json` se mantienen fuera de Git (`.gitignore`) a propósito. `data.json` se regenera solo con equipos y usuarios de ejemplo, sin credenciales; los hashes PBKDF2 y sus salts viven en `identidades.json`. El ZIP `PrestaTec_2.0_entrega_20261124.zip`, incluido en la raíz del repositorio, trae ambos archivos ya poblados con los seis equipos, los cuatro usuarios base, los tres usuarios de acceso y sus credenciales: extráelo sobre la carpeta para arrancar con la demostración completa. Si prefieres recrear solo las credenciales:

```powershell
$env:PRESTATEC_ADMIN_PASSWORD='admin123'
py identificar.py crear admin --rol Encargado
$env:PRESTATEC_ADMIN_PASSWORD='celador123'
py identificar.py crear celador --rol Guarda
$env:PRESTATEC_ADMIN_PASSWORD='estudiante123'
py identificar.py crear estudiante --rol Consulta
```

`estudiante` también debe existir como usuario de negocio para poder reservar; se da de alta en **Usuarios** con documento `estudiante` (el ZIP ya lo incluye). Para reiniciar la demostración, detén el servidor, elimina `data.json` y vuelve a ejecutar `py run.py`: eso borra préstamos y usuarios de prueba, pero no toca `identidades.json`.

### Persistencia opcional (SQLite)

El sistema sigue usando `data.json` por defecto. Para migrar de forma explícita, abre la paleta de comandos de VS Code y ejecuta **Tasks: Run Task → PrestaTec: migrar data.json a SQLite**, o desde la terminal:

```powershell
py migrar.py
```

El proceso crea `data.json.bak` con el contenido original y calcula su SHA-256; no sobrescribe `data.json`, `prestatec.db` ni el respaldo si ya existen. Para reemplazarlos deliberadamente se requiere `--forzar`.

Para ejecutar con SQLite, configura el backend antes de iniciar el servidor:

```powershell
$env:PRESTATEC_BACKEND='sqlite'
$env:PRESTATEC_DATA_FILE='prestatec.db'
py run.py
```

Volver a `json` (o quitar las variables) restaura el comportamiento original sin tocar la lógica de negocio.

### Respaldos

Cada copia se guarda con timestamp UTC, SHA-256 y conteo de entidades; la migración deja un manifiesto verificable junto al respaldo. Desde VS Code: **Tasks: Run Task → PrestaTec: crear respaldo verificable**. Desde la terminal:

```powershell
py respaldar.py crear data.json --directorio backups
py respaldar.py restaurar backups\data_....manifest.json data.json --confirmar
```

`restaurar` valida hash y conteos antes y después de reemplazar el destino. Si el destino es más reciente que la copia, exige `--confirmar`. No hay purga automática: las copias se conservan mientras DEC-06 no defina una retención.

### Ingreso y permisos

Toda ruta `/api/...` exige sesión. La pantalla de acceso muestra las tres cuentas de demostración y sus claves:

| Usuario | Contraseña | Perfil | Vista inicial |
|---|---|---|---|
| `admin` | `admin123` | Encargado | Resumen / gestión |
| `celador` | `celador123` | Guarda | Portería |
| `estudiante` | `estudiante123` | Consulta | Mis préstamos |

`admin` es `Encargado`: el rol `Administrador` fue eliminado en C12 y no se reincorpora. Si necesitas otra credencial, crea una con un perfil vigente:

```powershell
py identificar.py crear 52111222 --rol Encargado
```

La contraseña se solicita por consola (o desde `PRESTATEC_ADMIN_PASSWORD` solo en automatización). Se guarda como hash PBKDF2 con salt en `identidades.json`, archivo ignorado por Git; nunca aparece en `data.json`. Los roles `Administrador` y `Soporte` fueron eliminados en C12: se rechazan al crear credenciales y una credencial heredada con esos roles deja de iniciar sesión. Los archivos existentes no se borran.

Al abrir `http://127.0.0.1:5080` sin sesión se ve una pantalla de acceso completa, no un formulario aislado. Escribe usuario y contraseña y pulsa **Ingresar**; un error se muestra dentro de la tarjeta. Cada perfil entra en su propia vista (`mis`, `porteria` o `gestion`) y solo ve su navegación:

| Acción | Consulta | Guarda | Encargado |
|---|---|---|---|
| Solicitar préstamo (solo para su documento) | Sí | No | No |
| Verificar en portería | No | Sí | Sí |
| Entregar / devolver | No | Sí | Sí |
| Crear equipo / usuario | No | No | Sí |
| Registrar daño / mantenimiento | No | No | Sí |
| Habilitar reincorporación | No | No | Sí |
| Exportar reportes | Sí | No | Sí |
| Consultar historial | Sí | No | Sí |
| Ver resumen | No | Sí | Sí |
| Ver usuarios | No | No | Sí |

Los roles históricos `Estudiante` y `Docente` se tratan como `Consulta`. La matriz es una aprobación técnica temporal; se cambia en `prestatec/identidad.py` si la universidad define otra. Para SSO institucional se sustituye el proveedor al construir `PrestaTecApp`, sin tocar las reglas de negocio.

## 5. Módulos de la interfaz por perfil

- **Consulta — Mis préstamos:** indicadores personales, búsqueda de equipos libres mediante `/api/disponibilidad`, solicitud para su propio documento (con alternativas ante conflictos) e historial de sus equipos.
- **Guarda — Portería:** validación rápida por QR o cédula, resultado con audio y registro de las últimas lecturas. También accede a Préstamos para entregar y recibir.
- **Encargado — Gestión:** resumen, inventario (alta, estado, QR e historial), préstamos (entrega, devolución, cancelación), portería y usuarios, además del reporte CSV.

La interfaz muestra estados vacíos, mensajes de éxito/error, indicación de carga, foco visible y diseño adaptable a móvil. Todas las acciones visibles tienen controlador; la navegación se filtra según el perfil devuelto por `/api/auth/me`.

## 6. Metodología solicitada

La especificación está en `openspec/` y las pruebas están en `tests/`. El orden de trabajo aplicado es:

1. **SDD / OpenSpec:** `proposal.md`, `design.md` y `spec.md` definen el problema, alcance, reglas y criterios.
2. **TDD — Red:** se escribieron primero las pruebas que describen los comportamientos esperados.
3. **TDD — Green:** se implementó `prestatec/service.py` y las rutas HTTP para satisfacerlas.
4. **TDD — Refactor:** se separaron reglas de negocio, servidor e interfaz para mantener el código organizado y sencillo.

## 7. Control de versiones

El código está publicado en **https://github.com/jostinMorenoRJ/PrestaTec.git**, rama `main`. El historial completo empieza en el commit de línea base `8a92475 chore: linea base y gobernanza (C0)` y termina en el estado marcado con la etiqueta `nucleo`. Para verlo:

```powershell
git log --oneline --decorate
git status
git show nucleo-2-red    # prueba antes del código
git show nucleo-3-green  # código que la hace pasar
```

`.gitignore` excluye el entorno virtual, las cachés, `data.json`, `identidades.json` y la base SQLite local para no versionar datos ni credenciales. Las contraseñas de demostración aparecen en este README y en el informe Word; si el repositorio va a ser público, hazlo privado o retíralas antes de compartirlo.

## 8. Alcance y mejoras futuras

El levantamiento de requisitos incluye asuntos que deben definirse con la universidad: duración máxima del préstamo, anticipación de reservas, quién aprueba/cancela, sanciones, integración con correo/sistema académico y retención histórica. La autenticación local, los permisos por rol y los respaldos verificables ya están implementados (C4 y C5); siguen pendientes SSO institucional, notificaciones automáticas y despliegue. Se dejaron documentados en `openspec/legacy/prestamos-universidad/design.md` y en `openspec/specs/requisitos-institucionales/spec.md` para no inventar políticas.
