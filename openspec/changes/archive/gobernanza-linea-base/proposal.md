# Propuesta: gobernanza y línea base (C0)

## Problema
El proyecto original no tiene repositorio Git, configuración de pytest centralizada
ni artefactos OpenSpec completos. Sin esto, cualquier refactor posterior es
irreversible y no hay forma de demostrar qué comportamiento se conservó.

## Qué cambia
- Inicializar Git y dejar commits descriptivos.
- Crear `pyproject.toml` con configuración de pytest y marcadores.
- Normalizar `AGENTS.md` (el original tiene extensión `.txt`).
- Añadir pruebas de caracterización del comportamiento actual antes de modificarlo.
- Completar la estructura OpenSpec base ya creada en esta Etapa 3.

## Fuera de alcance
Cualquier cambio de lógica de negocio, interfaz o almacenamiento.

## Capacidades afectadas
- requisitos-institucionales
- prestamos (solo como línea base de caracterización)

## Impacto esperado
Permite iniciar TDD con una red de seguridad: si un cambio posterior altera el
comportamiento actual no previsto en una spec, la prueba de caracterización lo detecta.
