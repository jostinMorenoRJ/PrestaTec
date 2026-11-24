"""Preparación explícita de la demostración (DEMO-01..DEMO-04).

Este módulo nunca se ejecuta solo: la preparación la pide quien invoca
``run.py --demo`` o ``crear_demo.py``. No sobrescribe credenciales ni usuarios
que ya existan.
"""
from .identidad import AlmacenCredenciales
from .service import InventoryService

# Las mismas cuentas que anuncia la pantalla de acceso.
CUENTAS_DEMO = (
    ('admin', 'admin123', 'Encargado'),
    ('celador', 'celador123', 'Guarda'),
    ('estudiante', 'estudiante123', 'Consulta'),
)
USUARIO_NEGOCIO = ('Estudiante Demo', 'estudiante', 'Estudiante')


def preparar_demo(servicio=None, almacen=None):
    """Crea solo lo que falta y devuelve un informe de lo creado.

    Se reciben el servicio y el almacén ya construidos por la aplicación para
    que el usuario de negocio quede visible en la misma instancia que atiende
    las peticiones HTTP.
    """
    servicio = servicio if servicio is not None else InventoryService()
    almacen = almacen if almacen is not None else AlmacenCredenciales()

    credenciales_creadas = []
    for documento, clave, rol in CUENTAS_DEMO:
        if almacen.rol(documento) is None:
            almacen.crear(documento, clave, rol)
            credenciales_creadas.append(documento)

    usuarios_creados = []
    nombre, documento, rol = USUARIO_NEGOCIO
    if not any(u['documento'] == documento for u in servicio.listar_usuarios()):
        servicio.registrar_usuario(nombre, documento, rol)
        usuarios_creados.append(documento)

    return {'credenciales': credenciales_creadas, 'usuarios': usuarios_creados}
