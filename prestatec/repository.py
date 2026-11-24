"""Contrato de repositorio y adaptador JSON del estado actual.

La lógica de negocio no conoce este módulo: recibe un repositorio inyectado.
El adaptador JSON conserva el formato y la compatibilidad PascalCase del
proyecto original, incluido el comportamiento observado con claves mixtas
(documentado como defecto P9 en las pruebas de caracterización).
"""
import json
from pathlib import Path
from typing import Protocol, runtime_checkable

from .errors import BusinessError


def estado_vacio():
    """Devuelve una estructura nueva para evitar listas compartidas."""
    return {'equipos': [], 'usuarios': [], 'prestamos': [], 'eventos': []}


@runtime_checkable
class Repository(Protocol):
    """Contrato mínimo de persistencia para el dominio."""

    def load(self) -> dict:
        """Carga el estado completo."""

    def save(self, data: dict) -> None:
        """Guarda el estado completo."""


class JsonFileRepository:
    """Adaptador sobre `data.json`, sin cambiar su formato."""

    def __init__(self, data_file=None):
        self.data_file = (
            Path(data_file)
            if data_file is not None
            else Path(__file__).resolve().parent.parent / 'data.json'
        )
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict:
        if self.data_file.exists():
            try:
                data = json.loads(self.data_file.read_text(encoding='utf-8'))
                # Compatibilidad con el JSON PascalCase del proyecto C# original.
                if 'Equipos' in data:
                    data = {
                        'equipos': [{'id': x.get('Id', ''), 'tipo': x.get('Tipo', 'Portátil'), 'nombre': x.get('Nombre', ''), 'ubicacion': x.get('Ubicacion', ''), 'estado': x.get('Estado', 'Disponible')} for x in data.get('Equipos', [])],
                        'usuarios': [{'id': x.get('Id', ''), 'nombre': x.get('Nombre', ''), 'documento': x.get('Documento', ''), 'rol': x.get('Rol', 'Estudiante')} for x in data.get('Usuarios', [])],
                        'prestamos': [{'id': x.get('Id', ''), 'equipoId': x.get('EquipoId', ''), 'usuarioId': x.get('UsuarioId', ''), 'inicio': x.get('Inicio'), 'fin': x.get('Fin'), 'estado': x.get('Estado', 'Confirmada'), 'entregadoEn': x.get('EntregadoEn'), 'devueltoEn': x.get('DevueltoEn'), 'responsable': x.get('Responsable'), 'nota': x.get('Nota') or ''} for x in data.get('Reservas', [])],
                        'eventos': [{'fecha': x.get('Fecha'), 'equipoId': x.get('EquipoId', ''), 'texto': x.get('Texto', '')} for x in data.get('Eventos', [])],
                    }
                return {**estado_vacio(), **data}
            except (OSError, json.JSONDecodeError) as error:
                raise BusinessError('No fue posible leer datos.json.') from error
        return estado_vacio()

    def save(self, data: dict) -> None:
        self.data_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8'
        )
