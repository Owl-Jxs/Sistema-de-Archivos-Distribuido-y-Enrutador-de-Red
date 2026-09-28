from __future__ import annotations

from copy import deepcopy
from datetime import datetime


class Archivo:
    """Representa un archivo virtual almacenado completamente en memoria."""

    def __init__(
        self,
        id: int,
        nombre: str,
        contenido: object = None,
        ultima_modificacion: datetime | None = None,
    ) -> None:
        self.__validar_id(id)
        self.__validar_nombre(nombre)

        if ultima_modificacion is not None and not isinstance(
            ultima_modificacion, datetime
        ):
            raise TypeError(
                "La ultima_modificacion debe ser un datetime o None."
            )

        self.__id = id
        self.__nombre = nombre.strip()
        self.__contenido = contenido
        self.__ultima_modificacion = (
            ultima_modificacion
            if ultima_modificacion is not None
            else datetime.now()
        )

    @staticmethod
    def __validar_id(id: int) -> None:
        if not isinstance(id, int) or isinstance(id, bool) or id < 0:
            raise ValueError("El ID debe ser un entero no negativo.")

    @staticmethod
    def __validar_nombre(nombre: str) -> None:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre debe ser una cadena no vacia.")

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def contenido(self) -> object:
        return self.__contenido

    @property
    def ultima_modificacion(self) -> datetime:
        return self.__ultima_modificacion

    def renombrar(self, nombre: str) -> None:
        self.__validar_nombre(nombre)
        self.__nombre = nombre.strip()
        self.__ultima_modificacion = datetime.now()

    def actualizar_contenido(self, contenido: object) -> None:
        self.__contenido = contenido
        self.__ultima_modificacion = datetime.now()

    def clonar(self, nuevo_id: int) -> Archivo:
        """Crea una copia independiente conservando la fecha de modificacion."""
        self.__validar_id(nuevo_id)
        return Archivo(
            id=nuevo_id,
            nombre=self.__nombre,
            contenido=deepcopy(self.__contenido),
            ultima_modificacion=self.__ultima_modificacion,
        )
