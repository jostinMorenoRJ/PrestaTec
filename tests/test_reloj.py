"""C2 — reloj UTC y políticas inyectables (ARC-03, ARC-04).

TDD: creado antes de `prestatec/reloj.py` y `prestatec/politicas.py`.
"""
from datetime import datetime, timedelta, timezone

import pytest

from prestatec.politicas import Politicas
from prestatec.reloj import RelojFalso
from prestatec.service import BusinessError, InventoryService


MOMENTO = datetime(2026, 11, 24, 15, 0, tzinfo=timezone.utc)


def base(tmp_path, **kwargs):
    servicio = InventoryService(tmp_path / 'datos.json', seed=False, **kwargs)
    servicio.registrar_usuario('Ana Torres', '1001', 'Estudiante')
    equipo = servicio.registrar_equipo('Portátil', 'Lenovo ThinkPad', 'Biblioteca')
    return servicio, equipo


def test_ARC03_atraso_determinista_con_reloj_falso(tmp_path):
    servicio, equipo = base(tmp_path, reloj=RelojFalso(MOMENTO))
    prestamo = servicio.crear_prestamo(
        equipo['id'], '1001',
        datetime(2026, 11, 24, 9, 0, tzinfo=timezone.utc),
        datetime(2026, 11, 24, 14, 0, tzinfo=timezone.utc),
    )
    servicio.entregar(prestamo['id'], 'Encargado')

    assert servicio.listar_prestamos()[0]['estado'] == 'Atrasada'


def test_ARC03_misma_franja_en_otra_zona_no_se_solapa(tmp_path):
    servicio, equipo = base(tmp_path, reloj=RelojFalso(MOMENTO))
    servicio.crear_prestamo(
        equipo['id'], '1001',
        datetime(2026, 11, 24, 10, 0, tzinfo=timezone.utc),
        datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc),
    )
    zona_menos_cinco = timezone(timedelta(hours=-5))

    with pytest.raises(BusinessError, match='ocupado|horario'):
        servicio.crear_prestamo(
            equipo['id'], '1001',
            datetime(2026, 11, 24, 5, 0, tzinfo=zona_menos_cinco),
            datetime(2026, 11, 24, 7, 0, tzinfo=zona_menos_cinco),
        )


def test_ARC03_timestamps_se_almacenan_en_utc(tmp_path):
    servicio, _equipo = base(tmp_path, reloj=RelojFalso(MOMENTO))

    assert servicio.data['eventos'][0]['fecha'].endswith('+00:00')


def test_ARC04_politica_sin_valor_no_rechaza_por_duracion(tmp_path):
    servicio, equipo = base(
        tmp_path, reloj=RelojFalso(MOMENTO), politicas=Politicas()
    )

    prestamo = servicio.crear_prestamo(
        equipo['id'], '1001', MOMENTO, MOMENTO + timedelta(days=30)
    )

    assert prestamo['estado'] == 'Confirmada'
