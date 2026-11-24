# Índice de OpenSpec

Para revisar **solo lo pedido**, en este orden:

1. `specs/prestamos/spec.md` — requisitos RF01–RF09 del núcleo.
2. `changes/devolucion-responsable/` — ciclo 1 (DEV): spec → test → código.
3. `changes/devolucion-unica/` — ciclo 2 (DUP): spec → test → código → refactor.
4. `changes/demo-acceso-inicial/` — ciclo 3 (DEMO): acceso usable en el primer
   arranque.

Los deltas (`specs/` dentro de cada change) y sus `tasks.md` tienen las casillas
`[x]` de lo completado. Los dos changes del núcleo están en la raíz de
`changes/`; los incrementos terminados C0–C5, C12 y C13 están en
`changes/archive/`.

## Cómo comprobar los ciclos commit por commit

```powershell
# DEV
git show a76091e -- openspec/changes/devolucion-responsable
git show 9fc38c1 -- tests/test_prestamos.py
git show 9695bde -- prestatec/service.py

# DUP
git show 131d82c -- openspec/changes/devolucion-unica
git show d002ae0 -- tests/test_prestamos.py
git show 6907506 -- prestatec/service.py
git show beadd92 -- prestatec/service.py

# DEMO
git show 54c5d08 -- openspec/changes/demo-acceso-inicial
git show 89b6938 -- tests/test_demo.py
git show 4ab6f17 -- prestatec/demo.py run.py
```

Los pasos RED y GREEN están comprobados tal como se ejecutaron; cada detalle,
incluidos los conteos de la fase en que se registraron, está en:

- `evidencia/ejecucion-nucleo-dev.md`
- `evidencia/ejecucion-devolucion-unica.md`
- `evidencia/ejecucion-demo.md`

## Nota de honestidad

`service.py` y `test_prestamos.py` ya existían en la línea base `8a92475`,
documentada en `legacy/`: **no** se escribieron todas las pruebas antes que todo
el código. SDD/TDD se aplicó formalmente en los tres ciclos anteriores a partir
de esa base, sin reescribir historial.

Los commits del ciclo 1 se ejecutaron con un `identidades.json` local. En un
clon limpio de esos commits, `test_ACC01...` fallaba por depender de ese archivo
ignorado; se corrigió en `ca6aa0c`. Por eso la evidencia RED/GREEN del ciclo 1 se
mide sobre `tests/test_prestamos.py`, no sobre la suite completa. El ciclo 2 nace
después de la corrección y el ciclo 3 usa `tmp_path` desde el principio.

## Se puede ignorar

- `evidencia/ejecucion-c0.md` … `ejecucion-c13.md`: evidencia de incrementos
  anteriores; `ejecucion-nucleo-dev.md`, `ejecucion-devolucion-unica.md` y
  `ejecucion-demo.md` sí son la evidencia de los tres ciclos.
- `evidencia/revision-etapa4.md` y `evidencia/trazabilidad.md`: decisiones de
  revisión y relación requisito → spec → prueba → implementación.
- `changes/archive/` y su índice en `changes/README.md`: extras opcionales
  (autenticación, SQLite, respaldos, perfiles, acceso local).
- `legacy/`: documentación original del proyecto previo.

La tabla única del estado final de la suite está en el README principal.
