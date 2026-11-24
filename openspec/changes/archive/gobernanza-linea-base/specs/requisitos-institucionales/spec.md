# Delta: gobernanza y línea base

## MODIFIED Requirements

### INT-07 - Git y documentación técnica
El repositorio DEBE estar inicializado antes de cualquier cambio funcional.
Cada commit DEBE ser descriptivo y DEBE registrar la decisión técnica asociada.

#### Escenario: repositorio listo antes de tocar lógica
- DADO el workspace con el código original
- CUANDO se inicia el cambio C0
- ENTONCES existe `.git`, `pyproject.toml`, `AGENTS.md` y la estructura OpenSpec completa

## ADDED Requirements

### GOV-01 - Entorno reproducible
La configuración de pytest DEBE estar centralizada y las dependencias de prueba
DECLARADAS, sin depender de instalaciones globales.

#### Escenario: ejecución de pruebas desde cero
- DADO un entorno virtual nuevo
- CUANDO se instalan dependencias y se ejecuta `pytest`
- ENTONCES se ejecutan todas las pruebas con los marcadores definidos

### GOV-02 - Caracterización previa
ANTES de modificar comportamiento, DEBEN existir pruebas que documenten el
estado actual, incluidos sus defectos conocidos.

#### Escenario: conflicto actual documentado
- DADO dos reservas solapadas
- CUANDO se ejecuta la prueba de caracterización
- ENTONCES se registra que hoy se responde `400` y no `409`

### GOV-03 - Datos de prueba aislados
Las pruebas NO DEBEN modificar `data.json` real ni datos institucionales.

#### Escenario: aislamiento
- DADO cualquier prueba del proyecto
- CUANDO se ejecuta
- ENTONCES usa `tmp_path` o base de datos en memoria
