"""Ciclo DEMO: acceso usable en el primer arranque (Spec -> Test -> Codigo)."""
import json

import pytest

from prestatec.identidad import AlmacenCredenciales
from prestatec.service import InventoryService
from prestatec.web import PrestaTecApp

CUENTAS = (
    ('admin', 'admin123', 'Encargado'),
    ('celador', 'celador123', 'Guarda'),
    ('estudiante', 'estudiante123', 'Consulta'),
)


@pytest.fixture
def contexto(tmp_path):
    servicio = InventoryService(tmp_path / 'data.json', seed=False)
    almacen = AlmacenCredenciales(tmp_path / 'identidades.json')
    return servicio, almacen


def test_DEMO01_crea_las_tres_cuentas_visibles_en_pantalla(contexto):
    from prestatec.demo import preparar_demo

    servicio, almacen = contexto
    resultado = preparar_demo(servicio=servicio, almacen=almacen)

    for documento, clave, rol in CUENTAS:
        assert almacen.verificar(documento, clave), documento
        assert almacen.rol(documento) == rol
    assert sorted(resultado['credenciales']) == ['admin', 'celador', 'estudiante']


def test_DEMO02_estudiante_existe_como_usuario_de_negocio(contexto):
    from prestatec.demo import preparar_demo

    servicio, almacen = contexto
    preparar_demo(servicio=servicio, almacen=almacen)

    assert any(u['documento'] == 'estudiante' for u in servicio.listar_usuarios())


def test_DEMO03_no_sobrescribe_credenciales_ni_usuarios_existentes(contexto):
    from prestatec.demo import preparar_demo

    servicio, almacen = contexto
    almacen.crear('admin', 'clave-personal', 'Encargado')
    servicio.registrar_usuario('Estudiante Real', 'estudiante', 'Estudiante')

    resultado = preparar_demo(servicio=servicio, almacen=almacen)

    assert almacen.verificar('admin', 'clave-personal')
    assert not almacen.verificar('admin', 'admin123')
    assert 'admin' not in resultado['credenciales']
    assert 'estudiante' not in resultado['usuarios']
    usuario = next(u for u in servicio.listar_usuarios() if u['documento'] == 'estudiante')
    assert usuario['nombre'] == 'Estudiante Real'


def test_DEMO04_login_funciona_en_la_misma_app_que_sirve_la_ui(tmp_path):
    from prestatec.demo import preparar_demo

    app = PrestaTecApp(
        data_file=tmp_path / 'data.json', seed=False,
        identidad_file=tmp_path / 'identidades.json',
    )
    preparar_demo(servicio=app.service, almacen=app.identidad.almacen)

    estado, cuerpo, _, _ = app.dispatch(
        'POST', '/api/auth/login',
        {'documento': 'admin', 'contraseña': 'admin123'},
    )

    assert estado == 200
    assert json.loads(cuerpo)['token']
