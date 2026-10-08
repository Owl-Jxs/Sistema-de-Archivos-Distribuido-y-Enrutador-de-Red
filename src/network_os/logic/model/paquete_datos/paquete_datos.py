from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..fecha_hora import fecha_hora_actual_costa_rica


def _fecha_actual() -> datetime:
    return fecha_hora_actual_costa_rica()


@dataclass(frozen=True, slots=True)
class PaqueteDatos:
    """Contenido transferible entre dos servidores de la red."""

    origen: str
    destino: str
    tipo: str
    contenido: object
    fecha_envio: datetime = field(default_factory=_fecha_actual)

    def __post_init__(self) -> None:
        self.__validar_texto(self.origen, "El origen")
        self.__validar_texto(self.destino, "El destino")
        self.__validar_texto(self.tipo, "El tipo")
        if self.contenido is None:
            raise ValueError("El contenido del paquete no puede ser None.")
        if not isinstance(self.fecha_envio, datetime):
            raise TypeError("La fecha de envio debe ser un datetime.")

        object.__setattr__(self, "origen", self.origen.strip())
        object.__setattr__(self, "destino", self.destino.strip())
        object.__setattr__(self, "tipo", self.tipo.strip().upper())

    @staticmethod
    def __validar_texto(valor: str, nombre: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"{nombre} debe ser una cadena no vacia.")
