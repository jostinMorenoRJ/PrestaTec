# Ejecución del núcleo — Spec → Test → Código (DEV-01..04)

**Fecha:** 24 de noviembre de 2026
**Commit de spec:** `a76091e` — etiqueta `nucleo-1-spec`
**Commit RED:** `9fc38c1` — etiqueta `nucleo-2-red`
**Commit GREEN:** `9695bde` — etiqueta `nucleo-3-green`
**Commit de documentación:** `docs:` (se registra en `git log`)
**Etiqueta general:** `nucleo`

## Por qué este ciclo

El núcleo original (RF01–RF09) se documentó en la Etapa 1 con pruebas de
caracterización, antes de que existiera la regla obligatoria de TDD en
`AGENTS.md`. Para que un revisor pueda comprobar el orden exigido sin
interpretaciones, se eligió una brecha ya documentada en la spec base —RF06:
"falta responsable de devolución"— y se ejecutó un ciclo completo y nuevo con
tres commits separados. No se inventó ninguna política institucional.

## 1. Spec (primero)

Se creó `openspec/changes/devolucion-responsable/` con `proposal.md`,
`design.md`, `tasks.md` y el delta `specs/prestamos/spec.md` (RF06a, escenarios
DEV-01..DEV-04). **No se tocó ningún archivo de código ni de pruebas** en este
commit.

## 2. Test (después de la spec, antes del código)

Se añadieron dos pruebas a `tests/test_prestamos.py`:

- `test_DEV01_devolver_registra_responsable_explicito`
- `test_DEV02_devolver_toma_el_responsable_de_la_sesion`

Comando:

```powershell
$env:PYTHONPATH='C:\Users\spect\AppData\Local\Temp\opencode\pytest-libs'
python -m pytest tests/test_prestamos.py -q
python -m pytest -q
```

Resultado RED:

```
tests/test_prestamos.py: 2 failed, 9 passed in 0.39s
suite completa:          2 failed, 77 passed in 7.21s
```

Causas exactas:

- DEV-01: `TypeError: InventoryService.devolver() got an unexpected keyword
  argument 'responsable_devolucion'`.
- DEV-02: `KeyError: 'responsableDevolucion'`.

Las 77 pruebas preexistentes siguieron en verde: el fallo es exclusivamente
de las dos pruebas nuevas.

## 3. Código (al final)

Único cambio en `prestatec/service.py`: `devolver()` acepta
`responsable_devolucion=None`, lo prioriza sobre el nombre del actor y guarda
`responsableDevolucion`; el historial añade `Recibido por <nombre>.`. Sin
responsable ni actor el campo queda vacío, por compatibilidad. No hizo falta
tocar `web.py`: el endpoint ya devuelve el préstamo completo.

Resultado GREEN:

```
tests/test_prestamos.py: 11 passed in 0.21s
suite completa:          79 passed in 7.14s
```

## 4. Cómo mostrarlo en dos comandos

```powershell
git show 9fc38c1 -- tests/test_prestamos.py   # prueba, sin implementación
git show 9695bde -- prestatec/service.py      # implementación mínima
git log --oneline --decorate -4               # orden Spec → Test → Código
```

## 5. Decisiones

- RF06 pasa de "parcial" a cubierta en este delta; no se reclamó RF07 (tipo de
  falla y ticket), que sigue pendiente.
- No se exigió responsable de forma obligatoria: eso sería una política nueva
  y DEC-01..DEC-09 no la definen.
- Compatibilidad conservada: las nueve pruebas originales de `test_prestamos.py`
  y las 77 del resto de la suite no se modificaron para lograr GREEN.
- Árbol limpio y publicado en `https://github.com/jostinMorenoRJ/PrestaTec.git`.

## 6. Aclaración posterior sobre el clon limpio

Los tres commits de este ciclo se ejecutaron con `identidades.json` presente en
el directorio de trabajo. En un clon limpio de esos commits,
`test_ACC01_cuentas_reales_inician_sesion_con_su_perfil` fallaba porque leía ese
archivo, que está en `.gitignore`: la suite daba 1 fallo adicional. La prueba se
corrigió en `ca6aa0c` para crear sus credenciales en `tmp_path`.

Por eso la evidencia de este ciclo se mide sobre `tests/test_prestamos.py`, que
no depende de archivos ignorados y da los mismos números en local y en clon
limpio: RED `2 failed, 9 passed`, GREEN `11 passed`. No se reescribió el
historial: las etiquetas `nucleo-1-spec`, `nucleo-2-red` y `nucleo-3-green`
siguen apuntando a los commits originales. La suite completa en el HEAD actual
es `80 passed`, verificada en clon limpio.
