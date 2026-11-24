"""C13 — pantalla de acceso completa y cuentas de demostración (ACC-01..ACC-04).

TDD: creado antes de modificar `static/` o las credenciales del proyecto.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

from prestatec.identidad import AlmacenCredenciales
from prestatec.web import PrestaTecApp

RAIZ = Path(__file__).resolve().parents[1]
CUENTAS = [
    ('admin', 'admin123', 'Encargado', 'gestion'),
    ('celador', 'celador123', 'Guarda', 'porteria'),
    ('estudiante', 'estudiante123', 'Consulta', 'mis'),
]


def estaticos():
    html = (RAIZ / 'static' / 'index.html').read_text(encoding='utf-8')
    css = (RAIZ / 'static' / 'styles.css').read_text(encoding='utf-8')
    js = (RAIZ / 'static' / 'app.js').read_text(encoding='utf-8')
    return html, css, js


def test_ACC01_cuentas_reales_inician_sesion_con_su_perfil():
    ruta = RAIZ / 'identidades.json'
    almacen = AlmacenCredenciales(ruta)

    # La credencial heredada `admin` (Administrador) fue sustituida.
    assert almacen.rol('admin') == 'Encargado'
    for documento, clave, rol, vista in CUENTAS:
        assert almacen.verificar(documento, clave), documento
        assert almacen.rol(documento) == rol

    app = PrestaTecApp(
        data_file=RAIZ / 'data.json', seed=False, identidad_file=ruta
    )
    for documento, clave, rol, vista in CUENTAS:
        token = app.identidad.autenticar(documento, clave)
        assert token, documento
        estado, contenido, _mime, _ = app.dispatch(
            'GET', '/api/auth/me', {},
            {'Cookie': f'prestatec_session={token}'},
        )
        assert estado == 200, contenido
        perfil = json.loads(contenido)
        assert perfil['rol'] == rol
        assert perfil['vistaInicial'] == vista


def test_ACC01_estudiante_registrado_puede_reservar(tmp_path):
    app = PrestaTecApp(
        tmp_path / 'db.json', seed=False,
        identidad_file=tmp_path / 'identidades.json',
    )
    app.service.registrar_usuario('Estudiante', 'estudiante', 'Estudiante')
    equipo = app.service.registrar_equipo('Portátil', 'Lenovo ThinkPad')
    app.identidad.crear_credencial('estudiante', 'estudiante123', 'Consulta')
    estado, contenido, _mime, _ = app.dispatch(
        'POST', '/api/auth/login',
        {'documento': 'estudiante', 'contraseña': 'estudiante123'},
    )
    assert estado == 200, contenido
    headers = {'Cookie': 'prestatec_session=' + json.loads(contenido)['token']}
    inicio = (datetime.now() + timedelta(hours=1)).isoformat()
    fin = (datetime.now() + timedelta(hours=3)).isoformat()

    estado, contenido, _mime, _ = app.dispatch('POST', '/api/reservas', {
        'equipoId': equipo['id'], 'documento': 'estudiante',
        'inicio': inicio, 'fin': fin,
    }, headers)

    assert estado == 200, contenido
    guardada = next(
        p for p in app.service.listar_prestamos()
        if p['id'] == json.loads(contenido)['id']
    )
    assert guardada['documento'] == 'estudiante'


def test_ACC02_pantalla_de_acceso_completa_y_no_ventana_vacia():
    html, css, js = estaticos()

    inicio = html.index('id="acceso"')
    fin = html.index('</section>', inicio)
    form = html.index('id="fl"')
    assert inicio < form < fin, 'El formulario debe estar dentro de #acceso'
    cabecera = html[html.index('<header'):html.index('</header>')]
    assert 'id="fl"' not in cabecera

    assert 'Presta' in html[html.index('id="acceso"'):fin]
    assert 'min-height:100vh' in css
    assert 'body.sin-sesion .topbar' in css
    assert 'body.con-sesion #acceso{display:none}' in css
    assert "$('#acceso').hidden = !!perfil" in js


def test_ACC03_las_tres_cuentas_aparecen_en_el_acceso():
    html, _css, _js = estaticos()
    acceso = html[html.index('id="acceso"'):html.index('</section>', html.index('id="acceso"'))]

    for usuario, clave, rol, _vista in CUENTAS:
        assert usuario in acceso
        assert clave in acceso
        assert rol in acceso
    assert 'demostración' in acceso.lower()


def test_ACC04_error_visible_y_campos_etiquetados():
    html, _css, js = estaticos()

    assert '<label for="usuario"' in html
    assert '<label for="clave"' in html
    assert 'id="error-acceso"' in html
    assert "$('#error-acceso')" in js
    assert "$('#error-acceso').hidden = false" in js
