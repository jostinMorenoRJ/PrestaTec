# EjecuciÃ³n del tercer ciclo â€” acceso usable en el primer arranque

**Fecha:** 24 de noviembre de 2026
**Commit de spec:** `54c5d08`
**Commit RED:** `89b6938`
**Commit GREEN:** `4ab6f17` â€” etiqueta `demo-acceso-inicial`

## Problema verificado

En un clon limpio, `python run.py` mostraba `admin` / `admin123` en la
pantalla de acceso, pero el login devolvÃ­a `401 Credenciales invÃ¡lidas.`:
`identidades.json` estÃ¡ fuera de Git y `estudiante` no existÃ­a como usuario de
negocio. Las cuentas solo se podÃ­an crear con un comando explicado mÃ¡s abajo en
el README, asÃ­ que el primer intento del evaluador fallaba.

## 1. Spec

`openspec/changes/demo-acceso-inicial/` con `proposal.md`, `design.md`,
`tasks.md` y el delta `specs/acceso/spec.md` (DEMO-01..04). Sin tocar cÃ³digo ni
pruebas. La preparaciÃ³n es **opt-in**: no se crean cuentas con claves conocidas
de forma automÃ¡tica y silenciosa.

## 2. RED

`tests/test_demo.py`, cuatro pruebas antes de crear `prestatec.demo`:

- `test_DEMO01_crea_las_tres_cuentas_visibles_en_pantalla`
- `test_DEMO02_estudiante_existe_como_usuario_de_negocio`
- `test_DEMO03_no_sobrescribe_credenciales_ni_usuarios_existentes`
- `test_DEMO04_login_funciona_en_la_misma_app_que_sirve_la_ui`

```powershell
$env:PYTHONPATH='C:\Users\spect\AppData\Local\Temp\opencode\pytest-libs'
python -m pytest tests/test_demo.py -q
python -m pytest -q
```

Resultado: `4 failed in 0.26s` y `4 failed, 81 passed in 7.78s`.
Causa: `ModuleNotFoundError: No module named 'prestatec.demo'`.

## 3. GREEN

- `prestatec/demo.py`: `preparar_demo(servicio, almacen)` crea solo lo que
  falta, usando los objetos ya construidos por la app.
- `scripts/crear_demo.py`: CLI dedicada, sin iniciar el servidor.
- `run.py --demo`: prepara y luego sirve. `python run.py` sin bandera **no crea
  nada**.

```powershell
tests/test_demo.py: 4 passed in 1.40s
suite completa:      85 passed in 8.81s
```

VerificaciÃ³n adicional del flujo real: con `run.py --demo` sobre archivos
temporales se crearon las tres credenciales y el usuario `estudiante`; luego un
`POST /api/auth/login` HTTP real con `admin` / `admin123` devolviÃ³ **200** y un
token. (Un primer intento con PowerShell devolviÃ³ 401 por codificar mal la `Ã±`
de `contraseÃ±a`; repetido con Python y UTF-8 explÃ­cito, 200.)

## 4. CÃ³mo mostrarlo

```powershell
git show 54c5d08 -- openspec/changes/demo-acceso-inicial
git show 89b6938 -- tests/test_demo.py
git show 4ab6f17 -- prestatec/demo.py run.py crear_demo.py
git log --oneline --decorate -4
```
