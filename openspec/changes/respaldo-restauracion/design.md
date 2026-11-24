# Diseño: respaldo y restauración verificable

## Enfoque
El respaldo es una operación explícita del repositorio, no una copia oportunista
del archivo. Cada copia queda registrada con timestamp UTC, hash SHA-256 y conteo
de entidades para poder demostrar que la restauración fue exacta.

## Decisiones técnicas
- Formato de copia: snapshot SQLite consistente (o JSON normalizado si el flag sigue en `json`).
- La ruta de destino se configura por entorno; nunca una ruta productiva hardcoded.
- Restauración en transacción: se valida la copia antes de reemplazar el estado activo.
- Retención por defecto: `sin purga` mientras DEC-06 no defina cuánto conservar.

## Riesgos y mitigación
- Riesgo: copia corrupta que parezca válida. Mitigación: verificar hash y conteos antes y después.
- Riesgo: restaurar sobre datos más recientes. Mitigación: comparar timestamp y exigir confirmación explícita.

## Compatibilidad
No altera el esquema de C3. No elimina copias antiguas.
