# Diseño: endurecimiento y despliegue

## Enfoque
Este change es un conjunto de medidas de defensa en profundidad, agrupadas porque
comparten la configuración de entorno. No introduce un framework nuevo salvo que
la decisión DEC-07 lo justifique.

## Decisiones técnicas
- `.env.example` con variables documentadas; valores reales nunca versionados.
- CSRF: token por sesión en formularios y cabecera para peticiones mutantes.
- Errores: mensajes genéricos al cliente, detalle solo en logs del servidor.
- Separación clara entre `development` y `institutional` mediante perfil de configuración.

## Riesgos y mitigación
- Riesgo: cambiar el modelo de sesión y romper C5. Mitigación: reutilizar el adaptador de C5 y pruebas de regresión de roles.

## Compatibilidad
La ejecución local sigue funcionando con valores por defecto seguros de desarrollo.
