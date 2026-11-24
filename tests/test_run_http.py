"""SEC-01: la cookie de sesión debe viajar en el servidor HTTP real."""
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from prestatec.web import PrestaTecApp


def _cabecera(headers, nombre):
    return next((valor for clave, valor in headers.items() if clave.lower() == nombre.lower()), None)


def _peticion(base, ruta, metodo='GET', cuerpo=None, cookie=None):
    datos = json.dumps(cuerpo).encode('utf-8') if cuerpo is not None else None
    cabeceras = {'Content-Type': 'application/json'}
    if cookie:
        cabeceras['Cookie'] = cookie
    peticion = urllib.request.Request(
        base + ruta, data=datos, method=metodo, headers=cabeceras
    )
    try:
        with urllib.request.urlopen(peticion, timeout=5) as respuesta:
            return respuesta.status, respuesta.read(), dict(respuesta.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)


def test_servidor_envia_cookie_y_acepta_sesion(tmp_path):
    from run import crear_handler

    app = PrestaTecApp(
        tmp_path / 'db.json', seed=False,
        identidad_file=tmp_path / 'identidades.json',
    )
    app.identidad.crear_credencial('admin', 'clave', 'Administrador')
    servidor = ThreadingHTTPServer(('127.0.0.1', 0), crear_handler(app))
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    base = f'http://127.0.0.1:{servidor.server_port}'
    try:
        estado, _cuerpo, headers = _peticion(
            base, '/api/auth/login', 'POST',
            {'documento': 'admin', 'contraseña': 'clave'},
        )
        assert estado == 200
        cookie = _cabecera(headers, 'Set-Cookie')
        assert cookie and 'HttpOnly' in cookie and 'SameSite=Lax' in cookie
        token = cookie.split(';', 1)[0].split('=', 1)[1]

        assert _peticion(base, '/api/equipos')[0] == 401
        assert _peticion(
            base, '/api/equipos', cookie=f'prestatec_session={token}'
        )[0] == 200
    finally:
        servidor.shutdown()
        servidor.server_close()
        hilo.join(timeout=5)
