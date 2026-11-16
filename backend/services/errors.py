"""Errores controlados del análisis. Se convierten en el campo `error` de la evaluación."""

from models.schemas import CodigoError


class AnalisisError(Exception):
    def __init__(self, codigo: CodigoError, mensaje: str, reintentable: bool = True):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje
        self.reintentable = reintentable
