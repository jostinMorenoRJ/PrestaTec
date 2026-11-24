# Reglas generales del proyecto PrestaTec 2.0

> Reglas originales completas, complementadas con la sección de OpenSpec y
> trazabilidad. Es el único archivo de reglas en la raíz.

## Objetivo
Modernizar el sistema universitario de préstamos de computadores portátiles y proyectores.

## Tecnologías
- Python como lenguaje principal.
- pytest para pruebas automatizadas.
- OpenSpec para especificaciones.
- Git para control de versiones.

## Metodología obligatoria
- Aplicar SDD mediante OpenSpec.
- Definir los requisitos antes de implementar.
- Aplicar TDD mediante pytest.
- Seguir RED → GREEN → REFACTOR.
- Crear las pruebas antes de desarrollar cada funcionalidad.

## Reglas de desarrollo
1. Analizar el código existente antes de modificarlo.
2. No eliminar funcionalidades sin justificación.
3. No sobrescribir ni eliminar datos existentes sin autorización.
4. No implementar funcionalidades que no estén especificadas.
5. Mantener separadas la interfaz, la lógica de negocio y la persistencia.
6. No dejar botones o componentes sin funcionalidad.
7. Ejecutar las pruebas después de cada cambio.
8. Documentar las decisiones técnicas.
9. Mantener la compatibilidad con los requisitos institucionales.
10. No afirmar que una prueba fue aprobada si no se ejecutó.

## Regla fundamental
No comenzar a programar una funcionalidad hasta que:
- Su especificación esté definida.
- Sus criterios de aceptación estén claros.
- Sus pruebas automatizadas estén creadas.

## OpenSpec y trazabilidad
- Las especificaciones viven en `openspec/specs/`.
- Cada incremento se documenta en `openspec/changes/<id>/` con `proposal.md`,
  `design.md`, `tasks.md` y el delta de spec correspondiente.
- `openspec/trazabilidad.md` relaciona requisito, spec, prueba e implementación.
- `openspec/revision-etapa4.md` registra las decisiones de revisión.
- Los documentos originales del ZIP se conservan en `openspec/legacy/`.
- Una prueba de caracterización documenta el comportamiento actual, incluso si
  es defectuoso; NO debe confundirse con un criterio de aceptación definitivo.
