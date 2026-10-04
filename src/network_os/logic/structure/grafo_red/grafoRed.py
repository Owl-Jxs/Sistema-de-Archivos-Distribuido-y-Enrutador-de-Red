from __future__ import annotations

from pathlib import Path

from ....persistencia.persistencia_red.persistencia_red_csv import (
    PersistenciaRedCSV,
)
from ...controller.servidor.servidor import Servidor
from ...model.conexion.conexion import Conexion
from ...structure.vertice_red.verticeRed import VerticeRed


class GrafoRed:
    """Grafo ponderado de servidores de la red."""

    def __init__(
        self,
        ruta_conexiones_csv: str | Path = "datos/red_conexiones.csv",
    ) -> None:
        self.__validar_ruta(ruta_conexiones_csv)

        self.__vertices: list[VerticeRed] = []
        self.__persistencia = PersistenciaRedCSV(ruta_conexiones_csv)

    @property
    def vertices(self) -> list[VerticeRed]:
        return self.__vertices

    @property
    def persistencia(self) -> PersistenciaRedCSV:
        return self.__persistencia

    @staticmethod
    def __validar_ruta(ruta_conexiones_csv: str | Path) -> None:
        if isinstance(ruta_conexiones_csv, str):
            if not ruta_conexiones_csv.strip():
                raise ValueError("La ruta del archivo CSV no puede estar vacia.")
        elif not isinstance(ruta_conexiones_csv, Path):
            raise TypeError("La ruta del archivo CSV debe ser un str o Path.")

    @staticmethod
    def __validar_servidor(servidor: Servidor) -> None:
        if not isinstance(servidor, Servidor):
            raise TypeError("El servidor debe ser una instancia de Servidor.")

    @staticmethod
    def __validar_nombre(nombre: str) -> None:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del servidor debe ser una cadena no vacia.")

    @staticmethod
    def __validar_latencia(latencia: float) -> None:
        if isinstance(latencia, bool) or not isinstance(latencia, (int, float)):
            raise TypeError("La latencia debe ser un numero.")
        if latencia < 0:
            raise ValueError("La latencia no puede ser negativa.")

    def agregar_servidor(self, servidor: Servidor) -> None:
        """Agrega un servidor como vertice nuevo de la red."""
        self.__validar_servidor(servidor)

        if self.__buscar_vertice_interno(servidor.nombre) is not None:
            raise ValueError(
                f"Ya existe un servidor llamado {servidor.nombre} en la red."
            )

        self.__vertices.append(VerticeRed(servidor))

    def buscar_vertice(self, nombre: str) -> VerticeRed:
        """Devuelve el vertice del servidor con el nombre indicado."""
        self.__validar_nombre(nombre)

        vertice = self.__buscar_vertice_interno(nombre.strip())

        if vertice is None:
            raise ValueError(
                f"No existe un servidor llamado {nombre.strip()} en la red."
            )

        return vertice

    def agregar_conexion(
        self,
        origen: str,
        destino: str,
        latencia: float,
    ) -> None:
        """Conecta el vertice de origen con el vertice de destino."""
        self.__validar_nombre(origen)
        self.__validar_nombre(destino)
        self.__validar_latencia(latencia)

        vertice_origen = self.buscar_vertice(origen)
        vertice_destino = self.buscar_vertice(destino)

        vertice_origen.agregar_conexion(
            Conexion(vertice_destino, latencia),
        )

    def guardar(self) -> None:
        """Guarda los servidores y las conexiones de la red en el CSV."""
        self.__persistencia.guardar(self)

    def cargar(self) -> None:
        """Reconstruye la red desde el CSV."""
        grafo_cargado = self.__persistencia.cargar()
        self.__vertices = grafo_cargado.vertices

    def __buscar_vertice_interno(self, nombre: str) -> VerticeRed | None:
        for vertice in self.__vertices:
            if vertice.servidor.nombre == nombre:
                return vertice
        return None
