from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from ..model.registro_auditoria.registro_auditoria import RegistroAuditoria
from ...persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)


class AuditoriaServidor:
    """Expone las operaciones de auditoria asociadas a un servidor."""

    def __init__(
        self, nombre_servidor: str, persistencia: PersistenciaAuditoriaCSV
    ) -> None:
        self.__validar_nombre_servidor(nombre_servidor)
        if not isinstance(persistencia, PersistenciaAuditoriaCSV):
            raise TypeError(
                "La persistencia debe ser una PersistenciaAuditoriaCSV."
            )

        self.__nombre_servidor = nombre_servidor.strip()
        self.__persistencia = persistencia

    @property
    def nombre_servidor(self) -> str:
        return self.__nombre_servidor

    @property
    def persistencia(self) -> PersistenciaAuditoriaCSV:
        return self.__persistencia

    def registrar(
        self, categoria: str, accion: str, resultado: str, detalle: str
    ) -> None:
        registro = RegistroAuditoria(
            fecha_hora=datetime.now(ZoneInfo("America/Costa_Rica")),
            categoria=categoria,
            accion=accion,
            resultado=resultado,
            detalle=detalle,
        )
        self.__persistencia.agregar(registro)

    def consultar_todo(self) -> list[RegistroAuditoria]:
        return self.__persistencia.consultar_todo()

    def consultar_ultimos(self, cantidad: int) -> list[RegistroAuditoria]:
        return self.__persistencia.consultar_ultimos(cantidad)

    @staticmethod
    def __validar_nombre_servidor(nombre_servidor: str) -> None:
        if not isinstance(nombre_servidor, str) or not nombre_servidor.strip():
            raise ValueError("El nombre del servidor debe ser una cadena no vacia.")
