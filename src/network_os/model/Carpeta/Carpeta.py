# Carpeta.py
from __future__ import annotations


class Carpeta:
    """Clase que representa una carpeta en el sistema."""

    separador_direccion = '/'

    def __init__(
        self,
        id: int,
        nombre_carpeta: str,
        direccion_carpeta: str,
        carpeta_padre: Carpeta | None = None,
        lista_archivos: list[int] | None = None,
        primer_subcarpeta: Carpeta | None = None,
        siguiente_subcarpeta: Carpeta | None = None,
    ) -> None:
        """Constructor de la clase Carpeta."""

        # Validaciones de entrada
        self.__validar_id(id)
        self.__validar_str(nombre_carpeta)
        self.__validar_str(direccion_carpeta)

        self.id: int = id
        self.nombre_carpeta: str = nombre_carpeta.strip()
        self.direccion_carpeta: str = direccion_carpeta.strip()

        # Atributos privados
        self.__carpeta_padre: Carpeta | None = carpeta_padre
        self.__lista_archivos: list[int] = (
            lista_archivos if lista_archivos is not None else []
        )
        self.__primer_subcarpeta: Carpeta | None = primer_subcarpeta
        self.__siguiente_subcarpeta: Carpeta | None = siguiente_subcarpeta

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

    def __vaciado_recursivo(self) -> None:
        """Método auxiliar para borrar recursivamente el árbol de una carpeta."""
        subcarpeta_actual = self.__primer_subcarpeta

        while subcarpeta_actual is not None:
            siguiente = subcarpeta_actual.__siguiente_subcarpeta
            subcarpeta_actual.__vaciado_recursivo()
            subcarpeta_actual.__carpeta_padre = None
            subcarpeta_actual.__siguiente_subcarpeta = None
            subcarpeta_actual = siguiente

        self.__carpeta_padre = None
        self.__primer_subcarpeta = None

    # --- Métodos Públicos Generales ---

    def renombrar_carpeta(self, nuevo_nombre: str) -> None:
        """Renombra la carpeta previa validación."""
        self.__validar_str(nuevo_nombre)
        self.nombre_carpeta = nuevo_nombre.strip()

    # --- Métodos Públicos Relacionados con el arbol Carpeta ---

    def buscar_subcarpeta_por_nombre(self, nombre: str) -> Carpeta | None:
        """Busca entre las subcarpetas directas mediante su nombre."""
        self.__validar_str(nombre)
        carpeta_actual = self.__primer_subcarpeta

        while carpeta_actual is not None:
            if carpeta_actual.nombre_carpeta == nombre:
                return carpeta_actual
            carpeta_actual = carpeta_actual.__siguiente_subcarpeta

        return None

    def buscar_subcarpeta_por_id(self, id: int) -> Carpeta | None:
        """Busca entre las subcarpetas directas mediante su ID."""
        self.__validar_id(id)
        carpeta_actual = self.__primer_subcarpeta

        while carpeta_actual is not None:
            if carpeta_actual.id == id:
                return carpeta_actual
            carpeta_actual = carpeta_actual.__siguiente_subcarpeta

        return None

    def agregar_subcarpeta(self, nueva_subcarpeta: Carpeta) -> None:
        """Agrega una subcarpeta dentro de la carpeta actual."""
        nueva_subcarpeta.__carpeta_padre = self
        nueva_subcarpeta.direccion_carpeta = (
            f"{self.direccion_carpeta}{self.separador_direccion}{nueva_subcarpeta.nombre_carpeta}"
        )

        if self.__primer_subcarpeta is None:
            self.__primer_subcarpeta = nueva_subcarpeta
        else:
            subcarpeta_actual = self.__primer_subcarpeta
            while subcarpeta_actual.__siguiente_subcarpeta is not None:
                subcarpeta_actual = subcarpeta_actual.__siguiente_subcarpeta

            subcarpeta_actual.__siguiente_subcarpeta = nueva_subcarpeta

    def extraer_subcarpeta(
        self,
         id: int
    ) -> Carpeta | None:
        """Extrae una subcarpeta por su ID (funciona como un 'cortar').
        Desconecta la carpeta del árbol actual y la retorna intacta.
        """

        self.__validar_id(id)
        carpeta_anterior: Carpeta | None = None
        carpeta_actual = self.__primer_subcarpeta

        while carpeta_actual is not None:
            if carpeta_actual.id == id:
                break
            carpeta_anterior = carpeta_actual
            carpeta_actual = carpeta_actual.__siguiente_subcarpeta

        # Si no se encontró la carpeta
        if carpeta_actual is None:
            return None

        # CASO 1: Era la primera subcarpeta de la lista
        if carpeta_anterior is None:
            self.__primer_subcarpeta = carpeta_actual.__siguiente_subcarpeta
        # CASO 2: Estaba en el medio o al final
        else:
            carpeta_anterior.__siguiente_subcarpeta = (
                carpeta_actual.__siguiente_subcarpeta
            )

        # Aislamos la carpeta rompiendo sus conexiones anteriores
        carpeta_actual.__siguiente_subcarpeta = None
        carpeta_actual.__carpeta_padre = None
        return carpeta_actual


    def eliminar_subcarpeta_irreversible (self) -> None:
        """Elimina la carpeta de forma irreversible eliminando la memoria RAM."""
        self.__vaciado_recursivo()

