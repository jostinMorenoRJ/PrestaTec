"""Utilidades de prueba para autenticar peticiones contra `PrestaTecApp`.

C12: el perfil por defecto es `Encargado` (gestión). Las pruebas que solicitan
préstamos deben pedir explícitamente una credencial `Consulta` con el documento
del usuario de negocio (PER-03).
"""
import json


def autenticar(app, documento='gestor-tests', contraseña='clave-tests', rol='Encargado'):
    """Crea una credencial y devuelve cabeceras con una sesión válida."""
    app.identidad.crear_credencial(documento, contraseña, rol)
    estado, contenido, _mime, _nombre = app.dispatch(
        'POST', '/api/auth/login', {'documento': documento, 'contraseña': contraseña}
    )
    assert estado == 200, contenido
    return {'Cookie': f'prestatec_session={json.loads(contenido)["token"]}'}
