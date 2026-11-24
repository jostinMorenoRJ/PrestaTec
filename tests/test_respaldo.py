"""C4 — respaldo y restauración verificable (DAT-05, DAT-06).

TDD: creado antes de `prestatec/backup.py` y antes de añadir el manifiesto a la
migración de C3. Su fallo documenta la fase RED.
"""
import hashlib
import json
import os
from datetime import datetime, timedelta

import pytest

from prestatec.errors import BusinessError


def estado_demo():
    return {
        'equipos': [
            {'id': f'PT-{i:03d}', 'tipo': 'Portátil', 'nombre': f'Equipo {i}',
             'ubicacion': 'Biblioteca', 'estado': 'Disponible'}
            for i in range(1, 7)
        ],
        'usuarios': [
            {'id': f'U-{i:03d}', 'nombre': f'Usuario {i}',
             'documento': str(1000 + i), 'rol': 'Estudiante'}
            for i in range(1, 5)
        ],
        'prestamos': [{
            'id': 'P-001', 'equipoId': 'PT-001', 'usuarioId': 'U-001',
            'inicio': '2026-11-24T09:00:00+00:00', 'fin': '2026-11-24T11:00:00+00:00',
            'estado': 'Confirmada', 'entregadoEn': None, 'devueltoEn': None,
            'responsable': None, 'nota': '',
        }],
        'eventos': [{
            'fecha': '2026-11-24T08:00:00+00:00', 'equipoId': 'PT-001',
            'texto': 'Equipo registrado en el inventario.',
        }],
    }


def test_DAT05_backup_registra_hash_timestamp_y_conteos(tmp_path):
    from prestatec.backup import BackupService

    origen = tmp_path / 'data.json'
    origen.write_text(json.dumps(estado_demo()), encoding='utf-8')
    destino = tmp_path / 'backups'

    manifiesto = BackupService().crear(origen, directorio=destino)

    assert manifiesto['conteos'] == {
        'equipos': 6, 'usuarios': 4, 'prestamos': 1, 'eventos': 1,
    }
    assert manifiesto['sha256'] == hashlib.sha256(origen.read_bytes()).hexdigest()
    assert manifiesto['creadoEn'].endswith('+00:00')
    assert os.path.exists(manifiesto['archivo'])
    assert BackupService().validar(manifiesto) is True


def test_DAT05_la_migracion_deja_manifiesto_verificable(tmp_path):
    from prestatec.backup import BackupService
    from prestatec.migracion import migrar_desde_json

    origen = tmp_path / 'data.json'
    origen.write_text(json.dumps(estado_demo()), encoding='utf-8')

    informe = migrar_desde_json(
        origen, tmp_path / 'db.sqlite', tmp_path / 'respaldo.json'
    )

    manifiesto = informe['respaldo']['manifiesto']
    assert BackupService().validar(manifiesto) is True
    assert informe['respaldo']['conteos']['equipos'] == 6
    assert informe['respaldo']['conteos']['usuarios'] == 4


def test_DAT06_restore_devuelve_estado_exacto(tmp_path):
    from prestatec.backup import BackupService

    origen = tmp_path / 'data.json'
    original = estado_demo()
    origen.write_text(json.dumps(original), encoding='utf-8')
    servicio = BackupService()
    manifiesto = servicio.crear(origen)
    instantanea = open(manifiesto['archivo'], 'rb').read()

    modificado = estado_demo()
    modificado['equipos'].pop()
    modificado['equipos'][0]['nombre'] = 'Cambio posterior'
    origen.write_text(json.dumps(modificado), encoding='utf-8')
    futuro = datetime.fromisoformat(manifiesto['creadoEn']) + timedelta(seconds=120)
    os.utime(origen, (futuro.timestamp(), futuro.timestamp()))

    with pytest.raises(BusinessError, match='confirm'):
        servicio.restaurar(manifiesto, origen)
    assert json.loads(origen.read_text(encoding='utf-8')) == modificado

    servicio.restaurar(manifiesto, origen, confirmar=True)
    assert json.loads(origen.read_text(encoding='utf-8')) == json.loads(
        instantanea.decode('utf-8')
    )


def test_DAT06_copia_corrupta_se_rechaza(tmp_path):
    from prestatec.backup import BackupService

    origen = tmp_path / 'data.json'
    origen.write_text(json.dumps(estado_demo()), encoding='utf-8')
    servicio = BackupService()
    manifiesto = servicio.crear(origen)
    with open(manifiesto['archivo'], 'wb') as archivo:
        archivo.write(b'copia corrupta')

    with pytest.raises(BusinessError, match='hash|copia'):
        servicio.validar(manifiesto)
    with pytest.raises(BusinessError, match='hash|copia'):
        servicio.restaurar(manifiesto, origen, confirmar=True)
    assert json.loads(origen.read_text(encoding='utf-8')) == estado_demo()


def test_DAT06_copia_sqlite_corrupta_se_rechaza(tmp_path):
    from prestatec.backup import BackupService

    origen = tmp_path / 'data.json'
    origen.write_text(json.dumps(estado_demo()), encoding='utf-8')
    servicio = BackupService()
    manifiesto = servicio.crear(origen)
    copia = manifiesto['archivo'].replace('.json', '.db')
    with open(copia, 'wb') as archivo:
        archivo.write(b'no es una base sqlite')
    manifiesto['archivo'] = copia
    manifiesto['backend'] = 'sqlite'
    manifiesto['sha256'] = hashlib.sha256(open(copia, 'rb').read()).hexdigest()

    with pytest.raises(BusinessError, match='copia|leer'):
        servicio.validar(manifiesto)


def test_cli_backup_y_restore(tmp_path, capsys):
    from respaldar import main

    origen = tmp_path / 'data.json'
    original = estado_demo()
    origen.write_text(json.dumps(original), encoding='utf-8')
    directorio = tmp_path / 'backups'

    assert main(['crear', str(origen), '--directorio', str(directorio)]) == 0
    manifiesto = json.loads(capsys.readouterr().out)['manifiesto']

    modificado = estado_demo()
    modificado['equipos'].pop()
    origen.write_text(json.dumps(modificado), encoding='utf-8')

    assert main(['restaurar', manifiesto, str(origen), '--confirmar']) == 0
    assert json.loads(origen.read_text(encoding='utf-8')) == original


def test_DAT06_no_purga_copias(tmp_path):
    from prestatec.backup import BackupService

    origen = tmp_path / 'data.json'
    origen.write_text(json.dumps(estado_demo()), encoding='utf-8')
    directorio = tmp_path / 'backups'
    servicio = BackupService()

    creados = [servicio.crear(origen, directorio=directorio) for _ in range(3)]

    archivos = set(directorio.iterdir())
    assert len(archivos) == 6  # tres instantáneas y tres manifiestos
    assert all(os.path.exists(item['archivo']) for item in creados)
    assert len({item['archivo'] for item in creados}) == 3
