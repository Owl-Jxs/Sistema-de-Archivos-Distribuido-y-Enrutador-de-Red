from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from ...model.fecha_hora import fecha_hora_actual_costa_rica
from ...model.registro_auditoria.registro_auditoria import RegistroAuditoria
from ....persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)


T = TypeVar("T")


class Auditoria:
    """Registra las operaciones de un servidor o de la red en su propio archivo."""

    def __init__(
        self, origen: str, persistencia: PersistenciaAuditoriaCSV
    ) -> None:
        if not isinstance(origen, str) or not origen.strip():
            raise ValueError("El origen debe ser una cadena no vacia.")
        if not isinstance(persistencia, PersistenciaAuditoriaCSV):
            raise TypeError(
                "La persistencia debe ser una PersistenciaAuditoriaCSV."
            )

        self.__origen = origen.strip()
        self.__persistencia = persistencia

    @property
    def origen(self) -> str:
        return self.__origen

    @property
    def persistencia(self) -> PersistenciaAuditoriaCSV:
        return self.__persistencia

    def registrar(
        self, categoria: str, accion: str, resultado: str, detalle: str
    ) -> None:
        registro = RegistroAuditoria(
            fecha_hora=fecha_hora_actual_costa_rica(),
            categoria=categoria,
            accion=accion,
            resultado=resultado,
            detalle=detalle,
            origen=self.__origen,
        )
        self.__persistencia.agregar(registro)

    def ejecutar(
        self,
        categoria: str,
        accion: str,
        detalle: str,
        operacion: Callable[[], T],
        describir_resultado: Callable[[T], tuple[str, str]] | None = None,
    ) -> T:
        """Ejecuta una operacion y registra una sola vez su resultado final."""
        try:
            valor = operacion()
        except Exception as error:
            # Una excepcion de persistencia puede contener datos confidenciales.
            self.registrar(
                categoria, accion, "ERROR",
                f"{detalle} Error: {type(error).__name__}.",
            )
            raise

        resultado = "FALLIDO" if valor is False else "EXITOSO"
        if describir_resultado is not None:
            resultado, detalle = describir_resultado(valor)
        self.registrar(categoria, accion, resultado, detalle)
        return valor

    def consultar_todo(self) -> list[RegistroAuditoria]:
        return self.__persistencia.consultar_todo()

    def consultar_ultimos(self, cantidad: int) -> list[RegistroAuditoria]:
        return self.__persistencia.consultar_ultimos(cantidad)

