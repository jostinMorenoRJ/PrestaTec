"""Configuración del backend de persistencia (DAT-04).

El dominio no cambia al conmutar entre JSON y SQLite: solo se sustituye el
repositorio inyectado. Las variables de entorno permiten el flag de transición
sin editar código; los valores explícitos tienen prioridad sobre el entorno.
"""
import os
from pathlib import Path

from .errors import BusinessError
from .repository import JsonFileRepository
from .sqlite_repository import SQLiteRepository

ROOT = Path(__file__).resolve().parent.parent


class Configuracion:
    def __init__(self, backend=None, ruta_datos=None):
        self.backend = (backend or os.getenv('PRESTATEC_BACKEND', 'json')).strip().lower()
        if self.backend not in ('json', 'sqlite'):
            raise BusinessError("Backend no válido; use 'json' o 'sqlite'.")
        self.ruta_datos = Path(ruta_datos or os.getenv('PRESTATEC_DATA_FILE') or (
            ROOT / ('prestatec.db' if self.backend == 'sqlite' else 'data.json')
        ))

    def repositorio(self):
        if self.backend == 'sqlite':
            return SQLiteRepository(self.ruta_datos)
        return JsonFileRepository(self.ruta_datos)
