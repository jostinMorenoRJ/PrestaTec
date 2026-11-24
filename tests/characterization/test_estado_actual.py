"""Caracterización de la línea base (Etapa 1), ajustada en C5 y C12.

Estas pruebas documentan el comportamiento REAL del código original, incluidos
defectos conocidos. No son criterios de aceptación: los cambios C1..C12 podrán
modificar deliberadamente estos valores, pero solo con una spec aprobada que así
lo indique.

- C5 cambia el acceso anónimo por autenticación obligatoria (SEC-01).
- C12 corrige los defectos P3/P5/P6/P8/P9 según `specs/perfiles/spec.md`
  (PER-03, PER-04, PER-05, PER-06, PER-07). Las expectativas de esos casos se
  actualizan aquí para documentar el nuevo comportamiento, no para ocultar el
  anterior: el motivo queda registrado en cada docstring.
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


def autenticar(app, documento='gestor-caracterizacion',
               contraseña='clave-caracterizacion', rol='Encargado'):
    """C12: el perfil de gestión sustituye al antiguo `Administrador`."""
    app.identidad.crear_credencial(documento, contraseña, rol)
    return _login(app, documento, contraseña)


def como_consulta(app, documento, contraseña='clave-consulta'):
    """La solicitud de préstamo la hace el titular del documento (PER-03)."""
    app.identidad.crear_credencial(documento, contraseña, 'Consulta')
    return _login(app, documento, contraseña)


def _login(app, documento, contraseña):
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
    consulta = como_consulta(app, '100200300')
    reserva = call(app, 'POST', '/api/reservas', {
        'equipoId': equipo['id'], 'documento': '100200300',
        'inicio': inicio.isoformat(), 'fin': fin.isoformat(),
    }, consulta)[1]
    return equipo, reserva, inicio, fin


def test_c12_conflicto_devuelve_409_con_alternativas(tmp_path):
    """P3 corregido (PER-03): antes 400 sin alternativas; ahora 409 con opciones."""
    app = crear_app(tmp_path)
    headers = autenticar(app)
    equipo, _reserva, inicio, fin = preparar_prestamo(app, headers)
    libre = call(app, 'POST', '/api/equipos', {
        'tipo': 'Portátil', 'nombre': 'Portátil libre', 'ubicacion': 'Sala 2',
    }, headers)[1]
    # La credencial Consulta ya fue creada por `preparar_prestamo`.
    # Se emite una sesión nueva para usarla en el segundo intento.
    estado, contenido, _mime, _ = app.dispatch(
        'POST', '/api/auth/login',
        {'documento': '100200300', 'contraseña': 'clave-consulta'},
    )
    assert estado == 200
    sesion = {'Cookie': f'prestatec_session={json.loads(contenido)["token"]}'}

    status, body = call(app, 'POST', '/api/reservas', {
        'equipoId': equipo['id'], 'documento': '100200300',
        'inicio': inicio.isoformat(), 'fin': fin.isoformat(),
    }, sesion)
    assert status == 409
    assert 'mensaje' in body
    assert [a['id'] for a in body['alternativas']] == [libre['id']]


def test_c12_csv_tiene_bom_y_nombre_del_equipo(tmp_path):
    """P3 corregido (PER-05): la columna 'Equipo' muestra el nombre, no el ID."""
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
    assert filas[1][1] == equipo['nombre']
    assert filas[1][1] != equipo['id']


def test_caracterizacion_disponibilidad_funciona_y_sin_parametros_falla(tmp_path):
    """P5: el endpoint opera; C12 (PER-04) lo conecta con la interfaz."""
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
    consulta = como_consulta(app, '999')
    call(app, 'POST', '/api/reservas', {
        'equipoId': ocupado['id'], 'documento': '999',
        'inicio': inicio.isoformat(), 'fin': fin.isoformat(),
    }, consulta)
    query = urlencode({'tipo': 'Portátil', 'inicio': inicio.isoformat(), 'fin': fin.isoformat()})
    status, body = call(app, 'GET', f'/api/disponibilidad?{query}', headers=headers)
    assert status == 200
    ids = [item['id'] for item in body]
    assert libre['id'] in ids
    assert ocupado['id'] not in ids
    assert call(app, 'GET', '/api/disponibilidad', headers=headers)[0] == 400


def test_c12_json_mixto_conserva_claves_nuevas(tmp_path):
    """P9 corregido (PER-06): sobreviven el legado y las claves nuevas."""
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
    assert ids == ['PT-009', 'PT-050']
    assert 'PT-050' in ids


def test_caracterizacion_rutas_sin_autenticacion_responden_401_en_c5(tmp_path):
    """C5 cambia deliberadamente el acceso anónimo documentado en C0."""
    app = crear_app(tmp_path)
    app.service.registrar_usuario('Daniel Rojas', '12345', 'Estudiante')

    for ruta in ('/api/usuarios', '/api/equipos', '/api/resumen', '/api/reportes/csv'):
        assert call(app, 'GET', ruta)[0] == 401
    assert call(app, 'POST', '/api/usuarios', {
        'nombre': 'Ana', 'documento': '999', 'rol': 'Estudiante',
    })[0] == 401


def test_c12_estado_entrega_se_persiste(tmp_path):
    """P6 corregido (PER-05): `estadoEntrega` se guarda en el préstamo."""
    app = crear_app(tmp_path)
    headers = autenticar(app)
    equipo, reserva, _inicio, _fin = preparar_prestamo(app, headers)
    call(app, 'POST', f"/api/reservas/{reserva['id']}/entregar", {
        'responsable': 'Auxiliar', 'estadoEntrega': 'Regular',
    }, headers)
    prestamo = next(p for p in app.service.data['prestamos'] if p['id'] == reserva['id'])
    assert prestamo['estadoEntrega'] == 'Regular'
    eventos = app.service.historial_equipo(equipo['id'])
    assert any('Estado: Regular' in evento['texto'] for evento in eventos)


def test_c12_verificacion_exitosa_genera_evento(tmp_path):
    """P8 corregido (PER-05): toda verificación de portería queda auditada."""
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
    despues = app.service.historial_equipo(equipo['id'])
    assert len(despues) == antes + 1
    assert 'gestor-caracterizacion' in despues[0]['texto']
