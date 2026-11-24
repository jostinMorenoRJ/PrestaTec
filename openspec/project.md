# PrestaTec 2.0

## Propósito

Modernizar el sistema universitario de préstamo de computadores portátiles y
proyectores, conservando lo que funciona del programa actual y cerrando las
brechas de seguridad, persistencia, trazabilidad y experiencia de usuario
detectadas en la auditoría.

Python sigue siendo el lenguaje principal y el encargado de la lógica de
negocio. Las tecnologías complementarias se justifican en el diseño de cada
cambio.

## Stakeholders

- Estudiantes y docentes.
- Encargado de préstamos / biblioteca.
- Administrador de inventario y recursos tecnológicos.
- Coordinación académica / administración.
- Personal de soporte técnico.
- Guardas de seguridad (portería).

## Alcance obligatorio

Las seis funcionalidades del alcance mínimo y los requisitos no funcionales
RNF01-RNF04 del taller, más las restricciones 5.4, las excepciones 5.5 y las
reglas internas de `AGENTS.md.txt`. El detalle está en
`openspec/specs/requisitos-institucionales/spec.md`.

## Fuera de alcance hasta nueva decisión

- Sanciones automáticas, plazos máximos, anticipación de reservas, aprobación
  de reservas y retención numérica (taller §8.1-§8.4, §8.6).
- Integración con correo institucional o sistemas académicos (§8.5).
- SSO, PostgreSQL y despliegue central mientras no se defina infraestructura.
- Publicación en GitHub sin permisos verificados.

## Principios de trabajo

1. SDD: especificar antes de programar.
2. TDD: RED → GREEN → REFACTOR con pytest para cada funcionalidad.
3. No eliminar funcionalidades que funcionen sin justificación técnica.
4. No borrar ni sobrescribir datos sin autorización y respaldo verificable.
5. Separar interfaz, lógica de negocio y persistencia.
6. No dejar botones ni módulos sin funcionalidad real.
7. Documentar cada decisión técnica y no afirmar pruebas no ejecutadas.

## Línea base verificada

- 18 archivos en el ZIP original; 12 pruebas pytest pasan.
- Servidor local `127.0.0.1:5080`, almacenamiento `data.json`.
- Contrato actual: conflicto devuelve `400`, no `409`; disponibilidad solo en API.
- Brechas críticas: sin autenticación (RNF01) y sin respaldo (RNF04).

## Glosario

- **Equipo**: portátil o proyector con código único `PT-###` / `PR-###`.
- **Préstamo**: operación con reserva, entrega, devolución y estados.
- **Disponibilidad**: equipo libre en un intervalo y no en mantenimiento.
- **Change**: incremento pequeño documentado en `openspec/changes/`.
- **Delta**: modificación de una spec existente dentro de un change.
