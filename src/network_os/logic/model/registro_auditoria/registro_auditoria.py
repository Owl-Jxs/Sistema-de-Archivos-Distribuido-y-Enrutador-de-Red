from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RegistroAuditoria:
    """Representa una operacion de la red o de un servidor."""

    fecha_hora: datetime
    categoria: str
    accion: str
    resultado: str
    detalle: str
    origen: str = "RED"

    def __post_init__(self) -> None:
        if not isinstance(self.fecha_hora, datetime):
            raise TypeError("La fecha y hora debe ser un datetime.")
        self.__validar_texto(self.categoria, "La categoria")
        self.__validar_texto(self.accion, "La accion")
        self.__validar_texto(self.resultado, "El resultado")
        self.__validar_texto(self.origen, "El origen")
        if not isinstance(self.detalle, str):
            raise TypeError("El detalle debe ser una cadena.")

    @staticmethod
    def __validar_texto(valor: str, nombre: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"{nombre} debe ser una cadena no vacia.")
