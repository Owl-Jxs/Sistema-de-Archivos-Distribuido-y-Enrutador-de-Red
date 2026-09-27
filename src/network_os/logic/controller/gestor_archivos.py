from __future__ import annotations

from typing import Literal

from ..model.archivo.archivo import Archivo
from ..structure.carpeta.carpeta import Carpeta


OperacionPortapapeles = Literal["Cortar", "Copiar"]
ElementoPortapapeles = Carpeta | Archivo


class GestorArchivos:
    """Controla la navegacion y las operaciones del arbol de archivos."""

    CORTAR = "Cortar"
    COPIAR = "Copiar"

    def __init__(self, nombre_repertorio: str) -> None:
        self.__validar_str(nombre_repertorio)
        self.__nombre_repertorio = nombre_repertorio.strip()
        self.__raiz = Carpeta(id=0, nombre_carpeta=self.__nombre_repertorio)
        self.__carpeta_actual = self.__raiz
        self.__siguiente_id = 1

        self.__elemento_portapapeles: ElementoPortapapeles | None = None
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
        elemento = self.__elemento_portapapeles
        if elemento is not None and self.__operacion_portapapeles == self.CORTAR:
            if self.__carpeta_origen is None:
                raise RuntimeError("El corte pendiente no tiene una carpeta de origen.")

            if self.__pertenece_al_arbol(self.__carpeta_origen):
                if isinstance(elemento, Carpeta):
                    self.__carpeta_origen.agregar_subcarpeta(elemento)
                else:
                    self.__carpeta_origen.agregar_archivo(elemento)
            elif isinstance(elemento, Carpeta):
                elemento.eliminar_subcarpeta_irreversible()

        self.__limpiar_portapapeles()

    def __pertenece_al_arbol(self, carpeta: Carpeta) -> bool:
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

    def listar_subcarpetas(self) -> list[Carpeta]:
        return self.__carpeta_actual.listar_subcarpetas()

    def listar_archivos(self) -> list[Archivo]:
        return self.__carpeta_actual.listar_archivos()

    def listar_elementos(self) -> list[Carpeta | Archivo]:
        return self.__carpeta_actual.listar_elementos()

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

        self.__elemento_portapapeles = self.__carpeta_actual.extraer_subcarpeta(id)
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
        if not isinstance(self.__elemento_portapapeles, Carpeta):
            raise ValueError("El portapapeles no contiene una subcarpeta.")

        self.__carpeta_actual.pegar_subcarpeta(self.__elemento_portapapeles)
        self.__limpiar_portapapeles()

    def crear_nuevo_archivo(
        self, nombre: str, contenido: object = None
    ) -> Archivo:
        self.__validar_str(nombre)
        nuevo_archivo = Archivo(
            id=self.__siguiente_id,
            nombre=nombre.strip(),
            contenido=contenido,
        )
        self.__carpeta_actual.agregar_archivo(nuevo_archivo)
        self.__siguiente_id += 1
        return nuevo_archivo

    def agregar_archivo(self, nombre: str, contenido: object = None) -> Archivo:
        """Alias de crear_nuevo_archivo para conservar el nombre del UML."""
        return self.crear_nuevo_archivo(nombre, contenido)

    def renombrar_archivo(self, id: int, nuevo_nombre: str) -> None:
        self.__validar_id(id)
        self.__validar_str(nuevo_nombre)
        self.__carpeta_actual.renombrar_archivo(id, nuevo_nombre)

    def actualizar_contenido_archivo(self, id: int, contenido: object) -> None:
        self.__validar_id(id)
        archivo = self.__carpeta_actual.buscar_archivo_por_id(id)
        if archivo is None:
            raise ValueError(f"No se encontro ningun archivo con el ID {id}.")
        archivo.actualizar_contenido(contenido)

    def eliminar_archivo(self, id: int) -> None:
        self.__validar_id(id)
        self.__carpeta_actual.eliminar_archivo(id)

    def extraer_archivo(self, id: int) -> None:
        """Corta un archivo directo y lo guarda en el portapapeles."""
        self.__validar_id(id)
        if self.__carpeta_actual.buscar_archivo_por_id(id) is None:
            raise ValueError(f"No se encontro ningun archivo con el ID {id}.")
        self.__preparar_nueva_operacion_portapapeles()

        self.__elemento_portapapeles = self.__carpeta_actual.extraer_archivo(id)
        self.__operacion_portapapeles = self.CORTAR
        self.__carpeta_origen = self.__carpeta_actual

    def cortar_archivo(self, id: int) -> None:
        self.extraer_archivo(id)

    def copiar_archivo(self, id: int) -> None:
        self.__validar_id(id)
        if self.__carpeta_actual.buscar_archivo_por_id(id) is None:
            raise ValueError(f"No se encontro ningun archivo con el ID {id}.")
        self.__preparar_nueva_operacion_portapapeles()

        self.__elemento_portapapeles = self.__carpeta_actual.clonar_archivo(
            id, self.__siguiente_id
        )
        self.__siguiente_id += 1
        self.__operacion_portapapeles = self.COPIAR
        self.__carpeta_origen = self.__carpeta_actual

    def pegar_archivo(self) -> None:
        if not isinstance(self.__elemento_portapapeles, Archivo):
            raise ValueError("El portapapeles no contiene un archivo.")

        self.__carpeta_actual.pegar_archivo(self.__elemento_portapapeles)
        self.__limpiar_portapapeles()

    def pegar_elemento(self) -> None:
        if isinstance(self.__elemento_portapapeles, Carpeta):
            self.pegar_subcarpeta()
        elif isinstance(self.__elemento_portapapeles, Archivo):
            self.pegar_archivo()
        else:
            raise ValueError("No hay ningun elemento en el portapapeles.")
