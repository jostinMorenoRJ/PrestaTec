from datetime import datetime, timedelta
import json
from prestatec.web import PrestaTecApp


def call(app, method, path, body=None):
    status, content, mime, filename = app.dispatch(method, path, body)
    return status, json.loads(content) if mime.startswith('application/json') else content


def test_api_registra_y_consulta_equipo(tmp_path):
    app=PrestaTecApp(tmp_path/'db.json',seed=False)
    status, equipo=call(app,'POST','/api/equipos',{'tipo':'Portátil','nombre':'ASUS VivoBook','ubicacion':'Biblioteca'})
    assert status==200 and equipo['id']=='PT-001'
    assert call(app,'GET','/api/equipos')[1][0]['estado']=='Disponible'


def test_api_rechaza_documento_repetido(tmp_path):
    app=PrestaTecApp(tmp_path/'db.json',seed=False)
    body={'nombre':'Daniel Rojas','documento':'12345','rol':'Estudiante'}
    assert call(app,'POST','/api/usuarios',body)[0]==200
    status,error=call(app,'POST','/api/usuarios',body)
    assert status==400 and 'documento' in error['mensaje']


def test_api_ciclo_prestamo_devolucion(tmp_path):
    app=PrestaTecApp(tmp_path/'db.json',seed=False)
    call(app,'POST','/api/usuarios',{'nombre':'Daniel Rojas','documento':'12345','rol':'Estudiante'})
    equipo=call(app,'POST','/api/equipos',{'tipo':'Proyector','nombre':'Epson','ubicacion':'Sala 1'})[1]
    inicio=(datetime.now()-timedelta(minutes=1)).isoformat(); fin=(datetime.now()+timedelta(hours=1)).isoformat()
    reserva=call(app,'POST','/api/reservas',{'equipoId':equipo['id'],'documento':'12345','inicio':inicio,'fin':fin})[1]
    assert call(app,'POST',f"/api/reservas/{reserva['id']}/entregar",{'responsable':'Auxiliar'})[0]==200
    assert call(app,'GET','/api/equipos')[1][0]['estado']=='Prestado'
    assert call(app,'POST',f"/api/reservas/{reserva['id']}/devolver",{'danio':False,'nota':''})[0]==200
    assert call(app,'GET','/api/equipos')[1][0]['estado']=='Disponible'
