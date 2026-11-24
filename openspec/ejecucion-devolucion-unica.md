# Ejecución del segundo ciclo — devolución única (DUP-01..03)

**Fecha:** 24 de noviembre de 2026
**Commit de spec:** `131d82c`
**Commit RED:** `d002ae0`
**Commit GREEN:** `6907506` — etiqueta `devolucion-unica`
**Commit REFACTOR:** `beadd92`
**Prueba de clarificación:** `513209a`

## Origen

Regla del enunciado: *devolver equipos prestados*. La spec base ya impedía una
segunda devolución, pero con un mensaje que no distinguía ese caso de otros
estados inválidos. Se especificó `RF06b` en
`openspec/changes/devolucion-unica/specs/prestamos/spec.md` sin inventar
políticas de plazos ni sanciones.

## 1. Spec

`proposal.md`, `design.md`, `tasks.md` y el delta de spec se crearon en el
commit `131d82c`, sin tocar código ni pruebas.

## 2. RED

Nueva prueba en `tests/test_prestamos.py`:
`test_DUP01_no_se_puede_devolver_dos_veces_sin_modificar_el_prestamo`.

```powershell
$env:PYTHONPATH='C:\Users\spect\AppData\Local\Temp\opencode\pytest-libs'
python -m pytest tests/test_prestamos.py -q
python -m pytest -q
```

Resultado:

```
tests/test_prestamos.py: 1 failed, 11 passed in 0.23s
suite completa:          1 failed, 79 passed in 7.73s
```

Fallo exacto: se esperaba el mensaje "ya fue devuelto" y llegó
"Esta reserva no tiene un equipo entregado.".

## 3. GREEN

Cambio mínimo en `InventoryService.devolver()`: comprobar el estado `Devuelta`
antes de cualquier mutación y lanzar `BusinessError('El préstamo ya fue
devuelto.')`. Los demás estados conservan el mensaje anterior.

```
tests/test_prestamos.py: 12 passed in 0.21s
suite completa:          80 passed in 7.57s
```

## 4. REFACTOR (cuarto paso)

`beadd92` divide `listar_equipos`: un bucle legible y el ayudante
`_usuario_de_prestamo` sustituyen las dos líneas largas. Mismo contrato y mismos
campos (`estado`, `poseedor`, `devolucion`); la suite sigue en **80 passed**.
Sin este commit el método solo tenía Spec, Red y Green.

Después se añadió `513209a`
(`test_listar_equipos_separa_disponibles_y_prestados`) para nombrar
explícitamente uno de los cuatro pedidos del enunciado. **No es un RED**: la
función ya existía. El primer intento comparó `devolucion` contra el `datetime`
original y falló porque `crear_prestamo` normaliza a UTC ISO; se corrigió a
`prestamo['fin']` antes de publicar. Suite final: **81 passed**.

## 5. Diferencia con el ciclo 1

Este ciclo nace después de `ca6aa0c`, la corrección que hace que
`test_ACC01...` cree credenciales en `tmp_path`. Por sus números son válidos
también en un clon limpio, sin `identidades.json` ni `data.json`. La salida
completa de `pytest -v` en clon limpio está en
`documentacion/evidencia-pytest-clon-limpio.txt`.

## 6. Cómo mostrarlo

```powershell
git show 131d82c -- openspec/changes/devolucion-unica
git show d002ae0 -- tests/test_prestamos.py
git show 6907506 -- prestatec/service.py
git show beadd92 -- prestatec/service.py
git log --oneline --decorate -6
```
