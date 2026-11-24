"""Errores de dominio compartidos por los adaptadores y los casos de uso."""


class BusinessError(Exception):
    """Error de validación o regla de negocio."""


class ConflictoReserva(BusinessError):
    """El intervalo solicitado ya está ocupado; ofrece alternativas reales."""

    def __init__(self, mensaje, alternativas=None):
        super().__init__(mensaje)
        self.alternativas = list(alternativas or [])

