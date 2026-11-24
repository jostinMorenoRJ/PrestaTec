"""Proveedor de tiempo inyectable y normalización UTC.

Todas las reglas temporales del dominio obtienen la hora de este módulo.
Los valores naive se interpretan como UTC para evitar comparaciones entre
datetimes conscientes e inconscientes.
"""
from datetime import datetime, timezone


def a_utc(valor):
    """Convierte `datetime` o ISO 8601 a `datetime` consciente en UTC."""
    if isinstance(valor, str):
        valor = datetime.fromisoformat(valor)
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


class Reloj:
    """Reloj del sistema."""

    def ahora(self) -> datetime:
        return datetime.now(timezone.utc)


class RelojFalso(Reloj):
    """Reloj determinista para pruebas."""

    def __init__(self, momento: datetime):
        self.momento = a_utc(momento)

    def ahora(self) -> datetime:
        return self.momento
