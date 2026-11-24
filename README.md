# PrestaTec — sistema de préstamo de portátiles y proyectores

Aplicación web local desarrollada en Python. Permite administrar inventario, usuarios, reservas, entregas, devoluciones, daños, historial y validación rápida en portería. La interfaz está diseñada como un panel tipo landing page y funciona en el navegador.

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

La suite tiene **19 pruebas**: 12 originales (dominio y HTTP) y 7 de caracterización en `tests/characterization/`, que documentan el comportamiento actual, incluidos defectos conocidos. En VS Code también puedes usar el panel **Testing** o la tarea **PrestaTec: ejecutar pruebas** (`Ctrl+Shift+B`).

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

Para reiniciar la demostración, detén el servidor, elimina `data.json` y vuelve a ejecutar `py run.py`. Esto elimina también los registros creados durante la prueba.

## 5. Módulos de la interfaz

- **Resumen:** indicadores de inventario, atrasos y próximas reservas.
- **Inventario:** registrar equipos, cambiar su estado, imprimir etiqueta QR y consultar historial.
- **Préstamos:** reservar por fecha/hora, registrar entrega, devolución, cancelación o no presentación.
- **Portería:** verificar un código de equipo o documento de estudiante. También se puede usar un lector QR que escriba el código como teclado.
- **Usuarios:** registrar estudiantes, docentes y personal.
- **Reporte:** descargar el historial de préstamos en CSV.

## 6. Metodología solicitada

La especificación está en `openspec/` y las pruebas están en `tests/`. El orden de trabajo aplicado es:

1. **SDD / OpenSpec:** `proposal.md`, `design.md` y `spec.md` definen el problema, alcance, reglas y criterios.
2. **TDD — Red:** se escribieron primero las pruebas que describen los comportamientos esperados.
3. **TDD — Green:** se implementó `prestatec/service.py` y las rutas HTTP para satisfacerlas.
4. **TDD — Refactor:** se separaron reglas de negocio, servidor e interfaz para mantener el código organizado y sencillo.

## 7. Control de versiones

El repositorio Git **ya está inicializado** en esta carpeta y contiene el commit de línea base `8a92475 chore: linea base y gobernanza (C0)`. Para ver el historial:

```powershell
git log --oneline
git status
```

**No se ha publicado en GitHub**: no existe repositorio remoto ni autorización para publicar. Cuando se decida, se requiere definir el dueño del repositorio, la visibilidad y la política de datos antes de configurar `origin`.

`.gitignore` excluye el entorno virtual, las cachés y `data.json` para no versionar datos de prueba.

## 8. Alcance y mejoras futuras

El levantamiento de requisitos incluye asuntos que deben definirse con la universidad: duración máxima del préstamo, anticipación de reservas, quién aprueba/cancela, sanciones, integración con correo/sistema académico y retención histórica. La autenticación real, permisos por rol, notificaciones automáticas, respaldos y despliegue institucional también requieren una siguiente iteración. Se dejaron documentados en `openspec/legacy/prestamos-universidad/design.md` y en `openspec/specs/requisitos-institucionales/spec.md` para no inventar políticas.
