from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from ...logic.model.registro_auditoria.registro_auditoria import RegistroAuditoria


class PersistenciaAuditoriaCSV:
    """Agrega y consulta un archivo de auditoria con codificacion CSV."""

    CAMPOS = ("fecha_hora", "categoria", "accion", "resultado", "detalle", "origen")

    def __init__(self, ruta_csv: Path = Path("network_audit_log.txt")) -> None:
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
        campos = self.CAMPOS
        if not necesita_encabezado:
            with self.__ruta_csv.open("r", encoding="utf-8", newline="") as archivo:
                encabezado = next(csv.reader(archivo))
            if len(encabezado) == len(self.CAMPOS) and set(encabezado) == set(self.CAMPOS):
                campos = encabezado
            elif encabezado != list(self.CAMPOS[:-1]):
                raise ValueError("El archivo CSV contiene un encabezado invalido.")

        with self.__ruta_csv.open("a", encoding="utf-8", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            if necesita_encabezado:
                escritor.writeheader()
            escritor.writerow(
                {
                    "fecha_hora": registro.fecha_hora.isoformat(),
                    "origen": registro.origen,
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
            registros = []
            for fila in lector:
                if "origen" not in fila:
                    # El encabezado antiguo tiene cinco campos; append agrega
                    # el origen al final sin reescribir los registros previos.
                    adicionales = fila.pop(None, [])
                    fila["origen"] = adicionales[0] if adicionales else "DESCONOCIDO"
                registros.append(self.__reconstruir_registro(fila))
            return registros

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
                origen=fila.get("origen", "DESCONOCIDO"),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("El archivo CSV contiene un registro invalido.") from error
