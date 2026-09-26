from __future__ import annotations

class Carpeta:
    """Nodo de un arbol de carpetas con hijos directos enlazados."""

    separador_direccion = "/"

    def __init__(
        self,
        id: int,
        nombre_carpeta: str,
        *,
        direccion_carpeta: str | None = None,
        carpeta_padre: Carpeta | None = None,
        primer_subcarpeta: Carpeta | None = None,
        siguiente_subcarpeta: Carpeta | None = None,
    ) -> None:
        self.__validar_id(id)
        self.__validar_str(nombre_carpeta)
        self.__validar_carpeta_opcional(carpeta_padre, "carpeta_padre")
        self.__validar_carpeta_opcional(primer_subcarpeta, "primer_subcarpeta")
        self.__validar_carpeta_opcional(siguiente_subcarpeta, "siguiente_subcarpeta")

        nombre_limpio = nombre_carpeta.strip()
        if direccion_carpeta is not None:
            self.__validar_str(direccion_carpeta)

        self.__id = id
        self.__nombre_carpeta = nombre_limpio
        self.__direccion_carpeta = (
            direccion_carpeta.strip()
            if direccion_carpeta is not None
            else f"{self.separador_direccion}{nombre_limpio}"
        )
        self.__carpeta_padre = carpeta_padre
        self.__primer_subcarpeta = primer_subcarpeta
        self.__siguiente_subcarpeta = siguiente_subcarpeta

        self.__actualizar_padres_y_direcciones_descendientes()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def nombre_carpeta(self) -> str:
        return self.__nombre_carpeta

    @property
    def direccion_carpeta(self) -> str:
        """Direccion logica; no representa una ruta fisica del sistema."""
        return self.__direccion_carpeta

    @property
    def carpeta_padre(self) -> Carpeta | None:
        return self.__carpeta_padre

    @staticmethod
    def __validar_str(entrada: str | None) -> None:
        if not isinstance(entrada, str) or not entrada.strip():
            raise ValueError("El texto debe ser una cadena no vacia.")

    @staticmethod
    def __validar_id(id: int | None) -> None:
        if not isinstance(id, int) or isinstance(id, bool) or id < 0:
            raise ValueError("El ID debe ser un entero no negativo.")

    @staticmethod
    def __validar_carpeta_opcional(
        carpeta: Carpeta | None, nombre_parametro: str
    ) -> None:
        if carpeta is not None and not isinstance(carpeta, Carpeta):
            raise TypeError(f"{nombre_parametro} debe ser una Carpeta o None.")

    def __actualizar_padres_y_direcciones_descendientes(self) -> None:
        hijo = self.__primer_subcarpeta
        visitados: set[int] = set()

        while hijo is not None:
            identidad = id(hijo)
            if identidad in visitados or hijo is self:
                raise ValueError("La lista enlazada de subcarpetas contiene un ciclo.")
            visitados.add(identidad)

            hijo.__carpeta_padre = self
            base = self.__direccion_carpeta.rstrip(self.separador_direccion)
            hijo.__direccion_carpeta = (
                f"{base}{self.separador_direccion}{hijo.__nombre_carpeta}"
            )
            hijo.__actualizar_padres_y_direcciones_descendientes()
            hijo = hijo.__siguiente_subcarpeta

    def __vaciado_recursivo(self) -> None:
        hijo = self.__primer_subcarpeta
        while hijo is not None:
            siguiente = hijo.__siguiente_subcarpeta
            hijo.__vaciado_recursivo()
            hijo = siguiente

        self.__carpeta_padre = None
        self.__primer_subcarpeta = None
        self.__siguiente_subcarpeta = None

    def __clonar_recursivo(self, id_actual: int) -> tuple[Carpeta, int]:
        copia = Carpeta(id=id_actual, nombre_carpeta=self.__nombre_carpeta)
        siguiente_id = id_actual + 1

        hijo_actual = self.__primer_subcarpeta
        while hijo_actual is not None:
            copia_hijo, siguiente_id = hijo_actual.__clonar_recursivo(siguiente_id)
            copia.agregar_subcarpeta(copia_hijo)
            hijo_actual = hijo_actual.__siguiente_subcarpeta

        return copia, siguiente_id

    def __obtener_ids_subarbol(self) -> set[int]:
        ids_encontrados: set[int] = set()
        nodos_visitados: set[int] = set()
        pendientes = [self]

        while pendientes:
            carpeta = pendientes.pop()
            identidad = id(carpeta)
            if identidad in nodos_visitados:
                raise ValueError("El arbol de carpetas contiene un ciclo.")
            if carpeta.__id in ids_encontrados:
                raise ValueError("El arbol de carpetas contiene IDs repetidos.")

            nodos_visitados.add(identidad)
            ids_encontrados.add(carpeta.__id)
            pendientes.extend(carpeta.listar_contenido())

        return ids_encontrados

    def renombrar_carpeta(self, nuevo_nombre: str) -> None:
        self.__validar_str(nuevo_nombre)
        nombre_limpio = nuevo_nombre.strip()

        if self.__carpeta_padre is not None:
            existente = self.__carpeta_padre.buscar_subcarpeta_por_nombre(nombre_limpio)
            if existente is not None and existente is not self:
                raise ValueError("Ya existe una subcarpeta con ese nombre en el padre.")

            base = self.__carpeta_padre.direccion_carpeta.rstrip(
                self.separador_direccion
            )
            self.__direccion_carpeta = (
                f"{base}{self.separador_direccion}{nombre_limpio}"
            )
        else:
            self.__direccion_carpeta = f"{self.separador_direccion}{nombre_limpio}"

        self.__nombre_carpeta = nombre_limpio
        self.__actualizar_padres_y_direcciones_descendientes()

    def listar_contenido(self) -> list[Carpeta]:
        contenido: list[Carpeta] = []
        actual = self.__primer_subcarpeta
        while actual is not None:
            contenido.append(actual)
            actual = actual.__siguiente_subcarpeta
        return contenido

    def buscar_subcarpeta_por_nombre(self, nombre: str) -> Carpeta | None:
        self.__validar_str(nombre)
        nombre_limpio = nombre.strip()
        actual = self.__primer_subcarpeta

        while actual is not None:
            if actual.__nombre_carpeta == nombre_limpio:
                return actual
            actual = actual.__siguiente_subcarpeta
        return None

    def buscar_subcarpeta_por_id(self, id: int) -> Carpeta | None:
        self.__validar_id(id)
        actual = self.__primer_subcarpeta

        while actual is not None:
            if actual.__id == id:
                return actual
            actual = actual.__siguiente_subcarpeta
        return None

    def agregar_subcarpeta(self, nueva_subcarpeta: Carpeta) -> None:
        if not isinstance(nueva_subcarpeta, Carpeta):
            raise TypeError("La subcarpeta debe ser una instancia de Carpeta.")
        if nueva_subcarpeta.__carpeta_padre is not None:
            raise ValueError("Extrae la carpeta de su padre antes de moverla.")
        if nueva_subcarpeta.__siguiente_subcarpeta is not None:
            raise ValueError("La carpeta todavia esta enlazada con otra hermana.")
        if self.buscar_subcarpeta_por_nombre(nueva_subcarpeta.nombre_carpeta):
            raise ValueError("Ya existe una subcarpeta con ese nombre en esta carpeta.")

        ancestro: Carpeta | None = self
        while ancestro is not None:
            if ancestro is nueva_subcarpeta:
                raise ValueError("No se puede crear un ciclo entre carpetas.")
            ancestro = ancestro.__carpeta_padre

        raiz = self
        while raiz.__carpeta_padre is not None:
            raiz = raiz.__carpeta_padre

        ids_existentes = raiz.__obtener_ids_subarbol()
        ids_nuevos = nueva_subcarpeta.__obtener_ids_subarbol()
        if ids_existentes & ids_nuevos:
            raise ValueError("Ya existe una carpeta con uno de esos IDs en el arbol.")

        if self.__primer_subcarpeta is None:
            self.__primer_subcarpeta = nueva_subcarpeta
        else:
            ultima = self.__primer_subcarpeta
            while ultima.__siguiente_subcarpeta is not None:
                ultima = ultima.__siguiente_subcarpeta
            ultima.__siguiente_subcarpeta = nueva_subcarpeta

        nueva_subcarpeta.__carpeta_padre = self
        base = self.__direccion_carpeta.rstrip(self.separador_direccion)
        nueva_subcarpeta.__direccion_carpeta = (
            f"{base}{self.separador_direccion}"
            f"{nueva_subcarpeta.__nombre_carpeta}"
        )
        nueva_subcarpeta.__actualizar_padres_y_direcciones_descendientes()

    def extraer_subcarpeta(self, id: int) -> Carpeta:
        """Desconecta y devuelve una subcarpeta directa sin borrar sus hijos."""
        self.__validar_id(id)
        anterior: Carpeta | None = None
        actual = self.__primer_subcarpeta

        while actual is not None and actual.__id != id:
            anterior = actual
            actual = actual.__siguiente_subcarpeta

        if actual is None:
            raise ValueError(f"No se encontro ninguna subcarpeta con el ID {id}.")

        if anterior is None:
            self.__primer_subcarpeta = actual.__siguiente_subcarpeta
        else:
            anterior.__siguiente_subcarpeta = actual.__siguiente_subcarpeta

        actual.__carpeta_padre = None
        actual.__siguiente_subcarpeta = None
        return actual

    def eliminar_subcarpeta_irreversible(self) -> None:
        """Desconecta esta carpeta y elimina todos sus enlaces internos."""
        if self.__carpeta_padre is not None:
            self.__carpeta_padre.extraer_subcarpeta(self.__id)
        self.__vaciado_recursivo()

    def clonar_subcarpeta(
        self, id: int, primer_nuevo_id: int
    ) -> tuple[Carpeta, int]:
        self.__validar_id(id)
        self.__validar_id(primer_nuevo_id)
        original = self.buscar_subcarpeta_por_id(id)

        if original is None:
            raise ValueError(f"No se encontro ninguna subcarpeta con el ID {id}.")

        return original.__clonar_recursivo(primer_nuevo_id)

    def pegar_subcarpeta(self, carpeta: Carpeta) -> None:
        """Agrega una carpeta previamente extraida o clonada."""
        self.agregar_subcarpeta(carpeta)
