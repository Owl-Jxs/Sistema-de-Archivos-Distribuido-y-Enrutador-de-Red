from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from ..structure.archivo.archivo import Archivo
from ..structure.carpeta.carpeta import Carpeta


class PersistenciaArbolCSV:
    def __init__(self, ruta_csv: str | Path) -> None:
        self.__ruta_csv = Path(ruta_csv)

    @property
    def ruta_csv(self) -> Path:
        return self.__ruta_csv
    def guardar(self, raiz: Carpeta) -> None:
        if not isinstance(raiz, Carpeta):
            raise TypeError("La raiz debe ser una instancia de Carpeta.")

        self.__ruta_csv.parent.mkdir(parents=True, exist_ok=True)

        with self.__ruta_csv.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as archivo_csv:

            escritor = csv.writer(archivo_csv)

            escritor.writerow(
                [
                    "tipo",
                    "id",
                    "nombre",
                    "id_padre",
                    "contenido",
                    "ultima_modificacion",
                ]
            )

            self.__guardar_carpeta(
                escritor,
                raiz,
                None,
            )
    def __guardar_carpeta(
        self,
        escritor: csv.writer,
        carpeta: Carpeta,
        id_padre: int | None,
    ) -> None:

        escritor.writerow(
            [
                "CARPETA",
                carpeta.id,
                carpeta.nombre_carpeta,
                "" if id_padre is None else id_padre,
                "",
                "",
            ]
        )

        for archivo in carpeta.listar_archivos():
            escritor.writerow(
                [
                    "ARCHIVO",
                    archivo.id,
                    archivo.nombre,
                    carpeta.id,
                    archivo.contenido,
                    archivo.ultima_modificacion.isoformat(),
                ]
            )

        for subcarpeta in carpeta.listar_contenido():
            self.__guardar_carpeta(
                escritor,
                subcarpeta,
                carpeta.id,
            )
    def cargar(self) -> Carpeta:
        if not self.__ruta_csv.exists():
            raise FileNotFoundError(
                f"No existe el archivo CSV: {self.__ruta_csv}"
            )

        with self.__ruta_csv.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as archivo_csv:

            lector = csv.DictReader(archivo_csv)

            if lector.fieldnames is None:
                raise ValueError("El CSV no contiene encabezados.")

            filas = list(lector)

        carpetas: dict[int, Carpeta] = {}
        filas_archivos: list[dict[str, str]] = []

        for fila in filas:
            tipo = fila["tipo"].strip()

            if tipo == "CARPETA":
                id_carpeta = int(fila["id"])

                if id_carpeta in carpetas:
                    raise ValueError(
                        f"Existe una carpeta repetida con ID {id_carpeta}."
                    )

                carpetas[id_carpeta] = Carpeta(
                    id=id_carpeta,
                    nombre_carpeta=fila["nombre"],
                )

            elif tipo == "ARCHIVO":
                filas_archivos.append(fila)

            else:
                raise ValueError(
                    f"Tipo de elemento desconocido: {tipo}"
                )
        raices = [
            carpeta
            for carpeta in carpetas.values()
            if not self.__tiene_padre(filas, carpeta.id)
        ]

        if len(raices) != 1:
            raise ValueError(
                "El CSV debe contener exactamente una carpeta raiz."
            )

        raiz = raices[0]

        for fila in filas:
            if fila["tipo"].strip() != "CARPETA":
                continue

            id_carpeta = int(fila["id"])
            id_padre_texto = fila["id_padre"].strip()

            if id_padre_texto == "":
                continue

            id_padre = int(id_padre_texto)

            if id_padre not in carpetas:
                raise ValueError(
                    f"La carpeta {id_carpeta} "
                    f"referencia a un padre inexistente: {id_padre}."
                )

            carpeta = carpetas[id_carpeta]
            padre = carpetas[id_padre]

            padre.agregar_subcarpeta(carpeta) 
        
        for fila in filas_archivos:
            id_archivo = int(fila["id"])
            nombre = fila["nombre"]

            id_carpeta = int(fila["id_padre"])

            if id_carpeta not in carpetas:
                raise ValueError(
                    f"El archivo {id_archivo} referencia "
                    f"a una carpeta inexistente: {id_carpeta}."
                )

            contenido = fila["contenido"]

            fecha_texto = fila["ultima_modificacion"].strip()

            if fecha_texto:
                ultima_modificacion = datetime.fromisoformat(
                    fecha_texto
                )
            else:
                ultima_modificacion = None

            archivo = Archivo(
                id=id_archivo,
                nombre=nombre,
                contenido=contenido,
                ultima_modificacion=ultima_modificacion,
            )

            carpetas[id_carpeta].agregar_archivo(archivo)

        return raiz   

    @staticmethod
    def __tiene_padre(
        filas: list[dict[str, str]],
        id_carpeta: int,
    ) -> bool:

        for fila in filas:
            if fila["tipo"].strip() != "CARPETA":
                continue

            if fila["id"] == str(id_carpeta):
                id_padre = fila["id_padre"].strip()

                return id_padre != ""

        return False