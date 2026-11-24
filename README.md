# PrestaTec — sistema de préstamo de portátiles y proyectores

Aplicación web local desarrollada en Python. Permite administrar inventario,
usuarios, reservas, entregas, devoluciones, daños, historial y validación rápida
en portería. La interfaz funciona en el navegador, sin Flask, Django ni base de
datos externa.

## Ejecutar en 3 comandos

```powershell
pip install -r requirements.txt
python -m pytest
python run.py --demo
```

Abre **http://127.0.0.1:5080**. La suite queda en verde y las cuentas que
anuncia la pantalla de acceso funcionan en el primer intento.

`--demo` es **explícito y opt-in**: crea las tres credenciales y da de alta a
`estudiante` como usuario de negocio, sin sobrescribir nada. `python run.py` sin
bandera **no crea cuentas**. También puedes prepararlas sin iniciar el servidor
con `python scripts/crear_demo.py`.

> **SOLO DEMOSTRACIÓN — no usar en producción.** Estas claves son públicas y
> están aquí para que el sistema se pueda probar sin configuración previa.
> Antes de desplegar, cámbialas o retíralas del texto y de la interfaz.

| Usuario | Contraseña | Perfil | Vista inicial |
|---|---|---|---|
| `admin` | `admin123` | Encargado | Resumen / gestión |
| `celador` | `celador123` | Guarda | Portería |
| `estudiante` | `estudiante123` | Consulta | Mis préstamos |

El paso a paso para Windows y VS Code está más abajo.

## Núcleo pedido

| Lo solicitado | Dónde encontrarlo |
|---|---|
| **Especificación (SDD)** | `openspec/specs/prestamos/spec.md` (RF01–RF09) y los deltas `openspec/changes/devolucion-responsable/` (RF06a) y `openspec/changes/devolucion-unica/` (RF06b) |
| **Pruebas (pytest)** | `tests/test_prestamos.py` — registro, préstamo, devolución, disponibilidad, daño, portería y persistencia |
| **Programa Python** | `prestatec/service.py` — `InventoryService`: `registrar_equipo`, `registrar_usuario`, `crear_prestamo`, `entregar`, `devolver`, `listar_equipos` |

El núcleo proviene de una línea base previa documentada en `openspec/legacy/`,
presente desde `8a92475`; el orden SDD/TDD se aplicó formalmente desde esa base,
sin reescribir el historial. El detalle y la nota de honestidad están en
`openspec/README.md`.

## Ciclos TDD

| Ciclo | Spec | RED | GREEN | Etiqueta |
|---|---|---|---|---|
| DEV — responsable de devolución | `a76091e` | `9fc38c1` | `9695bde` | `nucleo-1-spec`, `nucleo-2-red`, `nucleo-3-green` |
| DUP — devolución única | `131d82c` | `d002ae0` | `6907506` | `devolucion-unica` |
| DEMO — acceso en el primer arranque | `54c5d08` | `89b6938` | `4ab6f17` | `demo-acceso-inicial` |

DEV y DUP son los ciclos del núcleo; DUP incluye además el REFACTOR `beadd92`.
Cada paso se puede comprobar con `git show <commit>`; los comandos concretos y
el detalle de cada fase están en `openspec/README.md`.

## Extras opcionales

Autenticación y permisos (`prestatec/identidad.py`), repositorio inyectado y
SQLite (`prestatec/repository.py`, `prestatec/migracion.py`), respaldos
verificables (`prestatec/backup.py`), perfiles e interfaz (`static/`), evidencias
en `openspec/evidencia/` y el informe Word en `documentacion/`. Cada extra tiene
su propuesta en `openspec/changes/` y se puede ignorar sin afectar al núcleo.

Los `openspec/evidencia/ejecucion-c0.md` … `ejecucion-c13.md`, los changes
C0–C13 en `openspec/changes/archive/` y `openspec/legacy/` son evidencia e
incrementos previos: no hacen falta para entender ni ejecutar lo pedido.

## Requisitos

- Python 3.10 o superior.
- Visual Studio Code (recomendable, extensión **Python** de Microsoft).
- Internet solo si se desean cargar fuentes y el generador QR desde su CDN; las
  funciones principales funcionan localmente.

## Instalación paso a paso en Windows / VS Code

1. Clona el repositorio o descarga el código; la carpeta debe contener `run.py`
   en la raíz:

   ```powershell
   git clone https://github.com/jostinMorenoRJ/PrestaTec.git
   cd PrestaTec
   ```

2. Abre VS Code y selecciona **Archivo → Abrir carpeta**, eligiendo esa carpeta.
   La configuración de `.vscode/` habilita pytest, la tarea de pruebas y dos
   configuraciones de depuración.

3. Abre una terminal (**Terminal → Nuevo terminal**) y comprueba Python:

   ```powershell
   py --version
   ```

4. Crea y activa el entorno virtual:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación, puedes ejecutar directamente con `py`,
   o usar CMD y `.venv\Scripts\activate.bat`.

5. Instala las dependencias y prepara la demostración:

   ```powershell
   py -m pip install -r requirements.txt
   py run.py --demo
   ```

6. Abre **http://127.0.0.1:5080**, ingresa con una cuenta de la tabla anterior
   y detén el servidor con **Ctrl + C** en la terminal.

## Pruebas

```powershell
py -m pytest -v
```

La suite final tiene **85 pruebas** y pasa en verde también en un clon limpio,
sin `data.json` ni `identidades.json`: **85 passed**. Es el resultado de la
línea base previa, los ciclos DEV y DUP y las cuatro pruebas del ciclo DEMO. La
salida completa está en `documentacion/evidencia-pytest-clon-limpio.txt`; el
informe histórico de C13 quedó en `documentacion/Pruebas_PrestaTec_C13.docx`.
Algunas pruebas son de caracterización: documentan el comportamiento real, no
son criterios de aceptación definitivos.

Solo los ciclos del núcleo:

```powershell
py -m pytest tests/test_prestamos.py -v
py -m pytest tests/test_demo.py -v
```

Los marcadores de `pyproject.toml` son `unit`, `integration`, `acceptance`, `nfr`
y `characterization`. En VS Code están el panel **Testing** y la tarea
**PrestaTec: ejecutar pruebas** (`Ctrl+Shift+B`).

## Datos de demostración

La primera ejecución crea `data.json` con seis equipos y cuatro usuarios:

| Tipo | Código | Nombre |
|---|---|---|
| Portátil | PT-001 | Lenovo ThinkPad E14 |
| Portátil | PT-002 | Dell Latitude 3420 |
| Portátil | PT-003 | HP ProBook 440 |
| Portátil | PT-004 | Acer Aspire 5 |
| Proyector | PR-001 | Epson X49 |
| Proyector | PR-002 | BenQ MS550 |

Documentos de ejemplo: Ana Torres `1001234567`, Brayan Ruiz `79876543`, Omar
Díaz `80123456` y Laura Gómez `52111222`. `admin`, `celador` y `estudiante`
se crean con `run.py --demo`; el último queda registrado como usuario de negocio
para poder reservar.

`data.json` e `identidades.json` están fuera de Git (`.gitignore`) a propósito:
los hashes PBKDF2 y sus salts viven en el segundo archivo, nunca en el primero,
y no se incluye ningún ZIP con copia del código. Para reiniciar, detén el
servidor, elimina `data.json` y vuelve a ejecutar `py run.py --demo`: eso borra
préstamos y usuarios de prueba sin tocar credenciales existentes.

### Persistencia opcional (SQLite)

El sistema usa `data.json` por defecto. Para migrar de forma explícita, ejecuta
la tarea **PrestaTec: migrar data.json a SQLite** en VS Code o:

```powershell
py scripts/migrar.py
```

El proceso crea `data.json.bak` con el contenido original y calcula su SHA-256;
no sobrescribe archivos existentes salvo que se pase `--forzar`. Para usar
SQLite:

```powershell
$env:PRESTATEC_BACKEND='sqlite'
$env:PRESTATEC_DATA_FILE='prestatec.db'
py run.py --demo
```

Quitar las variables restaura el comportamiento original sin tocar la lógica de
negocio.

### Respaldos

Cada copia se guarda con timestamp UTC, SHA-256 y conteo de entidades. Desde VS
Code, la tarea **PrestaTec: crear respaldo verificable**, o desde la terminal:

```powershell
py scripts/respaldar.py crear data.json --directorio backups
py scripts/respaldar.py restaurar backups\data_....manifest.json data.json --confirmar
```

`restaurar` valida hash y conteos antes y después de reemplazar el destino. Si
el destino es más reciente, exige `--confirmar`. No hay purga automática.

### Ingreso y permisos

Toda ruta `/api/...` exige sesión. Las cuentas y claves están en la sección
**Ejecutar en 3 comandos**. `admin` es `Encargado`: el rol `Administrador` fue
eliminado en C12 y no se reincorpora. Para otra credencial:

```powershell
py scripts/identificar.py crear 52111222 --rol Encargado
```

La contraseña se pide por consola (o desde `PRESTATEC_ADMIN_PASSWORD` solo en
automatización) y se guarda como hash PBKDF2 con salt en `identidades.json`.
Los roles `Administrador` y `Soporte` se rechazan al crear credenciales; los
alias históricos `Estudiante` y `Docente` se traducen a `Consulta`.

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

La matriz es una aprobación técnica temporal; se cambia en
`prestatec/identidad.py` si la universidad define otra. Para SSO institucional
se sustituye el proveedor al construir `PrestaTecApp`, sin tocar reglas de
negocio.

## Módulos de la interfaz por perfil

- **Consulta — Mis préstamos:** indicadores personales, búsqueda de equipos
  libres vía `/api/disponibilidad`, solicitud para su propio documento e
  historial.
- **Guarda — Portería:** validación por QR o cédula, resultado con audio y
  registro de lecturas; también entrega y recibe préstamos.
- **Encargado — Gestión:** resumen, inventario, préstamos, portería, usuarios y
  reporte CSV.

La interfaz muestra estados vacíos, mensajes de éxito/error, indicación de
carga, foco visible y diseño adaptable a móvil. Todas las acciones visibles
tienen controlador y la navegación se filtra según `/api/auth/me`.

## Metodología

Spec → Red → Green → Refactor se aplicó formalmente en los ciclos DEV y DUP
sobre la base previa de `openspec/legacy/`; después se añadió el ciclo DEMO para
corregir el acceso en el primer arranque. **No** se escribieron todas las
pruebas antes que todo el código. Los commits, etiquetas, evidencias y la nota
de honestidad están en `openspec/README.md`; las tareas de cada incremento, en
`openspec/changes/<change>/tasks.md` y su índice en `openspec/changes/README.md`.

## Control de versiones

Código publicado en **https://github.com/jostinMorenoRJ/PrestaTec.git**, rama
`main`. El historial empieza en `8a92475` y continúa sin reescrituras. Etiquetas
publicadas: `nucleo-1-spec`, `nucleo-2-red`, `nucleo-3-green`, `nucleo`,
`devolucion-unica`, `demo-acceso-inicial` y `entrega-final` (sobre el último
commit). Comandos para verificarlo:

```powershell
git log --oneline --decorate
git show devolucion-unica
git show demo-acceso-inicial
git status
```

`.gitignore` excluye entorno virtual, cachés, `data.json`, `identidades.json` y
la base SQLite local: no se versionan datos ni credenciales, y no hay ZIP con
copia del código. Las claves de demostración aparecen rotuladas como **solo
demostración**; antes de compartir el repo públicamente, cámbialas o retíralas.

## Alcance y mejoras futuras

Quedan por definir con la universidad la duración máxima del préstamo, la
anticipación de reservas, quién aprueba o cancela, sanciones, integración con
correo o sistema académico y retención histórica. La autenticación local, los
permisos por rol y los respaldos verificables ya están implementados; siguen
pendientes SSO institucional, notificaciones automáticas y despliegue. Está
documentado en `openspec/legacy/prestamos-universidad/design.md` y en
`openspec/specs/requisitos-institucionales/spec.md` para no inventar políticas.
