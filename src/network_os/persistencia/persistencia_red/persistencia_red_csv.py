from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING

from ...logic.controller.servidor.servidor import Servidor

if TYPE_CHECKING:
    from ...logic.structure.grafo_red.grafoRed import GrafoRed


class PersistenciaRedCSV:
    """Persiste los servidores y las conexiones de la red en un archivo CSV."""

    CAMPOS = (
        "tipo",
        "nombre",
        "id",
        "direccion_base",
        "origen",
        "destino",
        "latencia_ms",
    )

    def __init__(self, ruta_conexiones_csv: str | Path) -> None:
        self.__validar_ruta(ruta_conexiones_csv)
        self.__ruta_conexiones_csv = Path(ruta_conexiones_csv)

    @property
    def ruta_conexiones_csv(self) -> Path:
        return self.__ruta_conexiones_csv

    def guardar(self, grafo: GrafoRed) -> None:
        from ...logic.structure.grafo_red.grafoRed import GrafoRed

        if not isinstance(grafo, GrafoRed):
            raise TypeError("El grafo debe ser una instancia de GrafoRed.")

        self.__ruta_conexiones_csv.parent.mkdir(parents=True, exist_ok=True)

        with self.__ruta_conexiones_csv.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as archivo_csv:

            escritor = csv.writer(archivo_csv)

            escritor.writerow(self.CAMPOS)

            for vertice in grafo.vertices:
                servidor = vertice.servidor

                escritor.writerow(
                    [
                        "SERVIDOR",
                        servidor.nombre,
                        servidor.id,
                        str(servidor.persistencia.directorio.parent.parent),
                        "",
                        "",
                        "",
                    ]
                )

            for vertice in grafo.vertices:
                for conexion in vertice.conexiones:
                    escritor.writerow(
                        [
                            "CONEXION",
                            "",
                            "",
                            "",
                            vertice.servidor.nombre,
                            conexion.destino.servidor.nombre,
                            conexion.latencia_ms,
                        ]
                    )

    def cargar(self) -> GrafoRed:
        from ...logic.structure.grafo_red.grafoRed import GrafoRed

        if not self.__ruta_conexiones_csv.exists():
            raise FileNotFoundError(
                f"No existe el archivo CSV: {self.__ruta_conexiones_csv}"
            )

        with self.__ruta_conexiones_csv.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as archivo_csv:

            lector = csv.DictReader(archivo_csv)

            if lector.fieldnames is None:
                raise ValueError("El CSV no contiene encabezados.")

            if not set(self.CAMPOS).issubset(lector.fieldnames):
                raise ValueError(
                    "El CSV no contiene las columnas requeridas: "
                    f"{', '.join(self.CAMPOS)}."
                )

            filas = list(lector)

        grafo = GrafoRed(self.__ruta_conexiones_csv)
        filas_conexiones: list[dict[str, str]] = []

        for fila in filas:
            tipo = (fila.get("tipo") or "").strip()

            if tipo == "SERVIDOR":
                self.__cargar_servidor(grafo, fila)

            elif tipo == "CONEXION":
                filas_conexiones.append(fila)

            else:
                raise ValueError(f"Tipo de elemento desconocido: {tipo}")

        for fila in filas_conexiones:
            origen = (fila.get("origen") or "").strip()
            destino = (fila.get("destino") or "").strip()

            if not origen or not destino:
                raise ValueError(
                    "La fila CONEXION debe indicar el origen y el destino."
                )

            texto_latencia = (fila.get("latencia_ms") or "").strip()

            try:
                latencia = float(texto_latencia)
            except ValueError:
                raise ValueError(
                    f"La latencia de la conexion {origen} -> {destino} "
                    f"no es numerica: {texto_latencia}."
                ) from None

            grafo.agregar_conexion(origen, destino, latencia)

        return grafo

    @staticmethod
    def __cargar_servidor(grafo: GrafoRed, fila: dict[str, str]) -> None:
        nombre = (fila.get("nombre") or "").strip()
        id_texto = (fila.get("id") or "").strip()
        direccion_base = (fila.get("direccion_base") or "").strip()

        try:
            id_servidor = int(id_texto)
        except ValueError:
            raise ValueError(
                f"El id del servidor {nombre} no es un entero: {id_texto}."
            ) from None

        grafo.agregar_servidor(
            Servidor(nombre, id_servidor, direccion_base),
        )

    @staticmethod
    def __validar_ruta(ruta_conexiones_csv: str | Path) -> None:
        if isinstance(ruta_conexiones_csv, str):
            if not ruta_conexiones_csv.strip():
                raise ValueError("La ruta del archivo CSV no puede estar vacia.")
        elif not isinstance(ruta_conexiones_csv, Path):
            raise TypeError("La ruta del archivo CSV debe ser un str o Path.")
