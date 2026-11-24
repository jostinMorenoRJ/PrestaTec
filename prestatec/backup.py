"""Respaldos verificables y restauración exacta (DAT-05, DAT-06).

Cada copia queda descrita por un manifiesto con timestamp UTC, SHA-256 y
conteo de entidades. No existe operación de purga: mientras DEC-06 no defina
una retención, todas las copias se conservan.
"""
import hashlib
import json
import os
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .errors import BusinessError
from .migracion import normalizar
from .repository import estado_vacio
from .sqlite_repository import SQLiteRepository

_SUFFIX_SQLITE = ('.db', '.sqlite', '.sqlite3')


def _digest(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def _estado(ruta):
    """Lee una copia JSON o SQLite y devuelve el estado normalizado."""
    ruta = Path(ruta)
    try:
        if ruta.suffix.lower() in _SUFFIX_SQLITE:
            return SQLiteRepository(ruta).load()
        contenido = json.loads(ruta.read_text(encoding='utf-8'))
        if not isinstance(contenido, dict):
            raise BusinessError('La copia no contiene un objeto JSON.')
        return normalizar(contenido)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, sqlite3.Error) as error:
        raise BusinessError(f'No fue posible leer la copia: {ruta}') from error


def _conteos(estado):
    return {clave: len(valores) for clave, valores in estado.items()}


def _ruta_manifiesto(manifiesto):
    if isinstance(manifiesto, (str, Path)):
        return Path(manifiesto)
    return Path(manifiesto['manifiesto'])


class BackupService:
    """Crea, valida y restaura copias sin eliminar ninguna."""

    def crear(self, ruta, directorio=None, nombre=None):
        ruta = Path(ruta)
        if not ruta.exists():
            raise BusinessError(f'No existe el archivo a respaldar: {ruta}')
        directorio = Path(directorio) if directorio is not None else ruta.parent / 'backups'
        directorio.mkdir(parents=True, exist_ok=True)

        digesto = _digest(ruta)
        creado = datetime.now(timezone.utc)
        sufijo = nombre or (
            f"{ruta.stem}_{creado.strftime('%Y%m%dT%H%M%S%fZ')}_{digesto[:8]}{ruta.suffix}"
        )
        instantanea = directorio / sufijo
        contador = 1
        while instantanea.exists():
            instantanea = directorio / f'{contador:03d}_{sufijo}'
            contador += 1
        shutil.copy2(ruta, instantanea)

        manifiesto = {
            'origen': str(ruta.resolve()),
            'archivo': str(instantanea.resolve()),
            'creadoEn': creado.isoformat(),
            'sha256': digesto,
            'conteos': _conteos(_estado(instantanea)),
            'tamanio': instantanea.stat().st_size,
            'backend': 'sqlite' if ruta.suffix.lower() in _SUFFIX_SQLITE else 'json',
        }
        ruta_manifiesto = instantanea.with_name(instantanea.name + '.manifest.json')
        ruta_manifiesto.write_text(
            json.dumps(manifiesto, ensure_ascii=False, indent=2, default=str),
            encoding='utf-8',
        )
        manifiesto['manifiesto'] = str(ruta_manifiesto.resolve())
        return manifiesto

    def validar(self, manifiesto):
        manifiesto = self._cargar(manifiesto)
        instantanea = Path(manifiesto['archivo'])
        if not instantanea.exists():
            raise BusinessError(f"No existe la copia: {instantanea}")
        if _digest(instantanea) != manifiesto['sha256']:
            raise BusinessError('La copia no supera la verificación SHA-256.')
        conteos = _conteos(_estado(instantanea))
        if conteos != manifiesto['conteos']:
            raise BusinessError(
                f"Los conteos de la copia no coinciden: {conteos} != {manifiesto['conteos']}"
            )
        return True

    def restaurar(self, manifiesto, destino, confirmar=False):
        self.validar(manifiesto)
        manifiesto = self._cargar(manifiesto)
        destino = Path(destino)
        destino.parent.mkdir(parents=True, exist_ok=True)

        if destino.exists() and not confirmar:
            creado = datetime.fromisoformat(manifiesto['creadoEn'])
            modificado = datetime.fromtimestamp(destino.stat().st_mtime, timezone.utc)
            if modificado > creado:
                raise BusinessError(
                    'El destino es más reciente que la copia; se requiere confirmación explícita.'
                )

        temporal = destino.with_name(destino.name + '.restore.tmp')
        shutil.copy2(manifiesto['archivo'], temporal)
        os.replace(temporal, destino)

        if _conteos(_estado(destino)) != manifiesto['conteos']:
            raise BusinessError('La restauración no reprodujo los conteos de la copia.')
        return manifiesto

    def _cargar(self, manifiesto):
        if isinstance(manifiesto, dict):
            return manifiesto
        ruta = _ruta_manifiesto(manifiesto)
        try:
            datos = json.loads(ruta.read_text(encoding='utf-8'))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise BusinessError(f'No fue posible leer el manifiesto: {ruta}') from error
        if not isinstance(datos, dict) or 'sha256' not in datos:
            raise BusinessError(f'Manifiesto inválido: {ruta}')
        return datos
