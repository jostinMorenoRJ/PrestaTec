"""Migración segura de ``data.json`` a SQLite (DAT-02, DAT-04).

La copia de respaldo se crea antes de escribir cualquier destino. La migración
conserva registros en formato legacy (PascalCase) y en formato actual
(minúsculas) cuando ambas claves coexisten, corrigiendo el defecto P9 sin
modificar el comportamiento del adaptador JSON original.
"""
import hashlib
import json
import os
import shutil
from pathlib import Path

from .errors import BusinessError
from .repository import estado_vacio
from .sqlite_repository import SCHEMA_VERSION, SQLiteRepository

_EQUIVALENCIAS = {
    'equipos': {
        'id': ('id', 'Id'), 'tipo': ('tipo', 'Tipo'),
        'nombre': ('nombre', 'Nombre'), 'ubicacion': ('ubicacion', 'Ubicacion'),
        'estado': ('estado', 'Estado'),
    },
    'usuarios': {
        'id': ('id', 'Id'), 'nombre': ('nombre', 'Nombre'),
        'documento': ('documento', 'Documento'), 'rol': ('rol', 'Rol'),
    },
    'prestamos': {
        'id': ('id', 'Id'), 'equipoId': ('equipoId', 'EquipoId'),
        'usuarioId': ('usuarioId', 'UsuarioId'), 'inicio': ('inicio', 'Inicio'),
        'fin': ('fin', 'Fin'), 'estado': ('estado', 'Estado'),
        'entregadoEn': ('entregadoEn', 'EntregadoEn'),
        'devueltoEn': ('devueltoEn', 'DevueltoEn'),
        'responsable': ('responsable', 'Responsable'), 'nota': ('nota', 'Nota'),
    },
    'eventos': {
        'fecha': ('fecha', 'Fecha'), 'equipoId': ('equipoId', 'EquipoId'),
        'texto': ('texto', 'Texto'),
    },
}

_CLAVES_LEGACY = {
    'equipos': 'Equipos', 'usuarios': 'Usuarios',
    'prestamos': 'Reservas', 'eventos': 'Eventos',
}


def _valor(fila, nombres, defecto=None):
    for nombre in nombres:
        if nombre in fila and fila[nombre] is not None:
            return fila[nombre]
    return defecto


def _convertir(clave, fila):
    if not isinstance(fila, dict):
        return None
    return {
        destino: _valor(fila, nombres, '' if destino != 'nota' else '')
        for destino, nombres in _EQUIVALENCIAS[clave].items()
    }


def normalizar(datos):
    """Combina las claves legacy y actuales en un único estado interno."""
    estado = estado_vacio()
    for clave, plantilla in _EQUIVALENCIAS.items():
        actual, legacy = clave, _CLAVES_LEGACY[clave]
        filas = []
        for origen in (legacy, actual):
            for fila in datos.get(origen, []) or []:
                convertida = _convertir(clave, fila)
                if convertida is not None:
                    filas.append(convertida)
        unicas = {}
        for fila in filas:
            identificador = fila.get('id') or (
                fila.get('fecha'), fila.get('equipoId'), fila.get('texto')
            )
            unicas[identificador] = fila  # la clave actual prevalece sobre la legacy
        estado[clave] = list(unicas.values())
    return estado


def migrar_desde_json(origen, destino, respaldo=None, sobrescribir=False):
    """Migra `origen` a `destino` y devuelve un informe verificable.

    El archivo original no se modifica. Si la escritura falla, el destino no
    se reemplaza: se conserva el archivo SQLite temporal para diagnóstico.
    Requiere autorización explícita para reemplazar archivos ya existentes.
    """
    origen, destino = Path(origen), Path(destino)
    respaldo = Path(respaldo) if respaldo is not None else origen.with_suffix('.json.bak')
    if not origen.exists():
        raise BusinessError(f'No existe el archivo de origen: {origen}')
    for ruta, nombre in ((destino, 'destino'), (respaldo, 'respaldo')):
        if ruta.exists() and not sobrescribir:
            raise BusinessError(f'El {nombre} ya existe: {ruta}. No se sobrescribirá sin autorización.')

    contenido = origen.read_bytes()
    sha = hashlib.sha256(contenido).hexdigest()
    respaldo.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origen, respaldo)

    try:
        datos = json.loads(contenido.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BusinessError('El archivo de origen no contiene JSON válido.') from error
    if not isinstance(datos, dict):
        raise BusinessError('El archivo de origen debe contener un objeto JSON.')

    estado = normalizar(datos)
    temporal = destino.with_name(destino.name + '.tmp')
    if temporal.exists():
        temporal.unlink()
    SQLiteRepository(temporal).save(estado)
    os.replace(temporal, destino)

    return {
        'origen': str(origen),
        'destino': str(destino),
        'respaldo': {'ruta': str(respaldo), 'sha256': sha},
        'schema_version': SCHEMA_VERSION,
        'registros': {clave: len(valores) for clave, valores in estado.items()},
    }
