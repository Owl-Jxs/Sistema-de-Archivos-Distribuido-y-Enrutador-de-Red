from __future__ import annotations

from typing import Literal

from ..structure.carpeta.carpeta import Carpeta


OperacionPortapapeles = Literal["Cortar", "Copiar"]


class GestorArchivos:
    """Controla la navegacion y las operaciones del arbol de carpetas."""

    CORTAR = "Cortar"
    COPIAR = "Copiar"

    def __init__(self, nombre_repertorio: str) -> None:
        self.__validar_str(nombre_repertorio)
        self.__nombre_repertorio = nombre_repertorio.strip()
        self.__raiz = Carpeta(id=0, nombre_carpeta=self.__nombre_repertorio)
        self.__carpeta_actual = self.__raiz
        self.__siguiente_id = 1

        # Este portapapeles se ampliara para aceptar Archivo cuando exista.
        self.__elemento_portapapeles: Carpeta | None = None
        self.__operacion_portapapeles: OperacionPortapapeles | None = None
        self.__carpeta_origen: Carpeta | None = None

    @staticmethod
    def __validar_str(entrada: str | None) -> None:
        if not isinstance(entrada, str) or not entrada.strip():
            raise ValueError("El texto debe ser una cadena no vacia.")

    @staticmethod
    def __validar_id(id: int | None) -> None:
        if not isinstance(id, int) or isinstance(id, bool) or id < 0:
            raise ValueError("El ID debe ser un entero no negativo.")

    def __preparar_nueva_operacion_portapapeles(self) -> None:
        """Restaura un corte pendiente antes de reemplazar el portapapeles."""
        if (
            self.__elemento_portapapeles is not None
            and self.__operacion_portapapeles == self.CORTAR
        ):
            if self.__carpeta_origen is None:
                raise RuntimeError("El corte pendiente no tiene una carpeta de origen.")
            if self.__pertenece_al_arbol(self.__carpeta_origen):
                self.__carpeta_origen.agregar_subcarpeta(
                    self.__elemento_portapapeles
                )
            else:
                self.__elemento_portapapeles.eliminar_subcarpeta_irreversible()

        self.__limpiar_portapapeles()

    def __pertenece_al_arbol(self, carpeta: Carpeta) -> bool:
        """Revisa que una carpeta pertenezca al arbol o si por el contrario es la raiz del mismo"""
        actual: Carpeta | None = carpeta
        while actual is not None and actual is not self.__raiz:
            actual = actual.carpeta_padre
        return actual is self.__raiz

    def __limpiar_portapapeles(self) -> None:
        self.__operacion_portapapeles = None
        self.__elemento_portapapeles = None
        self.__carpeta_origen = None

    @property
    def nombre_repertorio(self) -> str:
        return self.__nombre_repertorio

    @property
    def carpeta_actual(self) -> Carpeta:
        return self.__carpeta_actual

    @property
    def raiz(self) -> Carpeta:
        return self.__raiz

    def bajar_a_subcarpeta(self, nombre_subcarpeta: str) -> None:
        self.__validar_str(nombre_subcarpeta)
        subcarpeta = self.__carpeta_actual.buscar_subcarpeta_por_nombre(
            nombre_subcarpeta.strip()
        )

        if subcarpeta is None:
            raise ValueError(f"No existe la subcarpeta '{nombre_subcarpeta}' aqui.")
        self.__carpeta_actual = subcarpeta

    def subir_nivel(self) -> None:
        padre = self.__carpeta_actual.carpeta_padre
        if padre is not None:
            self.__carpeta_actual = padre

    def volver_a_raiz(self) -> None:
        self.__carpeta_actual = self.__raiz

    def crear_nueva_subcarpeta(self, nombre: str) -> Carpeta:
        self.__validar_str(nombre)
        nueva_carpeta = Carpeta(
            id=self.__siguiente_id,
            nombre_carpeta=nombre.strip(),
        )
        self.__carpeta_actual.agregar_subcarpeta(nueva_carpeta)
        self.__siguiente_id += 1
        return nueva_carpeta

    def renombrar_subcarpeta(self, nombre: str) -> None:
        """Renombra la carpeta en la que se encuentra actualmente el gestor."""
        self.__validar_str(nombre)
        self.__carpeta_actual.renombrar_carpeta(nombre)

        if self.__carpeta_actual is self.__raiz:
            self.__nombre_repertorio = self.__raiz.nombre_carpeta

    def eliminar_subcarpeta(self, id: int) -> None:
        self.__validar_id(id)
        subcarpeta = self.__carpeta_actual.extraer_subcarpeta(id)
        subcarpeta.eliminar_subcarpeta_irreversible()

    def extraer_subcarpeta(self, id: int) -> None:
        """Corta una subcarpeta directa y la guarda en el portapapeles."""
        self.__validar_id(id)
        if self.__carpeta_actual.buscar_subcarpeta_por_id(id) is None:
            raise ValueError(f"No se encontro ninguna subcarpeta con el ID {id}.")
        self.__preparar_nueva_operacion_portapapeles()

        self.__elemento_portapapeles = (
            self.__carpeta_actual.extraer_subcarpeta(id)
        )
        self.__operacion_portapapeles = self.CORTAR
        self.__carpeta_origen = self.__carpeta_actual

    def copiar_subcarpeta(self, id: int) -> None:
        self.__validar_id(id)
        if self.__carpeta_actual.buscar_subcarpeta_por_id(id) is None:
            raise ValueError(f"No se encontro ninguna subcarpeta con el ID {id}.")
        self.__preparar_nueva_operacion_portapapeles()

        copia, siguiente_id = self.__carpeta_actual.clonar_subcarpeta(
            id, self.__siguiente_id
        )
        self.__elemento_portapapeles = copia
        self.__siguiente_id = siguiente_id
        self.__operacion_portapapeles = self.COPIAR
        self.__carpeta_origen = self.__carpeta_actual

    def pegar_subcarpeta(self) -> None:
        if self.__elemento_portapapeles is None:
            raise ValueError("No hay ninguna subcarpeta en el portapapeles.")

        self.__carpeta_actual.pegar_subcarpeta(self.__elemento_portapapeles)
        self.__limpiar_portapapeles()
