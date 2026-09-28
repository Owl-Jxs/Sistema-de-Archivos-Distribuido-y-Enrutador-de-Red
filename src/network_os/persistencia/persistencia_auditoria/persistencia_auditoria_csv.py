from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from ...logic.model.registro_auditoria.registro_auditoria import RegistroAuditoria


class PersistenciaAuditoriaCSV:
    """Guarda y recupera registros de auditoria en un archivo CSV."""

    CAMPOS = ("fecha_hora", "categoria", "accion", "resultado", "detalle")

    def __init__(self, ruta_csv: Path) -> None:
        if not isinstance(ruta_csv, Path):
            raise TypeError("La ruta CSV debe ser un Path.")

        self.__ruta_csv = ruta_csv

    @property
    def ruta_csv(self) -> Path:
        return self.__ruta_csv

    def agregar(self, registro: RegistroAuditoria) -> None:
        if not isinstance(registro, RegistroAuditoria):
            raise TypeError("El registro debe ser un RegistroAuditoria.")

        self.__ruta_csv.parent.mkdir(parents=True, exist_ok=True)
        necesita_encabezado = (
            not self.__ruta_csv.exists() or self.__ruta_csv.stat().st_size == 0
        )

        with self.__ruta_csv.open("a", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=self.CAMPOS)
            if necesita_encabezado:
                escritor.writeheader()
            escritor.writerow(
                {
                    "fecha_hora": registro.fecha_hora.isoformat(),
                    "categoria": registro.categoria,
                    "accion": registro.accion,
                    "resultado": registro.resultado,
                    "detalle": registro.detalle,
                }
            )

    def consultar_todo(self) -> list[RegistroAuditoria]:
        if not self.__ruta_csv.exists():
            return []

        with self.__ruta_csv.open("r", encoding="utf-8", newline="") as archivo:
            lector = csv.DictReader(archivo)
            return [self.__reconstruir_registro(fila) for fila in lector]

    def consultar_ultimos(self, cantidad: int) -> list[RegistroAuditoria]:
        self.__validar_cantidad(cantidad)
        if cantidad == 0:
            return []
        return self.consultar_todo()[-cantidad:]

    @staticmethod
    def __validar_cantidad(cantidad: int) -> None:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 0:
            raise ValueError("La cantidad debe ser un entero no negativo.")

    @staticmethod
    def __reconstruir_registro(fila: dict[str, str]) -> RegistroAuditoria:
        try:
            return RegistroAuditoria(
                fecha_hora=datetime.fromisoformat(fila["fecha_hora"]),
                categoria=fila["categoria"],
                accion=fila["accion"],
                resultado=fila["resultado"],
                detalle=fila["detalle"],
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("El archivo CSV contiene un registro invalido.") from error
