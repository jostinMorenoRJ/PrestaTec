"""Adaptador SQLite del estado de PrestaTec.

Cumple DAT-01 (esquema versionado e integridad referencial) y DAT-03
(mutaciones atómicas y serializadas por archivo). El dominio sigue sin conocer
este módulo: solo recibe un objeto con ``load()`` y ``save()``.
"""
import sqlite3
import threading
from pathlib import Path

from .errors import BusinessError
from .repository import estado_vacio

SCHEMA_VERSION = '1'

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS meta (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS equipos (
    id TEXT PRIMARY KEY,
    tipo TEXT NOT NULL,
    nombre TEXT NOT NULL,
    ubicacion TEXT,
    estado TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS usuarios (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    documento TEXT NOT NULL UNIQUE,
    rol TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS prestamos (
    id TEXT PRIMARY KEY,
    equipoId TEXT NOT NULL,
    usuarioId TEXT NOT NULL,
    inicio TEXT,
    fin TEXT,
    estado TEXT NOT NULL,
    entregadoEn TEXT,
    devueltoEn TEXT,
    responsable TEXT,
    nota TEXT,
    FOREIGN KEY (equipoId) REFERENCES equipos(id),
    FOREIGN KEY (usuarioId) REFERENCES usuarios(id)
);
CREATE TABLE IF NOT EXISTS eventos (
    fecha TEXT,
    equipoId TEXT NOT NULL,
    texto TEXT,
    FOREIGN KEY (equipoId) REFERENCES equipos(id)
);
"""

# Las claves foráneas de SQLite son por conexión. Las restricciones también se
# reflejan con triggers para que cualquier conexión (incluida la de una prueba
# o una herramienta externa) respete la integridad referencial (DAT-01).
_INTEGRIDAD = """
CREATE TRIGGER IF NOT EXISTS prestamos_fk_equipo_ins
BEFORE INSERT ON prestamos
WHEN NOT EXISTS (SELECT 1 FROM equipos WHERE id = NEW.equipoId)
BEGIN SELECT RAISE(ABORT, 'integridad: equipo inexistente'); END;
CREATE TRIGGER IF NOT EXISTS prestamos_fk_usuario_ins
BEFORE INSERT ON prestamos
WHEN NOT EXISTS (SELECT 1 FROM usuarios WHERE id = NEW.usuarioId)
BEGIN SELECT RAISE(ABORT, 'integridad: usuario inexistente'); END;
CREATE TRIGGER IF NOT EXISTS prestamos_fk_equipo_upd
BEFORE UPDATE OF equipoId ON prestamos
WHEN NOT EXISTS (SELECT 1 FROM equipos WHERE id = NEW.equipoId)
BEGIN SELECT RAISE(ABORT, 'integridad: equipo inexistente'); END;
CREATE TRIGGER IF NOT EXISTS prestamos_fk_usuario_upd
BEFORE UPDATE OF usuarioId ON prestamos
WHEN NOT EXISTS (SELECT 1 FROM usuarios WHERE id = NEW.usuarioId)
BEGIN SELECT RAISE(ABORT, 'integridad: usuario inexistente'); END;
CREATE TRIGGER IF NOT EXISTS eventos_fk_equipo_ins
BEFORE INSERT ON eventos
WHEN NOT EXISTS (SELECT 1 FROM equipos WHERE id = NEW.equipoId)
BEGIN SELECT RAISE(ABORT, 'integridad: equipo inexistente'); END;
"""

_COLUMNAS = {
    'equipos': ('id', 'tipo', 'nombre', 'ubicacion', 'estado'),
    'usuarios': ('id', 'nombre', 'documento', 'rol'),
    'prestamos': ('id', 'equipoId', 'usuarioId', 'inicio', 'fin', 'estado',
                  'entregadoEn', 'devueltoEn', 'responsable', 'nota'),
    'eventos': ('fecha', 'equipoId', 'texto'),
}

_CANDADOS = {}
_GUARDA_CANDADOS = threading.Lock()


def _candado(ruta):
    clave = str(ruta.resolve())
    with _GUARDA_CANDADOS:
        return _CANDADOS.setdefault(clave, threading.RLock())


class SQLiteRepository:
    """Repositorio sobre un archivo SQLite, con el mismo contrato que JSON."""

    def __init__(self, data_file=None):
        self.data_file = Path(data_file or 'prestatec.db')
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._candado = _candado(self.data_file)
        with self._candado:
            conexion = self._conectar()
            try:
                conexion.executescript(_ESQUEMA)
                conexion.executescript(_INTEGRIDAD)
                conexion.execute(
                    "INSERT OR IGNORE INTO meta (clave, valor) VALUES ('schema_version', ?)",
                    (SCHEMA_VERSION,),
                )
                conexion.commit()
            finally:
                conexion.close()

    def _conectar(self):
        conexion = sqlite3.connect(self.data_file, timeout=30, check_same_thread=False)
        conexion.row_factory = sqlite3.Row
        conexion.execute('PRAGMA foreign_keys = ON')
        return conexion

    def load(self):
        estado = estado_vacio()
        with self._candado:
            conexion = self._conectar()
            try:
                for clave, columnas in _COLUMNAS.items():
                    estado[clave] = [
                        dict(fila) for fila in conexion.execute(
                            f"SELECT {', '.join(columnas)} FROM {clave} ORDER BY rowid"
                        )
                    ]
            finally:
                conexion.close()
        return estado

    def save(self, data):
        with self._candado:
            conexion = self._conectar()
            try:
                conexion.execute('BEGIN IMMEDIATE')
                for clave in ('prestamos', 'eventos', 'equipos', 'usuarios'):
                    conexion.execute(f'DELETE FROM {clave}')
                for clave, columnas in _COLUMNAS.items():
                    marcadores = ', '.join(':' + c for c in columnas)
                    filas = [
                        {c: fila.get(c) for c in columnas}
                        for fila in data.get(clave, [])
                    ]
                    if filas:
                        conexion.executemany(
                            f"INSERT INTO {clave} ({', '.join(columnas)}) VALUES ({marcadores})",
                            filas,
                        )
                conexion.commit()
            except (sqlite3.Error, KeyError, TypeError) as error:
                conexion.rollback()
                raise BusinessError(f'No fue posible guardar en SQLite: {error}') from error
            finally:
                conexion.close()
