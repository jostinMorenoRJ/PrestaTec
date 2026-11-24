# Tareas: identidad y control de acceso

- [ ] Revisar y aprobar este change, especialmente la matriz de permisos.
- [ ] RED: `test_RNF01_anonimo_recibe_401` para cada ruta `/api/...`.
- [ ] RED: `test_RNF01_guarda_no_registra_usuarios` → 403.
- [ ] RED: `test_RNF01_encargado_entrega_y_devuelve` → 200 auditado.
- [ ] Ejecutar y confirmar fallos.
- [ ] GREEN: implementar `IdentityProvider`, hashing y sesiones.
- [ ] GREEN: implementar `Authorizer` y aplicarlo en API y casos de uso.
- [ ] RED: `test_RNF01_sin_secretos_en_repositorio`.
- [ ] GREEN: mover secretos a configuración de entorno.
- [ ] REFACTOR: suite completa + caracterización (actualizando la expectativa de acceso anónimo según la nueva spec).
- [ ] Commit `feat: identidad y rbac`.
