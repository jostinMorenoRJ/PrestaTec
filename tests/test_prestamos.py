"""Pruebas de aceptación del dominio PrestaTec (TDD: Red -> Green -> Refactor)."""
from datetime import datetime, timedelta
import pytest

from prestatec.service import InventoryService, BusinessError


@pytest.fixture
def sistema(tmp_path):
    return InventoryService(tmp_path / "datos.json", seed=False)


def registrar_base(sistema):
    usuario = sistema.registrar_usuario("María Pérez", "100200300", "Estudiante")
    equipo = sistema.registrar_equipo("Portátil", "Lenovo ThinkPad", "Biblioteca")
    return usuario, equipo


def test_registrar_estudiante_y_rechazar_documento_duplicado(sistema):
    usuario = sistema.registrar_usuario("María Pérez", "100200300", "Estudiante")
    assert usuario["nombre"] == "María Pérez"
    with pytest.raises(BusinessError, match="documento"):
        sistema.registrar_usuario("Otra persona", "100200300", "Estudiante")


def test_registrar_equipo_con_codigo_unico(sistema):
    primero = sistema.registrar_equipo("Portátil", "Lenovo", "Biblioteca")
    segundo = sistema.registrar_equipo("Proyector", "Epson", "Sala 2")
    assert primero["id"] == "PT-001"
    assert segundo["id"] == "PR-001"


def test_prestar_y_devolver_equipo_actualiza_disponibilidad(sistema):
    usuario, equipo = registrar_base(sistema)
    inicio = datetime.now() - timedelta(minutes=1)
    fin = datetime.now() + timedelta(hours=2)
    prestamo = sistema.crear_prestamo(equipo["id"], usuario["documento"], inicio, fin)
    sistema.entregar(prestamo["id"], "Laura encargada", "Bueno")
    assert sistema.listar_equipos()[0]["estado"] == "Prestado"
    sistema.devolver(prestamo["id"], False, "")
    assert sistema.obtener_equipo(equipo["id"])["estado"] == "Disponible"


def test_no_permite_prestar_equipo_ya_prestado(sistema):
    usuario, equipo = registrar_base(sistema)
    inicio = datetime.now() - timedelta(minutes=1)
    fin = datetime.now() + timedelta(hours=2)
    p = sistema.crear_prestamo(equipo["id"], usuario["documento"], inicio, fin)
    sistema.entregar(p["id"], "Encargada", "Bueno")
    with pytest.raises(BusinessError, match="ocupado|disponible|horario"):
        sistema.crear_prestamo(equipo["id"], usuario["documento"], inicio, fin)


def test_no_permite_reservas_duplicadas_en_mismo_horario(sistema):
    usuario, equipo = registrar_base(sistema)
    inicio = datetime.now() + timedelta(hours=1)
    fin = inicio + timedelta(hours=2)
    sistema.crear_prestamo(equipo["id"], usuario["documento"], inicio, fin)
    with pytest.raises(BusinessError, match="horario"):
        sistema.crear_prestamo(equipo["id"], usuario["documento"], inicio, fin)


def test_equipo_danado_pasa_a_mantenimiento_y_no_se_presta(sistema):
    usuario, equipo = registrar_base(sistema)
    inicio = datetime.now() - timedelta(minutes=1)
    fin = datetime.now() + timedelta(hours=2)
    p = sistema.crear_prestamo(equipo["id"], usuario["documento"], inicio, fin)
    sistema.entregar(p["id"], "Encargada", "Bueno")
    sistema.devolver(p["id"], True, "Pantalla rota")
    assert sistema.obtener_equipo(equipo["id"])["estado"] == "Mantenimiento"
    with pytest.raises(BusinessError, match="Mantenimiento"):
        sistema.crear_prestamo(equipo["id"], usuario["documento"], inicio, fin)


def test_porteria_autoriza_estudiante_con_equipo_a_cargo(sistema):
    usuario, equipo = registrar_base(sistema)
    inicio = datetime.now() - timedelta(minutes=1)
    fin = datetime.now() + timedelta(hours=2)
    p = sistema.crear_prestamo(equipo["id"], usuario["documento"], inicio, fin)
    sistema.entregar(p["id"], "Encargada", "Bueno")
    resultado = sistema.verificar_porteria(usuario["documento"])
    assert resultado["ok"] is True
    assert equipo["id"] in " ".join(resultado["detalle"])


def test_datos_persisten_al_reiniciar_servicio(tmp_path):
    ruta = tmp_path / "datos.json"
    sistema = InventoryService(ruta, seed=False)
    sistema.registrar_usuario("María Pérez", "100200300", "Estudiante")
    recargado = InventoryService(ruta, seed=False)
    assert len(recargado.listar_usuarios()) == 1


def test_importa_datos_del_proyecto_base_en_formato_csharp(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text('{"Equipos":[{"Id":"PT-009","Tipo":"Portátil","Nombre":"Equipo legado","Ubicacion":"Biblioteca","Estado":"Disponible"}],"Usuarios":[],"Reservas":[],"Eventos":[]}', encoding="utf-8")
    sistema = InventoryService(ruta, seed=False)
    assert sistema.listar_equipos()[0]["id"] == "PT-009"
    assert sistema.listar_equipos()[0]["nombre"] == "Equipo legado"
