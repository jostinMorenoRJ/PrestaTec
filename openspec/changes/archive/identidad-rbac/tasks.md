# Tareas: identidad y control de acceso

- [x] Revisar y aprobar este change, especialmente la matriz de permisos. El
      usuario aprobó la matriz propuesta con `Estudiante`/`Docente` → `Consulta`
      como decisión técnica temporal (2026-11-24).
- [x] RED: `tests/test_seguridad.py` creado antes de `prestatec/identidad.py`;
      fallo por `ModuleNotFoundError: prestatec.identidad`.
- [x] RED: `test_RNF01_guarda_no_registra_usuarios` → 403.
- [x] RED: `test_RNF01_encargado_entrega_y_devuelve` → 200 auditado.
- [x] Ejecutar y confirmar fallos.
- [x] GREEN: implementar `IdentityProvider` local, PBKDF2, sesiones firmadas y
      separación de credenciales de `data.json`.
- [x] GREEN: implementar `Autorizador` y aplicarlo en API y casos de uso.
- [x] RED: `test_RNF01_sin_secretos_en_repositorio` y CLI de alta de credenciales.
- [x] GREEN: mover secretos a configuración de entorno; `identificar.py` pide la
      contraseña por consola y rechaza sobrescribir credenciales.
- [x] RED/GREEN: `/api/auth/me` expone identidad y permisos para la interfaz.
- [x] RED/GREEN: `run.py` propaga `Cookie`/`Set-Cookie` en HTTP real.
- [x] REFACTOR: actualizar `test_web.py`, `test_configuracion.py` y
      caracterización para autenticar; el acceso anónimo ahora es 401 por spec.
- [x] REFACTOR: interfaz con inicio/cierre de sesión y ocultación de acciones
      según permisos; verificado en navegador con roles `Administrador` y `Guarda`.
- [x] REFACTOR: suite completa **57 passed in 4.34s**.
- [x] Registrar evidencia en `openspec/evidencia/ejecucion-c5.md`.
- [x] Commit `feat: identidad y control de acceso (C5)` (ver `git log`).
