"""Identidad, sesiones y autorización (SEC-01..SEC-04).

El proveedor local es temporal e intercambiable: el dominio y los casos de uso
solo conocen ``Identidad`` y ``Autorizador``. Las credenciales se guardan en un
archivo distinto de `data.json`, con PBKDF2 y salt por usuario; nunca se
almacena texto plano ni secretos en el repositorio.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from .errors import BusinessError

ROOT = Path(__file__).resolve().parent.parent

# C12: solo tres roles operativos. Los alias históricos Estudiante/Docente se
# traducen a Consulta; Administrador y Soporte dejan de ser válidos.
ROLES_PERMITIDOS = ('Consulta', 'Guarda', 'Encargado')
ROLES_LEGACY = {
    'Estudiante': 'Consulta',
    'Docente': 'Consulta',
    'Consulta': 'Consulta',
    'Guarda': 'Guarda',
    'Encargado': 'Encargado',
}
VISTAS_INICIALES = {
    'Consulta': 'mis',
    'Guarda': 'porteria',
    'Encargado': 'gestion',
}

MATRIZ = {
    'SOLICITAR_PRESTAMO': {'Consulta'},
    'VERIFICAR_PORTERIA': {'Guarda', 'Encargado'},
    'ENTREGAR_DEVOLVER': {'Guarda', 'Encargado'},
    'CREAR_RECURSO': {'Encargado'},
    'REGISTRAR_DANO': {'Encargado'},
    'HABILITAR': {'Encargado'},
    'EXPORTAR': {'Encargado', 'Consulta'},
    'CONSULTAR_HISTORIAL': {'Encargado', 'Consulta'},
    'VER_RESUMEN': {'Guarda', 'Encargado'},
    'VER_USUARIOS': {'Encargado'},
}


def normalizar_rol(rol):
    """Devuelve el rol permitido o `None` si no pertenece a la matriz C12."""
    texto = str(rol or '').strip()
    if not texto:
        return None
    return ROLES_LEGACY.get(texto, texto if texto in ROLES_PERMITIDOS else None)



class NoAutenticado(BusinessError):
    """La petición no tiene una identidad válida."""


class SinPermiso(BusinessError):
    """La identidad no tiene el permiso requerido."""


@dataclass(frozen=True)
class Identidad:
    id: str
    nombre: str
    rol: str
    documento: str = ''


class Autorizador:
    """Matriz central de permisos; se configura, no se reescribe."""

    def __init__(self, matriz=None):
        self.matriz = dict(matriz or MATRIZ)

    def puede(self, identidad, accion):
        return bool(identidad) and identidad.rol in self.matriz.get(accion, set())

    def exigir(self, identidad, accion):
        if not self.puede(identidad, accion):
            raise SinPermiso(f'Sin permiso para: {accion}.')
        return identidad


@runtime_checkable
class ProveedorIdentidad(Protocol):
    """Contrato mínimo para proveedores locales o institucionales."""

    def autenticar(self, documento, contraseña) -> str | None:
        """Devuelve un token de sesión o `None` si falla."""

    def resolver(self, headers) -> Identidad | None:
        """Resuelve la identidad de una petición."""


class AlmacenCredenciales:
    """Credenciales con hash PBKDF2; separadas del repositorio de negocio."""

    def __init__(self, ruta=None, iteraciones=210000):
        self.ruta = Path(ruta or os.getenv('PRESTATEC_IDENTITY_FILE') or ROOT / 'identidades.json')
        self.iteraciones = iteraciones
        self.ruta.parent.mkdir(parents=True, exist_ok=True)

    def _leer(self):
        if not self.ruta.exists():
            return {'credenciales': {}}
        try:
            datos = json.loads(self.ruta.read_text(encoding='utf-8'))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise BusinessError('No fue posible leer las credenciales.') from error
        datos.setdefault('credenciales', {})
        return datos

    def _guardar(self, datos):
        self.ruta.write_text(
            json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8'
        )

    def crear(self, documento, contraseña, rol=None):
        documento, contraseña = str(documento or '').strip(), str(contraseña or '')
        if not documento or not contraseña:
            raise BusinessError('Documento y contraseña son obligatorios.')
        rol = normalizar_rol(rol)
        if rol is None:
            raise BusinessError(
                f'Rol no válido. Roles permitidos: {", ".join(ROLES_PERMITIDOS)}.'
            )
        datos = self._leer()
        if documento in datos['credenciales']:
            raise BusinessError(f'Ya existe una credencial para: {documento}.')
        sal = os.urandom(16)
        digesto = hashlib.pbkdf2_hmac(
            'sha256', contraseña.encode('utf-8'), sal, self.iteraciones
        )
        datos['credenciales'][documento] = {
            'salt': sal.hex(),
            'hash': digesto.hex(),
            'iteraciones': self.iteraciones,
            'rol': rol,
        }
        self._guardar(datos)
        return documento

    def verificar(self, documento, contraseña):
        credencial = self._leer()['credenciales'].get(str(documento or '').strip())
        if not credencial:
            return False
        digesto = hashlib.pbkdf2_hmac(
            'sha256', str(contraseña or '').encode('utf-8'),
            bytes.fromhex(credencial['salt']), credencial['iteraciones'],
        )
        return hmac.compare_digest(digesto.hex(), credencial['hash'])

    def rol(self, documento):
        credencial = self._leer()['credenciales'].get(str(documento or '').strip())
        return credencial.get('rol') if credencial else None


class ProveedorIdentidadLocal:
    """Proveedor local con sesiones firmadas; sustituible por SSO."""

    def __init__(self, servicio, ruta=None, secreto=None):
        self.servicio = servicio
        self.almacen = AlmacenCredenciales(ruta)
        self.secreto = secreto or os.getenv('PRESTATEC_SESSION_SECRET') or secrets.token_hex(32)

    def crear_credencial(self, documento, contraseña, rol=None):
        if rol is None:
            # C5: si no se da rol explícito se toma del usuario de negocio (PER-01).
            documento_texto = str(documento or '').strip()
            usuario = next(
                (u for u in self.servicio.listar_usuarios()
                 if u['documento'] == documento_texto), None
            )
            if usuario is None:
                raise BusinessError(
                    'Rol obligatorio si el documento no está registrado. '
                    f'Roles permitidos: {", ".join(ROLES_PERMITIDOS)}.'
                )
            rol = usuario['rol']
        return self.almacen.crear(documento, contraseña, rol)

    def autenticar(self, documento, contraseña):
        if not self.almacen.verificar(documento, contraseña):
            return None
        if self.identidad(documento) is None:
            return None
        return self._emitir(str(documento).strip())

    def resolver(self, headers):
        token = self._token(headers)
        if not token:
            return None
        documento = self._validar(token)
        if documento is None:
            return None
        return self.identidad(documento)

    def identidad(self, documento):
        documento = str(documento or '').strip()
        usuario = next(
            (u for u in self.servicio.listar_usuarios() if u['documento'] == documento), None
        )
        rol = normalizar_rol(self.almacen.rol(documento))
        if rol:
            return Identidad(
                usuario['id'] if usuario else f'ID-{documento}',
                usuario['nombre'] if usuario else documento,
                rol, documento,
            )
        if self.almacen.rol(documento):
            return None  # credencial con rol eliminado: no resuelve identidad
        if usuario:
            rol = normalizar_rol(usuario['rol']) or 'Consulta'
            return Identidad(usuario['id'], usuario['nombre'], rol, documento)
        return None

    def _emitir(self, documento):
        cuerpo = f'{documento}|{int(time.time()) + 8 * 3600}'
        firma = hmac.new(
            self.secreto.encode('utf-8'), cuerpo.encode('utf-8'), hashlib.sha256
        ).hexdigest()[:24]
        return base64.urlsafe_b64encode(f'{cuerpo}|{firma}'.encode('utf-8')).decode().rstrip('=')

    def _validar(self, token):
        try:
            relleno = '=' * (-len(token) % 4)
            texto = base64.urlsafe_b64decode(token + relleno).decode('utf-8')
            documento, vencimiento, firma = texto.split('|', 2)
            esperada = hmac.new(
                self.secreto.encode('utf-8'),
                f'{documento}|{vencimiento}'.encode('utf-8'), hashlib.sha256,
            ).hexdigest()[:24]
            if not hmac.compare_digest(firma, esperada) or int(vencimiento) < time.time():
                return None
            return documento
        except (ValueError, UnicodeDecodeError):
            return None

    @staticmethod
    def _token(headers):
        if not headers:
            return None
        cabecera = headers.get('Cookie') or headers.get('cookie') or ''
        for parte in str(cabecera).split(';'):
            nombre, _, valor = parte.strip().partition('=')
            if nombre == 'prestatec_session':
                return valor
        autorizacion = headers.get('Authorization') or headers.get('authorization') or ''
        if str(autorizacion).lower().startswith('bearer '):
            return str(autorizacion)[7:].strip()
        return None
