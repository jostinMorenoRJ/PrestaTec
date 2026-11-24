"""SEC-02: permisos comprobados también en los casos de uso.

Creado antes de inyectar `Autorizador` en `InventoryService`; su fallo documenta
la fase RED de esta parte del change C5.
"""
from datetime import datetime, timedelta

import pytest

from prestatec.identidad import Identidad, SinPermiso
from prestatec.service import InventoryService


def identidad(identificador, nombre, rol):
    return Identidad(identificador, nombre, rol, identificador)


def test_caso_uso_rechaza_registro_de_usuario_sin_permiso(tmp_path):
    servicio = InventoryService(tmp_path / 'db.json', seed=False)
    guarda = identidad('ID-G', 'Guarda Uno', 'Guarda')

    with pytest.raises(SinPermiso, match='CREAR_RECURSO'):
        servicio.registrar_usuario('Ana Torres', '1001', 'Estudiante', actor=guarda)

    assert servicio.listar_usuarios() == []


def test_caso_uso_admin_registra_y_encargado_entrega(tmp_path):
    servicio = InventoryService(tmp_path / 'db.json', seed=False)
    admin = identidad('ID-A', 'Administrador', 'Administrador')
    encargado = identidad('ID-E', 'Laura Gómez', 'Encargado')

    servicio.registrar_usuario('Laura Gómez', '1002', 'Encargado', actor=admin)
    equipo = servicio.registrar_equipo('Portátil', 'ThinkPad', actor=admin)
    inicio = (datetime.now() - timedelta(minutes=1)).isoformat()
    fin = (datetime.now() + timedelta(hours=1)).isoformat()
    reserva = servicio.crear_prestamo(equipo['id'], '1002', inicio, fin, actor=admin)

    entregado = servicio.entregar(reserva['id'], 'Auxiliar', actor=encargado)
    assert entregado['actorId'] == 'ID-E'
    assert any(
        'Laura Gómez' in evento['texto']
        for evento in servicio.historial_equipo(equipo['id'])
    )
    servicio.devolver(reserva['id'], actor=encargado)


def test_caso_uso_guarda_no_cambia_estado(tmp_path):
    servicio = InventoryService(tmp_path / 'db.json', seed=False)
    admin = identidad('ID-A', 'Administrador', 'Administrador')
    guarda = identidad('ID-G', 'Guarda Uno', 'Guarda')
    equipo = servicio.registrar_equipo('Portátil', 'ThinkPad', actor=admin)

    with pytest.raises(SinPermiso, match='REGISTRAR_DANO'):
        servicio.cambiar_estado(
            equipo['id'], 'Mantenimiento', 'Revisar', actor=guarda
        )

    assert servicio.obtener_equipo(equipo['id'])['estado'] == 'Disponible'
