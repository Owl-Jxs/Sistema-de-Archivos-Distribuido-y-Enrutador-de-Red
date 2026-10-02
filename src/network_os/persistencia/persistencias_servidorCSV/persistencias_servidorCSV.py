from __future__ import annotations

from pathlib import Path

from ..persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV
)

from ..persistencia_usuarios.persistencia_usuarios_csv import (
    PersistenciaUsuariosCSV
)

from ..persistencia_carpetas.persistencia_arbol_csv import (
    PersistenciaArbolCSV
)

class PersistenciaServidorCSV:
    """Agrupa las persistencias necesarias de cada servidor"""

    CARACTERES_INVALIDOS = frozenset('<>:"/\\|?*')

    def __init__(
        self,
        ruta_base: str | Path,
        nombre: str,
        id_servidor: int,
    ) -> None:
        self.__validar_ruta_base(ruta_base)
        self.__validar_nombre(nombre)
        self.__validar_id(id_servidor)

        identificador = f"{nombre.strip()}_{id_servidor}"
        self.__directorio = Path(ruta_base) / "servidores" / identificador
        self.__directorio.mkdir(parents=True, exist_ok=True)

        self.__auditoria = PersistenciaAuditoriaCSV(
            self.__directorio / "auditoria.csv"
        )

        self.__usuarios = PersistenciaUsuariosCSV (
            self.__directorio / "usuarios.csv"
        )

        self.__archivos = PersistenciaArbolCSV (
            self.__directorio / "archivos.csv"
        )

    @property
    def directorio(self) -> Path:
        return self.__directorio

    @property
    def auditoria(self) -> PersistenciaAuditoriaCSV:
        return self.__auditoria

    @property
    def usuarios (self) -> PersistenciaUsuariosCSV:
       return self.__usuarios

    @property
    def archivos (self) -> PersistenciaArbolCSV:
       return self.__archivos

    @staticmethod
    def __validar_ruta_base(ruta_base: str | Path) -> None:
        if isinstance(ruta_base, str):
            if not ruta_base.strip():
                raise ValueError("La ruta base no puede estar vacia.")
        elif not isinstance(ruta_base, Path):
            raise TypeError("La ruta base debe ser un str o Path.")

    @classmethod
    def __validar_nombre(cls, nombre: str) -> None:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del servidor debe ser una cadena no vacia.")
        if any(caracter in cls.CARACTERES_INVALIDOS for caracter in nombre):
            raise ValueError(
                "El nombre del servidor contiene caracteres no permitidos en una ruta."
            )

    @staticmethod
    def __validar_id(id_servidor: int) -> None:
        if (
            not isinstance(id_servidor, int)
            or isinstance(id_servidor, bool)
            or id_servidor < 0
        ):
            raise ValueError("El ID del servidor debe ser un entero no negativo.")
