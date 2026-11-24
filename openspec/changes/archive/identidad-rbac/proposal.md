# Propuesta: identidad y control de acceso (C5)

## Problema
Hoy cualquier persona puede listar usuarios, consultar documentos y exportar CSV.
Los roles se guardan pero nunca se comprueban. Esto incumple PDF-RNF01, RES-02 y
el requisito institucional 5.4.2.

## Qué cambia
- Proveedor de identidad con cuentas internas y contraseñas con hash seguro.
- RBAC comprobado en la lógica de negocio y en la API (401/403), no solo en botones.
- Roles: Guarda, Encargado, Soporte, Administrador, Consulta.
- Adaptador de identidad desacoplado para permitir SSO futuro sin tocar el dominio.

## Fuera de alcance
SSO institucional, integración académica y credenciales reales en el repositorio
(DEC-05, DEC-07, O5).

## Capacidades afectadas
- seguridad (nueva)
- requisitos-institucionales (PDF-RNF01, RES-02)

## Impacto esperado
Cierra la brecha crítica de seguridad y evita reescribir endpoints después, al
introducir permisos antes de las funcionalidades visibles (C7–C10).
