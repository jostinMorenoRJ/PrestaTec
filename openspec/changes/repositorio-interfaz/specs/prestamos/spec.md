# Delta: repositorio e inversión de dependencias

## ADDED Requirements

### ARQ-01 - Acceso a datos detrás de una interfaz
La lógica de negocio NO DEBE acceder directamente a archivos, consultas ni
detalles de persistencia. DEBE hacerlo mediante un repositorio inyectado.

#### Escenario: servicio con repositorio falso
- DADO un repositorio en memoria de prueba
- CUANDO se crea el servicio con ese repositorio
- ENTONCES el servicio registra y consulta sin saber que existe `data.json`

### ARQ-02 - Formato actual conservado
Durante este change, el adaptador por defecto DEBE seguir leyendo y escribiendo
`data.json` con la estructura actual, incluida la compatibilidad PascalCase.

#### Escenario: legado preservado
- DADO un `data.json` con claves `Equipos` y `Reservas`
- CUANDO se inicializa el servicio
- ENTONCES los datos se exponen con claves en minúscula sin pérdida
