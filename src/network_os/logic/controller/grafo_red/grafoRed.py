from __future__ import annotations

import math
from pathlib import Path

from ....persistencia.persistencia_red.persistencia_red_csv import (
    PersistenciaRedCSV,
)
from ..servidor.servidor import Servidor
from ..auditoria.auditoria import Auditoria
from ...model.conexion.conexion import Conexion
from ...model.registro_auditoria.registro_auditoria import RegistroAuditoria
from ...structure.vertice_red.verticeRed import VerticeRed


class GrafoRed:
    """Grafo ponderado de servidores de la red."""

    def __init__(
        self,
        ruta_conexiones_csv: str | Path = "datos/red_conexiones.csv",
        *,
        auditoria: Auditoria,
    ) -> None:
        self.__validar_ruta(ruta_conexiones_csv)
        if not isinstance(auditoria, Auditoria):
            raise TypeError("La auditoria debe ser una instancia de Auditoria.")
        self.__auditoria = auditoria

        self.__vertices: list[VerticeRed] = []
        self.__persistencia = PersistenciaRedCSV(ruta_conexiones_csv)

    @property
    def vertices(self) -> list[VerticeRed]:
        return self.__vertices

    @property
    def persistencia(self) -> PersistenciaRedCSV:
        return self.__persistencia

    @property
    def auditoria(self) -> Auditoria:
        return self.__auditoria

    def consultar_auditoria(self) -> list[RegistroAuditoria]:
        return self.__auditoria.consultar_todo()

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
        if not math.isfinite(latencia):
            raise ValueError("La latencia debe ser un numero finito.")
        if latencia < 0:
            raise ValueError("La latencia no puede ser negativa.")

    def agregar_servidor(self, servidor: Servidor) -> None:
        """Agrega un servidor como vertice nuevo de la red."""
        detalle = (
            f"Servidor '{servidor.nombre}', ID {servidor.id}."
            if isinstance(servidor, Servidor) else "Servidor invalido."
        )
        self.__auditoria.ejecutar(
            "RED", "AGREGAR_SERVIDOR", detalle,
            lambda: self._agregar_servidor(servidor),
        )

    def _agregar_servidor(self, servidor: Servidor) -> None:
        """Insercion validada; la carga la reutiliza sin registrar un alta nueva."""
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
        """Conecta dos servidores con una arista bidireccional de latencia dada."""
        self.__auditoria.ejecutar(
            "RED", "AGREGAR_CONEXION",
            f"Origen: {origen}; destino: {destino}; latencia: {latencia} ms.",
            lambda: self._agregar_conexion(origen, destino, latencia),
        )

    def _agregar_conexion(self, origen: str, destino: str, latencia: float) -> None:
        """Conexion validada, tambien utilizada al reconstruir el CSV."""
        self.__validar_nombre(origen)
        self.__validar_nombre(destino)
        self.__validar_latencia(latencia)

        vertice_origen = self.buscar_vertice(origen)
        vertice_destino = self.buscar_vertice(destino)

        if (
            vertice_origen.buscar_conexion(vertice_destino) is not None
            or vertice_destino.buscar_conexion(vertice_origen) is not None
        ):
            raise ValueError(
                f"Ya existe una conexion entre {origen} y {destino}."
            )

        vertice_origen.agregar_conexion(Conexion(vertice_destino, latencia))
        if vertice_origen is not vertice_destino:
            vertice_destino.agregar_conexion(Conexion(vertice_origen, latencia))

    def eliminar_conexion(self, origen: str, destino: str) -> None:
        """Elimina la conexion bidireccional entre dos servidores."""
        self.__auditoria.ejecutar(
            "RED", "ELIMINAR_CONEXION",
            f"Origen: {origen}; destino: {destino}.",
            lambda: self.__eliminar_conexion(origen, destino),
        )

    def __eliminar_conexion(self, origen: str, destino: str) -> None:
        self.__validar_nombre(origen)
        self.__validar_nombre(destino)

        vertice_origen = self.buscar_vertice(origen)
        vertice_destino = self.buscar_vertice(destino)

        if (
            vertice_origen.buscar_conexion(vertice_destino) is None
            and vertice_destino.buscar_conexion(vertice_origen) is None
        ):
            raise ValueError(
                f"No existe una conexion entre {origen} y {destino}."
            )

        vertice_origen.eliminar_conexion(vertice_destino)
        if vertice_origen is not vertice_destino:
            vertice_destino.eliminar_conexion(vertice_origen)

    def bfs(self, origen: str) -> list[str]:
        """Devuelve los nombres alcanzables por niveles, en orden de conexion."""
        vertice_origen = self.buscar_vertice(origen)
        pendientes = [vertice_origen]
        visitados = {vertice_origen.servidor.nombre}
        recorrido: list[str] = []
        indice = 0

        # El indice permite usar la lista como cola sin desplazar elementos.
        while indice < len(pendientes):
            actual = pendientes[indice]
            indice += 1
            recorrido.append(actual.servidor.nombre)

            for conexion in actual.conexiones:
                nombre = conexion.destino.servidor.nombre
                if nombre not in visitados:
                    visitados.add(nombre)
                    pendientes.append(conexion.destino)

        return recorrido

    def dijkstra(
        self, origen: str,
    ) -> tuple[dict[str, float], dict[str, str | None]]:
        """Devuelve distancias y predecesores; los inalcanzables quedan en inf."""
        vertice_origen = self.buscar_vertice(origen)

        # Conexion permite cambiar la latencia despues de agregar la arista.
        for vertice in self.__vertices:
            for conexion in vertice.conexiones:
                self.__validar_latencia(conexion.latencia_ms)

        distancias = {
            vertice.servidor.nombre: math.inf for vertice in self.__vertices
        }
        anteriores: dict[str, str | None] = {
            vertice.servidor.nombre: None for vertice in self.__vertices
        }
        distancias[vertice_origen.servidor.nombre] = 0
        visitados: set[str] = set()

        while True:
            actual = None
            menor_distancia = math.inf
            for vertice in self.__vertices:
                nombre = vertice.servidor.nombre
                if nombre not in visitados and distancias[nombre] < menor_distancia:
                    actual = vertice
                    menor_distancia = distancias[nombre]

            # No quedan vertices pendientes alcanzables desde el origen.
            if actual is None:
                break

            nombre_actual = actual.servidor.nombre
            visitados.add(nombre_actual)
            for conexion in actual.conexiones:
                destino = conexion.destino.servidor.nombre
                if destino in visitados:
                    continue
                nueva_distancia = menor_distancia + conexion.latencia_ms
                if nueva_distancia < distancias[destino]:
                    distancias[destino] = nueva_distancia
                    anteriores[destino] = nombre_actual

        return distancias, anteriores

    def ruta_mas_corta(
        self, origen: str, destino: str,
    ) -> tuple[list[str], float] | None:
        """Devuelve (nombres de la ruta, latencia total), o None si no hay ruta."""
        detalle = f"Origen: {origen}; destino: {destino}."

        def describir(resultado: tuple[list[str], float] | None) -> tuple[str, str]:
            if resultado is None:
                return "FALLIDO", f"{detalle} No existe una ruta."
            ruta, costo = resultado
            return "EXITOSO", f"{detalle} Recorrido: {' -> '.join(ruta)}; costo: {costo} ms."

        return self.__auditoria.ejecutar(
            "RED", "RUTA_MAS_CORTA", detalle,
            lambda: self.__ruta_mas_corta(origen, destino), describir,
        )

    def __ruta_mas_corta(
        self, origen: str, destino: str,
    ) -> tuple[list[str], float] | None:
        self.buscar_vertice(origen)
        nombre_destino = self.buscar_vertice(destino).servidor.nombre
        distancias, anteriores = self.dijkstra(origen)
        costo_total = distancias[nombre_destino]
        if costo_total == math.inf:
            return None

        ruta: list[str] = []
        actual: str | None = nombre_destino
        while actual is not None:
            ruta.append(actual)
            actual = anteriores[actual]
        ruta.reverse()
        return ruta, costo_total

    def ping_general(self, origen: str) -> dict[str, float | None]:
        """Latencia minima a cada otro servidor; None indica que es inalcanzable."""
        def describir(resultado: dict[str, float | None]) -> tuple[str, str]:
            destinos = "; ".join(
                f"{nombre}: {latencia} ms" if latencia is not None
                else f"{nombre}: inalcanzable"
                for nombre, latencia in resultado.items()
            )
            return "EXITOSO", f"Origen: {origen}; {destinos or 'sin otros servidores'}."

        return self.__auditoria.ejecutar(
            "RED", "PING_GENERAL", f"Origen: {origen}.",
            lambda: self.__ping_general(origen), describir,
        )

    def __ping_general(self, origen: str) -> dict[str, float | None]:
        distancias, _ = self.dijkstra(origen)
        return {
            nombre: distancia if distancia != math.inf else None
            for nombre, distancia in distancias.items()
            if nombre != origen.strip()
        }

    def guardar(self) -> None:
        """Guarda los servidores y las conexiones de la red en el CSV."""
        self.__auditoria.ejecutar(
            "PERSISTENCIA", "GUARDAR_RED", "Estado de la red.",
            lambda: self.__persistencia.guardar(self),
        )

    def cargar(self) -> None:
        """Reconstruye la red desde el CSV."""
        def operacion() -> None:
            grafo_cargado = self.__persistencia.cargar(self.__auditoria)
            self.__vertices = grafo_cargado.vertices

        self.__auditoria.ejecutar(
            "PERSISTENCIA", "CARGAR_RED", "Reconstruccion de la red.", operacion,
        )

    def __buscar_vertice_interno(self, nombre: str) -> VerticeRed | None:
        for vertice in self.__vertices:
            if vertice.servidor.nombre == nombre:
                return vertice
        return None
