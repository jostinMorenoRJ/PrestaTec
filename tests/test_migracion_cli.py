"""C3 — proceso explícito de migración (DAT-02, DAT-04).

TDD: creado antes de `migrar.py`.
"""
import json

from prestatec.sqlite_repository import SQLiteRepository


def test_cli_migracion_crea_respaldo_y_base(tmp_path, capsys):
    from scripts.migrar import main

    origen = tmp_path / 'data.json'
    destino = tmp_path / 'prestatec.db'
    copia = tmp_path / 'respaldo.json'
    origen.write_text(json.dumps({
        'Equipos': [{'Id': 'PT-009', 'Tipo': 'Portátil', 'Nombre': 'Legado',
                     'Ubicacion': 'Biblioteca', 'Estado': 'Disponible'}],
        'Usuarios': [], 'Reservas': [], 'Eventos': [],
    }), encoding='utf-8')

    codigo = main([str(origen), str(destino), str(copia)])

    assert codigo == 0
    assert copia.exists()
    assert SQLiteRepository(destino).load()['equipos'][0]['id'] == 'PT-009'
    assert 'sha256' in capsys.readouterr().out
