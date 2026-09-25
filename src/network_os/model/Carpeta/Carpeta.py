# Carpeta.py
from __future__ import annotations


class Carpeta:
    """Clase que representa una carpeta en el sistema."""

    def __init__(
            self,
            id: int,
            nombre_carpeta: str,
            direccion_carpeta: str,
            _carpeta_padre: Carpeta | None = None,
            _lista_archivos: list[int] | None = None,
            _primer_subcarpeta: Carpeta | None = None,
            _siguiente_subcarpeta: Carpeta | None = None,
    ) -> None:
        """Constructor de la clase Carpeta."""

        # Validamos los parámetros recibidos antes de asignarlos
        self.__validar_id(id)
        self.__validar_str(nombre_carpeta)
        self.__validar_str(direccion_carpeta)

        self.id: int = id
        self.nombre_carpeta: str = nombre_carpeta.strip()
        self.direccion_carpeta: str = direccion_carpeta.strip()
        self._carpeta_padre: Carpeta | None = _carpeta_padre
        self._lista_archivos: list[int] = (
            _lista_archivos if _lista_archivos is not None else []
        )
        self._primer_subcarpeta: Carpeta | None = _primer_subcarpeta
        self._siguiente_subcarpeta: Carpeta | None = _siguiente_subcarpeta

    # --- Métodos Privados de Validación ---

    def __validar_str(self, entrada: str | None) -> None:
        """Valida que las entradas de texto no sean nulas ni vacías."""
        if entrada is None or not bool(entrada.strip()):
            raise ValueError(
                "El texto no puede estar vacío, ser nulo ni contener solo espacios."
            )

    def __validar_id(self, id: int | None) -> None:
        """Valida que el ID no sea nulo y sea un entero válido."""
        if id is None or id < 0:
            raise ValueError("El ID no puede ser nulo ni negativo.")

    # --- Métodos Privados de Busqueda ---


    # --- Métodos Públicos ---

    def renombrar_carpeta(
        self,
        nuevo_nombre: str
    ) -> None:
        """Renombra la carpeta previa validación."""
        self.__validar_str(nuevo_nombre)
        self.nombre_carpeta = nuevo_nombre.strip()


    def buscar_subcarpeta_por_nombre (
        self,
        nombre : str
    ) -> Carpeta | None:
        """Buscamos entre las carpetas actuales la carpeta deseada mediante el nombre"""
        self.__validar_str(nombre)
        carpeta_actual = self._primer_subcarpeta

        while (carpeta_actual is not None):
            if (carpeta_actual.nombre_carpeta == nombre):
                carpeta_deseada = carpeta_actual
                return carpeta_actual

            carpeta_actual = carpeta_actual._siguiente_subcarpeta
        return None #Si no se encontro

    def buscar_subcarpeta_por_id (
            self,
            id : int
    ) -> Carpeta | None:
        """Buscamos entre las carpetas actuales la carpeta deseada mediante el nombre"""
        self.__validar_id(id)
        carpeta_actual = self._primer_subcarpeta

        while (carpeta_actual is not None):
            if (carpeta_actual.id == id):
                carpeta_deseada = carpeta_actual
                return carpeta_actual

            carpeta_actual = carpeta_actual._siguiente_subcarpeta
        return None #Si no se encontro