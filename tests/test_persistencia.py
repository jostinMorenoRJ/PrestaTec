"""C3 — persistencia SQLite y migración segura (DAT-01..DAT-04).

TDD: creado antes de `prestatec/sqlite_repository.py` y `prestatec/migracion.py`.
"""
import hashlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from prestatec.migracion import migrar_desde_json
from prestatec.repository import JsonFileRepository
from prestatec.service import InventoryService
from prestatec.sqlite_repository import SQLiteRepository


JSON_MIXTO = {
    'Equipos': [
        {'Id': 'PT-009', 'Tipo': 'Portátil', 'Nombre': 'Equipo legado',
         'Ubicacion': 'Biblioteca', 'Estado': 'Disponible'},
    ],
    'equipos': [
        {'id': 'PT-050', 'tipo': 'Proyector', 'nombre': 'Equipo nuevo',
         'ubicacion': 'Sala 2', 'estado': 'Disponible'},
    ],
    'Usuarios': [
        {'Id': 'U-001', 'Nombre': 'Ana Torres', 'Documento': '1001', 'Rol': 'Estudiante'},
    ],
    'Reservas': [],
    'Eventos': [],
}


def test_DAT02_migracion_mixta_conserva_legacy_y_nuevo(tmp_path):
    origen = tmp_path / 'data.json'
    destino = tmp_path / 'prestatec.db'
    copia = tmp_path / 'respaldo.json'
    origen.write_text(json.dumps(JSON_MIXTO), encoding='utf-8')

    informe = migrar_desde_json(origen, destino, copia)

    ids = {e['id'] for e in SQLiteRepository(destino).load()['equipos']}
    assert {'PT-009', 'PT-050'} <= ids
    assert copia.exists()
    esperado = hashlib.sha256(origen.read_bytes()).hexdigest()
    assert informe['respaldo']['sha256'] == esperado


def test_DAT01_esquema_con_integridad_referencial(tmp_path):
    ruta = tmp_path / 'db.sqlite'
    SQLiteRepository(ruta)
    conexion = sqlite3.connect(ruta)

    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute(
            'INSERT INTO prestamos (id, equipoId, usuarioId, inicio, fin, estado) '
            "VALUES ('X', 'NO-EXISTE', 'NO-USER', '', '', 'Confirmada')"
        )
    conexion.close()


def test_DAT03_veinte_escrituras_concurrentes(tmp_path):
    servicio = InventoryService(
        repository=SQLiteRepository(tmp_path / 'db.sqlite'), seed=False
    )

    def alta(indice):
        return servicio.registrar_equipo('Portátil', f'Equipo {indice}')

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(alta, range(20)))

    equipos = servicio.listar_equipos()
    assert len(equipos) == 20
    assert len({e['id'] for e in equipos}) == 20


def test_DAT02_rechaza_sobrescribir_destino_sin_autorizacion(tmp_path):
    origen = tmp_path / 'data.json'
    destino = tmp_path / 'db.sqlite'
    origen.write_text(json.dumps(JSON_MIXTO), encoding='utf-8')
    destino.write_bytes(b'base preexistente')
    copia = tmp_path / 'respaldo.json'

    with pytest.raises(Exception, match='destino|sobrescrib|existe'):
        migrar_desde_json(origen, destino, copia)

    assert destino.read_bytes() == b'base preexistente'


def test_DAT04_cambio_de_backend_sin_perder_el_original(tmp_path):
    origen = tmp_path / 'data.json'
    destino = tmp_path / 'db.sqlite'
    copia = tmp_path / 'respaldo.json'
    origen.write_text(json.dumps(JSON_MIXTO), encoding='utf-8')
    original = origen.read_bytes()

    migrar_desde_json(origen, destino, copia)

    con_json = InventoryService(repository=JsonFileRepository(origen), seed=False)
    con_sqlite = InventoryService(repository=SQLiteRepository(destino), seed=False)
    ids_sqlite = {e['id'] for e in con_sqlite.listar_equipos()}
    assert {'PT-009', 'PT-050'} <= ids_sqlite
    assert con_json.listar_equipos()  # el backend JSON sigue operativo
    assert origen.read_bytes() == original
