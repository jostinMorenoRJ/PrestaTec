"""Parámetros de política sujetos a decisión institucional.

Todos los valores son `None` mientras DEC-01..DEC-06 permanezcan abiertas.
El dominio NO inventa umbrales: si un valor no está definido, la regla
correspondiente no se aplica.
"""


class Politicas:
    def __init__(
        self,
        duracion_maxima=None,
        anticipacion_minima=None,
        aprobacion_requerida=None,
        sancion_atraso=None,
        retencion=None,
    ):
        self.duracion_maxima = duracion_maxima
        self.anticipacion_minima = anticipacion_minima
        self.aprobacion_requerida = aprobacion_requerida
        self.sancion_atraso = sancion_atraso
        self.retencion = retencion

    def definida(self, nombre):
        return getattr(self, nombre, None) is not None
