"""C12 — perfiles por rol y experiencia de usuario (PER-01..PER-07).

TDD: creado antes de modificar `identidad.py`, `web.py`, `service.py`,
`repository.py`, la CLI o `static/`. Los fallos de esta fase son la evidencia RED.
"""
import csv
import hashlib
import io
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from scripts.identificar import main as identificar_main
from prestatec.errors import BusinessError
from prestatec.identidad import Identidad
from prestatec.service import InventoryService
from prestatec.web import PrestaTecApp


def crear_app(tmp_path):
    return PrestaTecApp(
        tmp_path / 'db.json', seed=False,
        identidad_file=tmp_path / 'identidades.json',
    )


def credencial(app, documento, contraseña, rol):
    app.identidad.crear_credencial(documento, contraseña, rol)


def login(app, documento, contraseña):
    estado, contenido, _mime, _ = app.dispatch(
        'POST', '/api/auth/login',
        {'documento': documento, 'contraseña': contraseña},
    )
    assert estado == 200, contenido
    return {'Cookie': f'prestatec_session={json.loads(contenido)["token"]}'}


def llamar(app, metodo, ruta, cuerpo=None, headers=None):
    estado, contenido, mime, _nombre = app.dispatch(metodo, ruta, cuerpo, headers)
    if mime.startswith('application/json'):
        return estado, json.loads(contenido)
    return estado, contenido


def preparar(app, documento='1001'):
    usuario = app.service.registrar_usuario('Ana Torres', documento, 'Estudiante')
    equipo = app.service.registrar_equipo('Portátil', 'Lenovo ThinkPad')
    inicio = datetime.now() - timedelta(minutes=1)
    fin = datetime.now() + timedelta(hours=2)
    return usuario, equipo, inicio, fin


def intervalo(inicio, fin):
    return inicio.isoformat(), fin.isoformat()


def credencial_invalida(tmp_path, documento, rol, contraseña='clave'):
    """Escribe una credencial heredada sin pasar por la validación futura."""
    sal = bytes.fromhex('ab' * 16)
    digest = hashlib.pbkdf2_hmac('sha256', contraseña.encode(), sal, 210000).hex()
    archivo = tmp_path / 'identidades.json'
    archivo.write_text(json.dumps({'credenciales': {
        documento: {'salt': sal.hex(), 'hash': digest,
                    'iteraciones': 210000, 'rol': rol},
    }}), encoding='utf-8')
    return archivo


def test_PER01_alta_rechaza_roles_eliminados(tmp_path):
    almacen = PrestaTecApp(
        tmp_path / 'db.json', seed=False,
        identidad_file=tmp_path / 'identidades.json',
    ).identidad

    for rol in ('Administrador', 'Soporte'):
        with pytest.raises(BusinessError, match='Roles permitidos'):
            almacen.crear_credencial(f'usuario-{rol}', 'clave', rol)


def test_PER01_credencial_administrador_no_inicia_sesion(tmp_path):
    credencial_invalida(tmp_path, 'admin', 'Administrador')
    app = PrestaTecApp(
        tmp_path / 'db.json', seed=False,
        identidad_file=tmp_path / 'identidades.json',
    )

    estado, cuerpo = llamar(app, 'POST', '/api/auth/login', {
        'documento': 'admin', 'contraseña': 'clave',
    })
    assert estado == 401
    assert 'inválidas' in str(cuerpo)


def test_PER01_rol_legacy_se_traduce_a_consulta(tmp_path):
    app = crear_app(tmp_path)
    credencial(app, 'ana', 'clave', 'Estudiante')
    headers = login(app, 'ana', 'clave')

    estado, perfil = llamar(app, 'GET', '/api/auth/me', headers=headers)
    assert estado == 200
    assert perfil['rol'] == 'Consulta'


def test_PER01_cli_rechaza_rol_administrador(tmp_path, monkeypatch):
    monkeypatch.setenv('PRESTATEC_ADMIN_PASSWORD', 'clave-cli')
    archivo = tmp_path / 'identidades.json'

    assert identificar_main([
        'crear', 'admin', '--rol', 'Administrador', '--archivo', str(archivo),
    ]) == 1
    assert not archivo.exists()


def test_PER02_me_expone_vista_inicial_por_rol(tmp_path):
    app = crear_app(tmp_path)
    esperado = {'ana': ('Consulta', 'mis'), 'guarda': ('Guarda', 'porteria'),
                'laura': ('Encargado', 'gestion')}
    for documento, (rol, vista) in esperado.items():
        credencial(app, documento, 'clave', rol)
        headers = login(app, documento, 'clave')
        estado, perfil = llamar(app, 'GET', '/api/auth/me', headers=headers)
        assert estado == 200
        assert perfil['rol'] == rol
        assert perfil['vistaInicial'] == vista


def test_PER03_consulta_reserva_solo_su_documento(tmp_path):
    app = crear_app(tmp_path)
    _usuario, equipo, inicio, fin = preparar(app)
    app.service.registrar_usuario('Otra Persona', '1002', 'Estudiante')
    credencial(app, '1001', 'clave', 'Consulta')
    headers = login(app, '1001', 'clave')
    ini, fini = intervalo(inicio, fin)

    estado, reserva = llamar(app, 'POST', '/api/reservas', {
        'equipoId': equipo['id'], 'documento': '1001',
        'inicio': ini, 'fin': fini,
    }, headers)
    assert estado == 200
    guardada = next(
        p for p in app.service.listar_prestamos() if p['id'] == reserva['id']
    )
    assert guardada['documento'] == '1001'

    estado, cuerpo = llamar(app, 'POST', '/api/reservas', {
        'equipoId': equipo['id'], 'documento': '1002',
        'inicio': ini, 'fin': fini,
    }, headers)
    assert estado == 403
    assert 'propio' in str(cuerpo).lower() or 'permiso' in str(cuerpo).lower()


def test_PER03_solo_consulta_puede_reservar(tmp_path):
    app = crear_app(tmp_path)
    _usuario, equipo, inicio, fin = preparar(app)
    credencial(app, 'guarda', 'clave', 'Guarda')
    headers = login(app, 'guarda', 'clave')
    ini, fini = intervalo(inicio, fin)

    estado, _cuerpo = llamar(app, 'POST', '/api/reservas', {
        'equipoId': equipo['id'], 'documento': '1001',
        'inicio': ini, 'fin': fini,
    }, headers)
    assert estado == 403


def test_PER03_conflicto_devuelve_409_con_alternativas(tmp_path):
    app = crear_app(tmp_path)
    _usuario, ocupado, inicio, fin = preparar(app)
    libre = app.service.registrar_equipo('Portátil', 'HP ProBook')
    app.service.crear_prestamo(ocupado['id'], '1001', inicio, fin)
    credencial(app, '1001', 'clave', 'Consulta')
    headers = login(app, '1001', 'clave')
    ini, fini = intervalo(inicio, fin)

    estado, cuerpo = llamar(app, 'POST', '/api/reservas', {
        'equipoId': ocupado['id'], 'documento': '1001',
        'inicio': ini, 'fin': fini,
    }, headers)

    assert estado == 409
    assert 'mensaje' in cuerpo
    assert [a['id'] for a in cuerpo['alternativas']] == [libre['id']]


def test_PER04_consulta_no_ve_reservas_ni_usuarios(tmp_path):
    app = crear_app(tmp_path)
    preparar(app)
    credencial(app, '1001', 'clave', 'Consulta')
    headers = login(app, '1001', 'clave')

    for ruta in ('/api/reservas', '/api/usuarios', '/api/resumen'):
        estado, _cuerpo = llamar(app, 'GET', ruta, headers=headers)
        assert estado == 403, ruta


def test_PER04_consulta_ve_solo_sus_prestamos(tmp_path):
    app = crear_app(tmp_path)
    usuario, equipo, inicio, fin = preparar(app)
    otro = app.service.registrar_usuario('Brayan Ruiz', '1002', 'Docente')
    otro_equipo = app.service.registrar_equipo('Proyector', 'Epson')
    app.service.crear_prestamo(equipo['id'], '1001', inicio, fin)
    app.service.crear_prestamo(otro_equipo['id'], '1002', inicio, fin)
    credencial(app, '1001', 'clave', 'Consulta')
    headers = login(app, '1001', 'clave')

    estado, prestamos = llamar(app, 'GET', '/api/mis-prestamos', headers=headers)
    assert estado == 200
    assert len(prestamos) == 1
    assert prestamos[0]['equipoId'] == equipo['id']
    assert prestamos[0]['documento'] == usuario['documento']
    assert otro['documento'] not in str(prestamos)


def test_PER05_estado_entrega_persistido(tmp_path):
    app = crear_app(tmp_path)
    _usuario, equipo, inicio, fin = preparar(app)
    reserva = app.service.crear_prestamo(equipo['id'], '1001', inicio, fin)

    app.service.entregar(reserva['id'], 'Auxiliar', 'Regular')
    guardado = next(p for p in app.service.data['prestamos'] if p['id'] == reserva['id'])
    assert guardado['estadoEntrega'] == 'Regular'


def test_PER05_verificacion_porteria_audita_exito(tmp_path):
    app = crear_app(tmp_path)
    _usuario, equipo, inicio, fin = preparar(app)
    reserva = app.service.crear_prestamo(equipo['id'], '1001', inicio, fin)
    app.service.entregar(reserva['id'], 'Auxiliar')
    antes = len(app.service.historial_equipo(equipo['id']))
    actor = Identidad('guarda-1', 'Carlos Guarda', 'Guarda')

    resultado = app.service.verificar_porteria(equipo['id'], actor=actor)
    despues = app.service.historial_equipo(equipo['id'])

    assert resultado['ok'] is True
    assert len(despues) == antes + 1
    assert 'Carlos Guarda' in despues[0]['texto']


def test_PER05_csv_muestra_nombre_del_equipo(tmp_path):
    app = crear_app(tmp_path)
    _usuario, equipo, inicio, fin = preparar(app)
    app.service.crear_prestamo(equipo['id'], '1001', inicio, fin)
    credencial(app, 'laura', 'clave', 'Encargado')
    headers = login(app, 'laura', 'clave')

    estado, contenido = llamar(app, 'GET', '/api/reportes/csv', headers=headers)
    assert estado == 200
    filas = list(csv.reader(io.StringIO(contenido.decode('utf-8-sig'))))
    assert filas[1][1] == equipo['nombre']
    assert filas[1][1] != equipo['id']


def test_PER06_json_mixto_conserva_claves_nuevas(tmp_path):
    ruta = tmp_path / 'mixto.json'
    ruta.write_text(json.dumps({
        'Equipos': [{'Id': 'PT-009', 'Tipo': 'Portátil', 'Nombre': 'Legado',
                     'Ubicacion': 'Biblioteca', 'Estado': 'Disponible'}],
        'equipos': [{'id': 'PT-050', 'tipo': 'Portátil', 'nombre': 'Nuevo',
                     'ubicacion': 'Sala 2', 'estado': 'Disponible'}],
        'Usuarios': [], 'Reservas': [], 'Eventos': [],
    }), encoding='utf-8')

    ids = [e['id'] for e in InventoryService(ruta, seed=False).listar_equipos()]
    assert ids == ['PT-009', 'PT-050']


def test_PER07_ui_tres_perfiles_y_disponibilidad():
    raiz = Path(__file__).resolve().parents[1] / 'static'
    js = (raiz / 'app.js').read_text(encoding='utf-8')
    html = (raiz / 'index.html').read_text(encoding='utf-8')

    assert '/disponibilidad' in js
    for rol in ('Consulta', 'Guarda', 'Encargado'):
        assert rol in js
    assert 'Administrador' not in js
    assert 'v-mis' in html
    # PER-07: ningún botón de navegación queda sin controlador.
    assert "$$('nav button').forEach(b => b.onclick" in js
