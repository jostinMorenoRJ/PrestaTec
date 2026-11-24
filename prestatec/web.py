"""Enrutador HTTP pequeño construido con la biblioteca estándar de Python."""
import csv
import io
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .config import Configuracion
from .errors import BusinessError
from .identidad import (
    Autorizador, NoAutenticado, ProveedorIdentidadLocal, SinPermiso,
)
from .service import InventoryService

ROOT = Path(__file__).resolve().parent.parent


class PrestaTecApp:
    def __init__(self, data_file=None, seed=True, configuracion=None, identidad=None,
                 autorizador=None, identidad_file=None):
        configuracion = configuracion or Configuracion(ruta_datos=data_file)
        self.service = InventoryService(repository=configuracion.repositorio(), seed=seed)
        self.identidad = identidad or ProveedorIdentidadLocal(self.service, identidad_file)
        self.autorizador = autorizador or Autorizador()
        self.ultimos_headers = {}

    def dispatch(self, method, target, body=None, headers=None):
        """Devuelve (status, contenido, tipo_mime, nombre_archivo).

        Las cabeceras de respuesta que deba enviar el servidor quedan en
        ``self.ultimos_headers`` para no romper la firma existente.
        """
        self.ultimos_headers = {}
        parsed = urlparse(target)
        path = unquote(parsed.path)
        body = body or {}
        headers = headers or {}
        s = self.service
        try:
            if method == 'POST' and path == '/api/auth/login':
                token = self.identidad.autenticar(body.get('documento'), body.get('contraseña'))
                if not token:
                    return self._json({'mensaje': 'Credenciales inválidas.'}, 401)
                self.ultimos_headers['Set-Cookie'] = (
                    f'prestatec_session={token}; HttpOnly; SameSite=Lax; Path=/'
                )
                return self._json({'token': token})

            if path.startswith('/api/'):
                actor = self.identidad.resolver(headers)
                if actor is None:
                    return self._json({'mensaje': 'Autenticación requerida.'}, 401)
            else:
                actor = None

            if method == 'POST' and path == '/api/auth/logout':
                self.ultimos_headers['Set-Cookie'] = (
                    'prestatec_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0'
                )
                return self._json({'ok': True})
            if method == 'GET' and path == '/api/auth/me':
                permisos = sorted(
                    accion for accion, roles in self.autorizador.matriz.items()
                    if actor.rol in roles
                )
                return self._json({
                    'id': actor.id, 'nombre': actor.nombre, 'rol': actor.rol,
                    'documento': actor.documento, 'permisos': permisos,
                })
            if method == 'GET' and path == '/api/resumen':
                return self._json(s.resumen())
            if method == 'GET' and path == '/api/equipos':
                return self._json(s.listar_equipos())
            if method == 'POST' and path == '/api/equipos':
                self.autorizador.exigir(actor, 'CREAR_RECURSO')
                return self._json(s.registrar_equipo(
                    body.get('tipo'), body.get('nombre'), body.get('ubicacion'), actor=actor
                ))
            m = re.fullmatch(r'/api/equipos/([^/]+)/estado', path)
            if m and method == 'PUT':
                accion = 'HABILITAR' if body.get('estado') == 'Disponible' else 'REGISTRAR_DANO'
                self.autorizador.exigir(actor, accion)
                return self._json(s.cambiar_estado(
                    m.group(1), body.get('estado'), body.get('nota', ''), actor=actor
                ))
            m = re.fullmatch(r'/api/equipos/([^/]+)/historial', path)
            if m and method == 'GET':
                self.autorizador.exigir(actor, 'CONSULTAR_HISTORIAL')
                return self._json(s.historial_equipo(m.group(1)))
            if method == 'GET' and path == '/api/usuarios':
                return self._json(s.listar_usuarios())
            if method == 'POST' and path == '/api/usuarios':
                self.autorizador.exigir(actor, 'CREAR_RECURSO')
                return self._json(s.registrar_usuario(
                    body.get('nombre'), body.get('documento'), body.get('rol', 'Estudiante'),
                    actor=actor,
                ))
            if method == 'GET' and path == '/api/disponibilidad':
                q = parse_qs(parsed.query)
                return self._json(s.disponibilidad(
                    q.get('tipo', ['Portátil'])[0], q['inicio'][0], q['fin'][0]
                ))
            if method == 'GET' and path == '/api/reservas':
                return self._json(s.listar_prestamos())
            if method == 'POST' and path == '/api/reservas':
                return self._json(s.crear_prestamo(
                    body.get('equipoId'), body.get('documento'),
                    body.get('inicio'), body.get('fin'), actor=actor,
                ))
            m = re.fullmatch(r'/api/reservas/([^/]+)/(entregar|devolver|cancelar|noshow)', path)
            if m and method == 'POST':
                pid, accion = m.groups()
                self.autorizador.exigir(actor, 'ENTREGAR_DEVOLVER')
                if accion == 'devolver' and body.get('danio'):
                    self.autorizador.exigir(actor, 'REGISTRAR_DANO')
                if accion == 'entregar':
                    result = s.entregar(
                        pid, body.get('responsable'), body.get('estadoEntrega', 'Bueno'),
                        actor=actor,
                    )
                elif accion == 'devolver':
                    result = s.devolver(
                        pid, body.get('danio', False), body.get('nota', ''), actor=actor
                    )
                elif accion == 'cancelar':
                    result = s.cancelar(pid, 'Cancelada', actor=actor)
                else:
                    result = s.cancelar(pid, 'No se presentó', actor=actor)
                return self._json(result)
            m = re.fullmatch(r'/api/porteria/(.+)', path)
            if m and method == 'GET':
                self.autorizador.exigir(actor, 'VERIFICAR_PORTERIA')
                return self._json(s.verificar_porteria(m.group(1), actor=actor))
            if method == 'GET' and path == '/api/reportes/csv':
                self.autorizador.exigir(actor, 'EXPORTAR')
                out = io.StringIO()
                writer = csv.writer(out)
                writer.writerow([
                    'Préstamo', 'Equipo', 'Usuario', 'Inicio', 'Fin', 'Estado',
                    'Entregado', 'Devuelto', 'Responsable', 'Nota',
                ])
                for p in s.listar_prestamos():
                    writer.writerow([
                        p['id'], p['equipoId'], p['usuario'], p['inicio'], p['fin'],
                        p['estado'], p['entregadoEn'], p['devueltoEn'],
                        p['responsable'], p['nota'],
                    ])
                return 200, ('\ufeff' + out.getvalue()).encode('utf-8'), \
                    'text/csv; charset=utf-8', 'reporte_prestamos.csv'
            if method == 'GET' and path in ('/', '/static/index.html', '/static/styles.css', '/static/app.js'):
                name = 'index.html' if path == '/' else path.rsplit('/', 1)[1]
                mime = {
                    'html': 'text/html; charset=utf-8',
                    'css': 'text/css; charset=utf-8',
                    'js': 'application/javascript; charset=utf-8',
                }[name.rsplit('.', 1)[1]]
                return 200, (ROOT / 'static' / name).read_bytes(), mime, None
            return self._json({'mensaje': 'Recurso no encontrado.'}, 404)
        except NoAutenticado as error:
            return self._json({'mensaje': str(error)}, 401)
        except SinPermiso as error:
            return self._json({'mensaje': str(error)}, 403)
        except BusinessError as error:
            return self._json({'mensaje': str(error)}, 400)
        except (KeyError, TypeError, ValueError) as error:
            return self._json({'mensaje': f'Datos incompletos o inválidos: {error}'}, 400)

    @staticmethod
    def _json(data, status=200):
        return status, json.dumps(data, ensure_ascii=False).encode('utf-8'), \
            'application/json; charset=utf-8', None
