"""C3 — cambio de backend por configuración (DAT-04).

TDD: creado antes de `prestatec/config.py`; su fallo documenta la fase RED.
"""
import json

from prestatec.config import Configuracion
from prestatec.repository import JsonFileRepository
from prestatec.sqlite_repository import SQLiteRepository
from prestatec.web import PrestaTecApp
from helpers import autenticar


def test_DAT04_factory_selecciona_backend_segun_configuracion(tmp_path, monkeypatch):
    monkeypatch.setenv('PRESTATEC_BACKEND', 'sqlite')
    monkeypatch.setenv('PRESTATEC_DATA_FILE', str(tmp_path / 'db.sqlite'))
    assert isinstance(Configuracion().repositorio(), SQLiteRepository)

    monkeypatch.setenv('PRESTATEC_BACKEND', 'json')
    monkeypatch.setenv('PRESTATEC_DATA_FILE', str(tmp_path / 'db.json'))
    assert isinstance(Configuracion().repositorio(), JsonFileRepository)


def test_DAT04_app_opera_con_sqlite_sin_cambiar_reglas(tmp_path):
    configuracion = Configuracion(
        backend='sqlite', ruta_datos=tmp_path / 'db.sqlite'
    )
    app = PrestaTecApp(
        seed=False, configuracion=configuracion,
        identidad_file=tmp_path / 'identidades.json',
    )
    headers = autenticar(app)

    estado, contenido, mime, _nombre = app.dispatch(
        'POST', '/api/equipos',
        {'tipo': 'Portátil', 'nombre': 'Equipo SQLite', 'ubicacion': 'Sala 1'},
        headers,
    )
    assert estado == 200
    assert json.loads(contenido)['id'] == 'PT-001'

    estado, contenido, _mime, _nombre = app.dispatch('GET', '/api/equipos', headers=headers)
    assert estado == 200
    assert json.loads(contenido)[0]['nombre'] == 'Equipo SQLite'
