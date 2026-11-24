"""Caracterización de la línea base (Etapa 1), ajustada en C5.

Estas pruebas documentan el comportamiento REAL del código original, incluidos
defectos conocidos. No son criterios de aceptación: los cambios C1..C11 podrán
modificar deliberadamente estos valores, pero solo con una spec aprobada que
así lo indique. C5 cambia deliberadamente el acceso anónimo por autenticación
obligatoria (SEC-01), así que esa expectativa se actualizó aquí con la spec.
"""
import csv
import io
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode

import pytest

from prestatec.service import InventoryService
from prestatec.web import PrestaTecApp


pytestmark = pytest.mark.characterization


def crear_app(tmp_path):
    return PrestaTecApp(
        tmp_path / 'db.json', seed=False,
        identidad_file=tmp_path / 'identidades.json',
    )


def autenticar(app):
    documento, contraseña = 'admin-caracterizacion', 'clave-caracterizacion'
    app.identidad.crear_credencial(documento, contraseña, 'Administrador')
    estado, contenido, _mime, _nombre = app.dispatch(
        'POST', '/api/auth/login',
        {'documento': documento, 'contraseña': contraseña},
    )
    assert estado == 200, contenido
    return {'Cookie': f'prestatec_session={json.loads(contenido)["token"]}'}


def call(app, method, path, body=None, headers=None):
    status, content, mime, filename = app.dispatch(method, path, body, headers)
    if mime.startswith('application/json'):
        return status, json.loads(content)
    return status, content, filename


def preparar_prestamo(app, headers):
    call(app, 'POST', '/api/usuarios', {
        'nombre': 'María Pérez', 'documento': '100200300', 'rol': 'Estudiante',
    }, headers)
    equipo = call(app, 'POST', '/api/equipos', {
        'tipo': 'Portátil', 'nombre': 'Lenovo ThinkPad', 'ubicacion': 'Biblioteca',
    }, headers)[1]
    inicio = datetime.now() - timedelta(minutes=1)
    fin = datetime.now() + timedelta(hours=2)
    reserva = call(app, 'POST', '/api/reservas', {
        'equipoId': equipo['id'], 'documento': '100200300',
        'inicio': inicio.isoformat(), 'fin': fin.isoformat(),
    }, headers)[1]
    return equipo, reserva, inicio, fin


def test_caracterizacion_conflicto_devuelve_400_sin_alternativas(tmp_path):
    """P3: la UI espera 409 + alternativas, pero hoy se responde 400."""
    app = crear_app(tmp_path)
    headers = autenticar(app)
    equipo, _reserva, inicio, fin = preparar_prestamo(app, headers)
    status, body = call(app, 'POST', '/api/reservas', {
        'equipoId': equipo['id'], 'documento': '100200300',
        'inicio': inicio.isoformat(), 'fin': fin.isoformat(),
    }, headers)
    assert status == 400
    assert 'mensaje' in body
    assert 'alternativas' not in body


def test_caracterizacion_csv_tiene_bom_y_id_en_columna_equipo(tmp_path):
    """P3/RF08: la columna 'Equipo' contiene el ID, no el nombre."""
    app = crear_app(tmp_path)
    headers = autenticar(app)
    equipo, _reserva, _inicio, _fin = preparar_prestamo(app, headers)
    status, content, filename = call(app, 'GET', '/api/reportes/csv', headers=headers)
    assert status == 200
    assert content.startswith(b'\xef\xbb\xbf')
    assert filename == 'reporte_prestamos.csv'
    filas = list(csv.reader(io.StringIO(content.decode('utf-8-sig'))))
    assert filas[0] == ['Préstamo', 'Equipo', 'Usuario', 'Inicio', 'Fin',
                        'Estado', 'Entregado', 'Devuelto', 'Responsable', 'Nota']
    assert filas[1][1] == equipo['id']
    assert filas[1][1] != equipo['nombre']


def test_caracterizacion_disponibilidad_funciona_y_sin_parametros_falla(tmp_path):
    """P5: el endpoint opera, aunque la UI nunca lo invoca."""
    app = crear_app(tmp_path)
    headers = autenticar(app)
    call(app, 'POST', '/api/usuarios', {
        'nombre': 'Ana Torres', 'documento': '999', 'rol': 'Estudiante',
    }, headers)
    libre = call(app, 'POST', '/api/equipos', {
        'tipo': 'Portátil', 'nombre': 'Libre', 'ubicacion': 'Biblioteca',
    }, headers)[1]
    ocupado = call(app, 'POST', '/api/equipos', {
        'tipo': 'Portátil', 'nombre': 'Ocupado', 'ubicacion': 'Biblioteca',
    }, headers)[1]
    inicio = datetime.now() + timedelta(hours=1)
    fin = inicio + timedelta(hours=2)
    call(app, 'POST', '/api/reservas', {
        'equipoId': ocupado['id'], 'documento': '999',
        'inicio': inicio.isoformat(), 'fin': fin.isoformat(),
    }, headers)
    query = urlencode({'tipo': 'Portátil', 'inicio': inicio.isoformat(), 'fin': fin.isoformat()})
    status, body = call(app, 'GET', f'/api/disponibilidad?{query}', headers=headers)
    assert status == 200
    ids = [item['id'] for item in body]
    assert libre['id'] in ids
    assert ocupado['id'] not in ids
    assert call(app, 'GET', '/api/disponibilidad', headers=headers)[0] == 400


def test_caracterizacion_json_mixto_descarta_claves_nuevas(tmp_path):
    """P9: si coexisten 'Equipos' y 'equipos', sobrevive solo el legado."""
    ruta = tmp_path / 'mixto.json'
    ruta.write_text(json.dumps({
        'Equipos': [{'Id': 'PT-009', 'Tipo': 'Portátil', 'Nombre': 'Legado',
                     'Ubicacion': 'Biblioteca', 'Estado': 'Disponible'}],
        'equipos': [{'id': 'PT-050', 'tipo': 'Portátil', 'nombre': 'Nuevo',
                     'ubicacion': 'Sala 2', 'estado': 'Disponible'}],
        'Usuarios': [], 'Reservas': [], 'Eventos': [],
    }), encoding='utf-8')
    sistema = InventoryService(ruta, seed=False)
    ids = [equipo['id'] for equipo in sistema.listar_equipos()]
    assert ids == ['PT-009']
    assert 'PT-050' not in ids


def test_caracterizacion_rutas_sin_autenticacion_responden_401_en_c5(tmp_path):
    """C5 cambia deliberadamente el acceso anónimo documentado en C0."""
    app = crear_app(tmp_path)
    app.service.registrar_usuario('Daniel Rojas', '12345', 'Estudiante')

    for ruta in ('/api/usuarios', '/api/equipos', '/api/resumen', '/api/reportes/csv'):
        assert call(app, 'GET', ruta)[0] == 401
    assert call(app, 'POST', '/api/usuarios', {
        'nombre': 'Ana', 'documento': '999', 'rol': 'Estudiante',
    })[0] == 401


def test_caracterizacion_estado_entrega_no_se_persiste(tmp_path):
    """P6: estadoEntrega viaja en el body, solo aparece en el texto del evento."""
    app = crear_app(tmp_path)
    headers = autenticar(app)
    equipo, reserva, _inicio, _fin = preparar_prestamo(app, headers)
    call(app, 'POST', f"/api/reservas/{reserva['id']}/entregar", {
        'responsable': 'Auxiliar', 'estadoEntrega': 'Regular',
    }, headers)
    prestamo = next(p for p in app.service.data['prestamos'] if p['id'] == reserva['id'])
    assert 'estadoEntrega' not in prestamo
    eventos = app.service.historial_equipo(equipo['id'])
    assert any('Estado: Regular' in evento['texto'] for evento in eventos)


def test_caracterizacion_verificacion_exitosa_no_genera_evento(tmp_path):
    """P8: solo se registran alertas de equipos sin préstamo activo."""
    app = crear_app(tmp_path)
    headers = autenticar(app)
    equipo, _reserva, _inicio, _fin = preparar_prestamo(app, headers)
    call(app, 'POST', f"/api/reservas/{_reserva['id']}/entregar", {
        'responsable': 'Auxiliar',
    }, headers)
    antes = len(app.service.historial_equipo(equipo['id']))
    status, body = call(app, 'GET', f"/api/porteria/{equipo['id']}", headers=headers)
    assert status == 200
    assert body['ok'] is True
    assert len(app.service.historial_equipo(equipo['id'])) == antes
