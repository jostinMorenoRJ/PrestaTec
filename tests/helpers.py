"""Utilidades de prueba para autenticar peticiones contra `PrestaTecApp`."""
import json


def autenticar(app, documento='admin-tests', contraseña='clave-tests'):
    """Crea una credencial de administrador y devuelve cabeceras con sesión."""
    app.identidad.crear_credencial(documento, contraseña, 'Administrador')
    estado, contenido, _mime, _nombre = app.dispatch(
        'POST', '/api/auth/login', {'documento': documento, 'contraseña': contraseña}
    )
    assert estado == 200, contenido
    return {'Cookie': f'prestatec_session={json.loads(contenido)["token"]}'}
