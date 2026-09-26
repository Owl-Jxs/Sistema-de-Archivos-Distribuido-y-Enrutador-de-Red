# Carpeta.py
from __future__ import annotations
from typing import Callable

class Carpeta:
    """Nodo de un árbol de carpetas con hijos directos enlazados entre sí."""

    separador_direccion = "/"

    def __init__(
        self,
        id: int,
        nombre_carpeta: str,
        *,
        direccion_carpeta: str | None,
        carpeta_padre: Carpeta | None = None,
        primer_subcarpeta: Carpeta | None = None,
        siguiente_subcarpeta: Carpeta | None = None,
    ) -> None:
        self.__validar_id(id)
        self.__validar_str(nombre_carpeta)

        # son atributos estrictamente privados
        self.__id: int = id
        self.__nombre_carpeta: str = nombre_carpeta.strip()
        self.__direccion_carpeta: str = direccion_carpeta.strip()

        self.__carpeta_padre: Carpeta | None = carpeta_padre
        self.__primer_subcarpeta: Carpeta | None = primer_subcarpeta
        self.__siguiente_subcarpeta: Carpeta | None = siguiente_subcarpeta

    # --- Properties (Getters Pythonicos) ---

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nombre_carpeta(self) -> str:
        return self.__nombre_carpeta

    @property
    def direccion_carpeta(self) -> str:
        return self.__direccion_carpeta

    @property
    def carpeta_padre(self) -> Carpeta | None:
        return self.__carpeta_padre

    # --- Validaciones y utilidades privadas ---

    def __validar_str(self, entrada: str | None) -> None:
        if not isinstance(entrada, str) or not entrada.strip():
            raise ValueError("El texto debe ser una cadena no vacía.")

    def __validar_id(self, id: int | None) -> None:
        if not isinstance(id, int) or isinstance(id, bool) or id < 0:
            raise ValueError("El ID debe ser un entero no negativo.")

    def __actualizar_direcciones_descendientes(self) -> None:
        """Recalcula las rutas de todos los hijos a partir de esta carpeta."""
        hijo = self.__primer_subcarpeta
        while hijo is not None:
            base = self.__direccion_carpeta.rstrip(self.separador_direccion)
            # Modificamos el atributo privado directamente ya que estamos dentro de la clase
            hijo.__direccion_carpeta = f"{base}{self.separador_direccion}{hijo.__nombre_carpeta}"
            hijo.__actualizar_direcciones_descendientes()
            hijo = hijo.__siguiente_subcarpeta

    def __vaciado_recursivo(self) -> None:
        """Rompe las conexiones de todos los descendientes de esta carpeta."""
        hijo = self.__primer_subcarpeta
        while hijo is not None:
            siguiente = hijo.__siguiente_subcarpeta
            hijo.__vaciado_recursivo()
            hijo = siguiente

        self.__carpeta_padre = None
        self.__primer_subcarpeta = None
        self.__siguiente_subcarpeta = None


    def __clonar_recursivo(self, id_actual: int) -> tuple['Carpeta', int]:
        """Método privado que clona esta instancia exacta y a todos sus descendientes."""

        #Creamos la copia de ESTA carpeta (self)
        copia = Carpeta(
            id=id_actual,
            nombre_carpeta=self.nombre_carpeta,
            direccion_carpeta=self.direccion_carpeta
        )

        # El siguiente ID que podrá usar el primer hijo
        siguiente_id = id_actual + 1

        # Recorremos los hijos de ESTA carpeta
        hijo_actual = self.__primer_subcarpeta

        while hijo_actual is not None:
            # Llamada recursiva al hijo: le pasamos el ID disponible y nos devuelve en qué número terminó
            copia_hijo, siguiente_id = hijo_actual.__clonar_recursivo(siguiente_id)

            copia.agregar_subcarpeta(copia_hijo)
            hijo_actual = hijo_actual.__siguiente_subcarpeta

        # Retornamos nuestra copia, y el número en el que quedó el contador
        return copia, siguiente_id

    # --- Operaciones sobre la carpeta actual ---

    def renombrar_carpeta(self, nuevo_nombre: str) -> None:
        """Actúa como el 'setter' seguro para el nombre de la carpeta."""
        self.__validar_str(nuevo_nombre)
        nuevo_nombre = nuevo_nombre.strip()

        if self.__carpeta_padre is not None:
            existente = self.__carpeta_padre.buscar_subcarpeta_por_nombre(nuevo_nombre)
            if existente is not None and existente is not self:
                raise ValueError("Ya existe una subcarpeta con ese nombre en el padre.")

            base = self.__carpeta_padre.direccion_carpeta.rstrip(self.separador_direccion)
            self.__direccion_carpeta = f"{base}{self.separador_direccion}{nuevo_nombre}"

        self.__nombre_carpeta = nuevo_nombre
        self.__actualizar_direcciones_descendientes()

    def listar_contenido(self) -> list[Carpeta]:
        contenido: list[Carpeta] = []
        actual = self.__primer_subcarpeta
        while actual is not None:
            contenido.append(actual)
            actual = actual.__siguiente_subcarpeta
        return contenido

    def buscar_subcarpeta_por_nombre(self, nombre: str) -> Carpeta | None:
        self.__validar_str(nombre)
        nombre = nombre.strip()
        actual = self.__primer_subcarpeta
        while actual is not None:
            if actual.nombre_carpeta == nombre:
                return actual
            actual = actual.__siguiente_subcarpeta
        return None

    def buscar_subcarpeta_por_id(self, id: int) -> Carpeta | None:
        self.__validar_id(id)
        actual = self.__primer_subcarpeta
        while actual is not None:
            if actual.id == id:
                return actual
            actual = actual.__siguiente_subcarpeta
        return None

    def agregar_subcarpeta(self, nueva_subcarpeta: Carpeta) -> None:

        if not isinstance(nueva_subcarpeta, Carpeta):
            raise TypeError("La subcarpeta debe ser una instancia de Carpeta.")
        if nueva_subcarpeta.__carpeta_padre is not None:
            raise ValueError("Extrae la carpeta de su padre antes de moverla.")
        if nueva_subcarpeta.__siguiente_subcarpeta is not None:
            raise ValueError("La carpeta todavía está enlazada con otra hermana.")
        if self.buscar_subcarpeta_por_nombre(nueva_subcarpeta.nombre_carpeta):
            raise ValueError("Ya existe una subcarpeta con ese nombre en esta carpeta.")
        if self.buscar_subcarpeta_por_id(nueva_subcarpeta.id):
            raise ValueError("Ya existe una subcarpeta con ese ID en esta carpeta.")

        actual: Carpeta | None = self
        while actual is not None:
            if actual is nueva_subcarpeta:
                raise ValueError("No se puede agregar una carpeta dentro de sí misma.")
            actual = actual.__carpeta_padre

        if self.__primer_subcarpeta is None:
            self.__primer_subcarpeta = nueva_subcarpeta
        else:
            actual = self.__primer_subcarpeta
            while actual.__siguiente_subcarpeta is not None:
                actual = actual.__siguiente_subcarpeta
            actual.__siguiente_subcarpeta = nueva_subcarpeta

        nueva_subcarpeta.__carpeta_padre = self
        base = self.__direccion_carpeta.rstrip(self.separador_direccion)
        nueva_subcarpeta.__direccion_carpeta = f"{base}{self.separador_direccion}{nueva_subcarpeta.nombre_carpeta}"
        nueva_subcarpeta.__actualizar_direcciones_descendientes()

    def eliminar_subcarpeta_irreversible(self) -> None:
        """Desconecta esta carpeta del árbol (si está conectada) y destruye su contenido."""

        if self.__carpeta_padre is not None:
            self.__carpeta_padre.extraer_subcarpeta(self.id)

        self.__vaciado_recursivo()

# ---------------------- Metodos Para Portapapeles de carpeta ----------------------

    def extraer_subcarpeta(self, id: int) -> Carpeta:
        """Desconecta y devuelve una subcarpeta. Lanza error si no existe."""
        self.__validar_id(id)
        anterior: Carpeta | None = None
        actual = self.__primer_subcarpeta

        while actual is not None and actual.id != id:
            anterior = actual
            actual = actual.__siguiente_subcarpeta

        if actual is None:
            raise ValueError(f"No se encontró ninguna subcarpeta con el ID {id} para extraer.")

        if anterior is None:
            self.__primer_subcarpeta = actual.__siguiente_subcarpeta
        else:
            anterior.__siguiente_subcarpeta = actual.__siguiente_subcarpeta

        return actual

    def clonar_subcarpeta(self, id: int, primer_nuevo_id: int) -> tuple['Carpeta', int]:
        """Busca una subcarpeta directa por ID y delega la clonación a ella."""
        self.__validar_id(id)

        #Buscamos la subcarpeta objetivo
        actual = self.__primer_subcarpeta
        while actual is not None and actual.id != id:
            actual = actual.__siguiente_subcarpeta

        if actual is None:
            raise ValueError(f"No se encontró ninguna subcarpeta con el ID {id} para clonar.")

        # Una vez encontrada, le decimos AL objeto actual que se clone a sí mismo.
        # Le pasamos el ID y él nos devolverá su propia tupla (clon, siguiente_id).
        return actual.__clonar_recursivo(primer_nuevo_id)

    def pegar_subcarpeta (self, carpeta : Carpeta) -> None:
        carpeta.__carpeta_padre = self
        carpeta.__siguiente_subcarpeta = None
        hijos : carpeta = self.__primer_subcarpeta

        while hijos is not None:
            hijos = hijos.__siguiente_subcarpeta

        hijos.__siguiente_subcarpeta = carpeta

