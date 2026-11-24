"""Enrutador HTTP pequeño construido con la biblioteca estándar de Python."""
import csv
import io
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from .service import InventoryService, BusinessError

ROOT = Path(__file__).resolve().parent.parent

class PrestaTecApp:
    def __init__(self, data_file=None, seed=True):
        self.service = InventoryService(data_file or ROOT / 'data.json', seed=seed)

    def dispatch(self, method, target, body=None):
        """Devuelve (status, contenido, tipo_mime, nombre_archivo)."""
        parsed = urlparse(target); path = unquote(parsed.path); body = body or {}
        s = self.service
        try:
            if method == 'GET' and path == '/api/resumen': return self._json(s.resumen())
            if method == 'GET' and path == '/api/equipos': return self._json(s.listar_equipos())
            if method == 'POST' and path == '/api/equipos': return self._json(s.registrar_equipo(body.get('tipo'),body.get('nombre'),body.get('ubicacion')))
            m = re.fullmatch(r'/api/equipos/([^/]+)/estado',path)
            if m and method == 'PUT': return self._json(s.cambiar_estado(m.group(1),body.get('estado'),body.get('nota','')))
            m = re.fullmatch(r'/api/equipos/([^/]+)/historial',path)
            if m and method == 'GET': return self._json(s.historial_equipo(m.group(1)))
            if method == 'GET' and path == '/api/usuarios': return self._json(s.listar_usuarios())
            if method == 'POST' and path == '/api/usuarios': return self._json(s.registrar_usuario(body.get('nombre'),body.get('documento'),body.get('rol','Estudiante')))
            if method == 'GET' and path == '/api/disponibilidad':
                q=parse_qs(parsed.query); return self._json(s.disponibilidad(q.get('tipo',['Portátil'])[0],q['inicio'][0],q['fin'][0]))
            if method == 'GET' and path == '/api/reservas': return self._json(s.listar_prestamos())
            if method == 'POST' and path == '/api/reservas': return self._json(s.crear_prestamo(body.get('equipoId'),body.get('documento'),body.get('inicio'),body.get('fin')))
            m = re.fullmatch(r'/api/reservas/([^/]+)/(entregar|devolver|cancelar|noshow)',path)
            if m and method == 'POST':
                pid, accion=m.groups()
                if accion=='entregar': result=s.entregar(pid,body.get('responsable'),body.get('estadoEntrega','Bueno'))
                elif accion=='devolver': result=s.devolver(pid,body.get('danio',False),body.get('nota',''))
                elif accion=='cancelar': result=s.cancelar(pid,'Cancelada')
                else: result=s.cancelar(pid,'No se presentó')
                return self._json(result)
            m = re.fullmatch(r'/api/porteria/(.+)',path)
            if m and method == 'GET': return self._json(s.verificar_porteria(m.group(1)))
            if method == 'GET' and path == '/api/reportes/csv':
                out=io.StringIO(); writer=csv.writer(out)
                writer.writerow(['Préstamo','Equipo','Usuario','Inicio','Fin','Estado','Entregado','Devuelto','Responsable','Nota'])
                for p in s.listar_prestamos(): writer.writerow([p['id'],p['equipoId'],p['usuario'],p['inicio'],p['fin'],p['estado'],p['entregadoEn'],p['devueltoEn'],p['responsable'],p['nota']])
                return 200, ('\ufeff'+out.getvalue()).encode('utf-8'), 'text/csv; charset=utf-8', 'reporte_prestamos.csv'
            if method == 'GET' and path in ('/','/static/index.html','/static/styles.css','/static/app.js'):
                name='index.html' if path=='/' else path.rsplit('/',1)[1]
                mime={'html':'text/html; charset=utf-8','css':'text/css; charset=utf-8','js':'application/javascript; charset=utf-8'}[name.rsplit('.',1)[1]]
                return 200,(ROOT/'static'/name).read_bytes(),mime,None
            return self._json({'mensaje':'Recurso no encontrado.'},404)
        except BusinessError as error:
            return self._json({'mensaje':str(error)},400)
        except (KeyError, TypeError, ValueError) as error:
            return self._json({'mensaje':f'Datos incompletos o inválidos: {error}'},400)

    @staticmethod
    def _json(data, status=200):
        return status,json.dumps(data,ensure_ascii=False).encode('utf-8'),'application/json; charset=utf-8',None
