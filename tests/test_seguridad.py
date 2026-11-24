"""C5 — identidad y RBAC (SEC-01..SEC-04).

TDD: creado antes de `prestatec/identidad.py` y de anyadir autenticación al
enrutador. Su fallo documenta la fase RED.
"""
import json

from prestatec.identidad import Identidad, ProveedorIdentidad
from prestatec.web import PrestaTecApp


def crear_app(tmp_path):
    return PrestaTecApp(
        tmp_path / 'db.json', seed=False,
        identidad_file=tmp_path / 'identidades.json',
    )


def crear_credencial(app, documento, contraseña, rol=None):
    app.identidad.crear_credencial(documento, contraseña, rol)


def login(app, documento, contraseña):
    estado, contenido, mime, _ = app.dispatch(
        'POST', '/api/auth/login',
        {'documento': documento, 'contraseña': contraseña},
    )
    assert estado == 200, contenido
    return json.loads(contenido)['token']


def cabeceras(token):
    return {'Cookie': f'prestatec_session={token}'}


def llamar(app, metodo, ruta, cuerpo=None, headers=None):
    estado, contenido, mime, _ = app.dispatch(metodo, ruta, cuerpo, headers)
    return estado, json.loads(contenido) if mime.startswith('application/json') else contenido


def test_RNF01_anonimo_recibe_401_y_no_revela_datos(tmp_path):
    app = crear_app(tmp_path)
    app.service.registrar_usuario('Ana Torres', '1001', 'Estudiante')

    for ruta in ('/api/usuarios', '/api/equipos', '/api/resumen', '/api/reportes/csv'):
        estado, contenido = llamar(app, 'GET', ruta)
        assert estado == 401
        texto = contenido.decode('utf-8', errors='ignore') if isinstance(contenido, bytes) else str(contenido)
        assert '1001' not in texto


def test_RNF01_guarda_no_registra_usuarios(tmp_path):
    app = crear_app(tmp_path)
    crear_credencial(app, 'guarda1', 'clave', 'Guarda')
    headers = cabeceras(login(app, 'guarda1', 'clave'))

    estado, cuerpo = llamar(app, 'POST', '/api/usuarios', {
        'nombre': 'Daniel Rojas', 'documento': '12345', 'rol': 'Estudiante',
    }, headers)

    assert estado == 403
    assert 'permiso' in str(cuerpo).lower()
    assert app.service.listar_usuarios() == []


def test_RNF01_encargado_entrega_y_devuelve_asociado_a_identidad(tmp_path):
    app = crear_app(tmp_path)
    crear_credencial(app, 'admin', 'clave-admin', 'Administrador')
    admin = cabeceras(login(app, 'admin', 'clave-admin'))

    llamar(app, 'POST', '/api/usuarios', {
        'nombre': 'Laura Gómez', 'documento': '1002', 'rol': 'Encargado',
    }, admin)
    equipo = llamar(app, 'POST', '/api/equipos', {
        'tipo': 'Portátil', 'nombre': 'ThinkPad', 'ubicacion': 'Biblioteca',
    }, admin)[1]
    from datetime import datetime, timedelta
    inicio = (datetime.now() - timedelta(minutes=1)).isoformat()
    fin = (datetime.now() + timedelta(hours=1)).isoformat()
    reserva = llamar(app, 'POST', '/api/reservas', {
        'equipoId': equipo['id'], 'documento': '1002', 'inicio': inicio, 'fin': fin,
    }, admin)[1]

    crear_credencial(app, '1002', 'clave-encargado')  # rol tomado del usuario de negocio
    encargado = cabeceras(login(app, '1002', 'clave-encargado'))
    estado, entregado = llamar(
        app, 'POST', f"/api/reservas/{reserva['id']}/entregar",
        {'responsable': 'Auxiliar'}, encargado,
    )
    assert estado == 200
    prestamo = next(p for p in app.service.data['prestamos'] if p['id'] == reserva['id'])
    assert prestamo['actorId'] == app.service.listar_usuarios()[0]['id']
    assert 'Laura Gómez' in ' '.join(
        evento['texto'] for evento in app.service.historial_equipo(equipo['id'])
    )

    estado, _ = llamar(
        app, 'POST', f"/api/reservas/{reserva['id']}/devolver",
        {'danio': False, 'nota': ''}, encargado,
    )
    assert estado == 200


def test_RNF01_sin_secretos_en_repositorio(tmp_path):
    app = crear_app(tmp_path)
    crear_credencial(app, 'admin', 'clave-super-secreta', 'Administrador')

    identidades = json.loads((tmp_path / 'identidades.json').read_text(encoding='utf-8'))
    credencial = identidades['credenciales']['admin']
    assert 'clave-super-secreta' not in (tmp_path / 'identidades.json').read_text(encoding='utf-8')
    repositorio = tmp_path / 'db.json'
    contenido_repo = repositorio.read_text(encoding='utf-8') if repositorio.exists() else ''
    assert 'clave-super-secreta' not in contenido_repo
    assert len(credencial['hash']) == 64
    assert len(credencial['salt']) == 32
    assert credencial['iteraciones'] >= 100000


def test_SEC04_proveedor_intercambiable(tmp_path):
    class ProveedorFalso:
        def autenticar(self, documento, contraseña):
            return 'token-falso'

        def resolver(self, headers):
            return Identidad('externo', 'Usuario SSO', 'Consulta')

        def crear_credencial(self, documento, contraseña, rol=None):
            raise AssertionError('no debe usarse')

    proveedor = ProveedorFalso()
    assert isinstance(proveedor, ProveedorIdentidad)
    app = PrestaTecApp(
        tmp_path / 'db.json', seed=False, identidad=proveedor,
        identidad_file=tmp_path / 'identidades.json',
    )

    assert llamar(app, 'GET', '/api/equipos', headers={'Cookie': 'x=1'})[0] == 200


def test_RNF01_perfil_de_sesion_expone_permisos(tmp_path):
    app = crear_app(tmp_path)
    assert llamar(app, 'GET', '/api/auth/me')[0] == 401

    crear_credencial(app, 'admin-perfil', 'clave-perfil', 'Administrador')
    headers = cabeceras(login(app, 'admin-perfil', 'clave-perfil'))
    estado, perfil = llamar(app, 'GET', '/api/auth/me', headers=headers)

    assert estado == 200
    assert perfil['rol'] == 'Administrador'
    assert 'CREAR_RECURSO' in perfil['permisos']
    assert 'CONSULTAR_HISTORIAL' in perfil['permisos']
    assert 'contraseña' not in perfil


def test_RNF01_rol_explicito_de_credencial_prevalece_sobre_rol_historico(tmp_path):
    app = crear_app(tmp_path)
    app.service.registrar_usuario('Ana Torres', '1004', 'Estudiante')
    crear_credencial(app, '1004', 'clave-admin', 'Administrador')

    headers = cabeceras(login(app, '1004', 'clave-admin'))
    estado, perfil = llamar(app, 'GET', '/api/auth/me', headers=headers)

    assert estado == 200
    assert perfil['rol'] == 'Administrador'


def test_RNF01_token_invalido_recibe_401(tmp_path):
    app = crear_app(tmp_path)
    crear_credencial(app, 'admin-token', 'clave-token', 'Administrador')

    estado, cuerpo = llamar(
        app, 'GET', '/api/equipos',
        headers={'Cookie': 'prestatec_session=***no-es-un-token***'},
    )

    assert estado == 401
    assert 'Autenticación' in str(cuerpo)


def test_RNF01_permisos_de_reporte_y_historial(tmp_path):
    app = crear_app(tmp_path)
    crear_credencial(app, 'admin', 'clave-admin', 'Administrador')
    admin = cabeceras(login(app, 'admin', 'clave-admin'))
    llamar(app, 'POST', '/api/usuarios', {
        'nombre': 'Usuario Consulta', 'documento': '1003', 'rol': 'Docente',
    }, admin)
    crear_credencial(app, '1003', 'clave-consulta')
    consulta = cabeceras(login(app, '1003', 'clave-consulta'))
    crear_credencial(app, 'guarda2', 'clave-guardia', 'Guarda')
    guarda = cabeceras(login(app, 'guarda2', 'clave-guardia'))

    assert llamar(app, 'GET', '/api/reportes/csv', headers=consulta)[0] == 200
    assert llamar(app, 'GET', '/api/reportes/csv', headers=guarda)[0] == 403
    assert llamar(app, 'GET', '/api/equipos/PT-001/historial', headers=guarda)[0] == 403
