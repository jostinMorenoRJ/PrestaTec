"""C1 — repositorio e inversión de dependencias (ARQ-01, ARQ-02).

TDD: estas pruebas se ejecutan ANTES de crear `prestatec/repository.py` o de
modificar `InventoryService`. Su fallo es la evidencia RED del cambio.
"""
import json
from pathlib import Path

import prestatec.service as service_module
from prestatec.service import InventoryService
from prestatec.repository import JsonFileRepository, Repository  # no existe aún


class RepositorioFalso:
    """Double de prueba que cumple el contrato del repositorio."""

    def __init__(self, datos=None):
        self.datos = datos or {
            'equipos': [], 'usuarios': [], 'prestamos': [], 'eventos': [],
        }
        self.guardados = []

    def load(self):
        return self.datos

    def save(self, datos):
        self.guardados.append(datos)
        self.datos = datos


def test_ARQ01_servicio_acepta_repositorio_inyectado(tmp_path):
    repositorio = RepositorioFalso()
    servicio = InventoryService(repository=repositorio, seed=False)

    servicio.registrar_usuario('María Pérez', '100200300', 'Estudiante')

    assert repositorio.datos['usuarios'][0]['documento'] == '100200300'
    assert len(repositorio.guardados) == 1
    assert not (tmp_path / 'data.json').exists()


def test_ARQ01_repositorio_falso_cumple_el_contrato():
    assert isinstance(RepositorioFalso(), Repository)


def test_ARQ01_dominio_sin_acceso_directo_a_archivos():
    codigo = Path(service_module.__file__).read_text(encoding='utf-8')
    assert 'write_text' not in codigo
    assert 'read_text' not in codigo
    assert 'import json' not in codigo
    assert 'from pathlib' not in codigo


def test_ARQ02_adaptador_json_preserva_formato_y_legacy(tmp_path):
    ruta = tmp_path / 'datos.json'
    ruta.write_text(
        '{"Equipos":[{"Id":"PT-009","Tipo":"Portátil","Nombre":"Legado",'
        '"Ubicacion":"Biblioteca","Estado":"Disponible"}],'
        '"Usuarios":[],"Reservas":[],"Eventos":[]}',
        encoding='utf-8',
    )

    repositorio = JsonFileRepository(ruta)
    datos = repositorio.load()

    assert datos['equipos'][0]['id'] == 'PT-009'
    repositorio.save(datos)
    guardado = json.loads(ruta.read_text(encoding='utf-8'))
    assert guardado['equipos'][0]['id'] == 'PT-009'
