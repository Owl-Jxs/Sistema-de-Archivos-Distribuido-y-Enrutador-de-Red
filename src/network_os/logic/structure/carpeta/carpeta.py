from __future__ import annotations
from ...model.archivo.archivo import Archivo
class Carpeta:
    """Nodo de un arbol de carpetas con archivos y subcarpetas enlazadas."""

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
        archivos: list[Archivo] | None = None,
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
        self.__archivos = self.__validar_archivos(archivos)

        self.__actualizar_padres_y_direcciones_descendientes()
        self.__validar_nombres_directos()
        self.__obtener_ids_subarbol()

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

    @staticmethod
    def __validar_archivos(archivos: list[Archivo] | None) -> list[Archivo]:
        if archivos is None:
            return []
        if not isinstance(archivos, list):
            raise TypeError("Los archivos deben proporcionarse en una lista.")
        if any(not isinstance(archivo, Archivo) for archivo in archivos):
            raise TypeError("Todos los elementos deben ser instancias de Archivo.")
        return list(archivos)

    def __validar_nombres_directos(self) -> None:
        nombres: set[str] = set()

        for subcarpeta in self.listar_subcarpetas():
            if subcarpeta.nombre_carpeta in nombres:
                raise ValueError("Existen elementos con nombres repetidos.")
            nombres.add(subcarpeta.nombre_carpeta)

        for archivo in self.__archivos:
            if archivo.nombre in nombres:
                raise ValueError("Existen elementos con nombres repetidos.")
            nombres.add(archivo.nombre)

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

        self.__archivos.clear()
        self.__carpeta_padre = None
        self.__primer_subcarpeta = None
        self.__siguiente_subcarpeta = None

    def __clonar_recursivo(self, id_actual: int) -> tuple[Carpeta, int]:
        copia = Carpeta(id=id_actual, nombre_carpeta=self.__nombre_carpeta)
        siguiente_id = id_actual + 1

        for archivo in self.__archivos:
            copia.agregar_archivo(archivo.clonar(siguiente_id))
            siguiente_id += 1

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
            nodos_visitados.add(identidad)

            ids_directos = [carpeta.__id]
            ids_directos.extend(archivo.id for archivo in carpeta.__archivos)
            for id_elemento in ids_directos:
                if id_elemento in ids_encontrados:
                    raise ValueError("El arbol contiene IDs repetidos.")
                ids_encontrados.add(id_elemento)

            pendientes.extend(carpeta.listar_subcarpetas())

        return ids_encontrados

    def __obtener_raiz(self) -> Carpeta:
        raiz = self
        while raiz.__carpeta_padre is not None:
            raiz = raiz.__carpeta_padre
        return raiz

    def renombrar_carpeta(self, nuevo_nombre: str) -> None:
        self.__validar_str(nuevo_nombre)
        nombre_limpio = nuevo_nombre.strip()

        if self.__carpeta_padre is not None:
            existente = self.__carpeta_padre.buscar_subcarpeta_por_nombre(nombre_limpio)
            archivo = self.__carpeta_padre.buscar_archivo_por_nombre(nombre_limpio)
            if (existente is not None and existente is not self) or archivo is not None:
                raise ValueError("Ya existe un elemento con ese nombre en el padre.")

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

    def listar_subcarpetas(self) -> list[Carpeta]:
        subcarpetas: list[Carpeta] = []
        actual = self.__primer_subcarpeta
        while actual is not None:
            subcarpetas.append(actual)
            actual = actual.__siguiente_subcarpeta
        return subcarpetas

    def listar_contenido(self) -> list[Carpeta]:
        """Conserva el nombre historico para listar las subcarpetas directas."""
        return self.listar_subcarpetas()

    def listar_archivos(self) -> list[Archivo]:
        return list(self.__archivos)

    def listar_elementos(self) -> list[Carpeta | Archivo]:
        return [*self.listar_subcarpetas(), *self.__archivos]

    def buscar_subcarpeta_por_nombre(self, nombre: str) -> Carpeta | None:
        self.__validar_str(nombre)
        nombre_limpio = nombre.strip()

        for subcarpeta in self.listar_subcarpetas():
            if subcarpeta.__nombre_carpeta == nombre_limpio:
                return subcarpeta
        return None

    def buscar_subcarpeta_por_id(self, id: int) -> Carpeta | None:
        self.__validar_id(id)

        for subcarpeta in self.listar_subcarpetas():
            if subcarpeta.__id == id:
                return subcarpeta
        return None

    def agregar_subcarpeta(self, nueva_subcarpeta: Carpeta) -> None:
        if not isinstance(nueva_subcarpeta, Carpeta):
            raise TypeError("La subcarpeta debe ser una instancia de Carpeta.")
        if nueva_subcarpeta.__carpeta_padre is not None:
            raise ValueError("Extrae la carpeta de su padre antes de moverla.")
        if nueva_subcarpeta.__siguiente_subcarpeta is not None:
            raise ValueError("La carpeta todavia esta enlazada con otra hermana.")
        if (
            self.buscar_subcarpeta_por_nombre(nueva_subcarpeta.nombre_carpeta)
            or self.buscar_archivo_por_nombre(nueva_subcarpeta.nombre_carpeta)
        ):
            raise ValueError("Ya existe un elemento con ese nombre en esta carpeta.")

        ancestro: Carpeta | None = self
        while ancestro is not None:
            if ancestro is nueva_subcarpeta:
                raise ValueError("No se puede crear un ciclo entre carpetas.")
            ancestro = ancestro.__carpeta_padre

        ids_existentes = self.__obtener_raiz().__obtener_ids_subarbol()
        ids_nuevos = nueva_subcarpeta.__obtener_ids_subarbol()
        if ids_existentes & ids_nuevos:
            raise ValueError("Ya existe un elemento con uno de esos IDs en el arbol.")

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

    def clonar_subarbol(self, primer_nuevo_id: int) -> tuple[Carpeta, int]:
        """Clona esta carpeta completa usando una secuencia nueva de IDs."""
        self.__validar_id(primer_nuevo_id)
        return self.__clonar_recursivo(primer_nuevo_id)

    def pegar_subcarpeta(self, carpeta: Carpeta) -> None:
        self.agregar_subcarpeta(carpeta)

    def agregar_archivo(self, archivo: Archivo) -> None:
        if not isinstance(archivo, Archivo):
            raise TypeError("El archivo debe ser una instancia de Archivo.")
        if (
            self.buscar_archivo_por_nombre(archivo.nombre)
            or self.buscar_subcarpeta_por_nombre(archivo.nombre)
        ):
            raise ValueError("Ya existe un elemento con ese nombre en esta carpeta.")

        ids_existentes = self.__obtener_raiz().__obtener_ids_subarbol()
        if archivo.id in ids_existentes:
            raise ValueError("Ya existe un elemento con ese ID en el arbol.")

        self.__archivos.append(archivo)

    def buscar_archivo_por_nombre(self, nombre: str) -> Archivo | None:
        self.__validar_str(nombre)
        nombre_limpio = nombre.strip()

        for archivo in self.__archivos:
            if archivo.nombre == nombre_limpio:
                return archivo
        return None

    def buscar_archivo_recursivo(self, nombre: str) -> Archivo | None:
        """Busca un archivo navegando todo el subarbol en profundidad."""
        self.__validar_str(nombre)
        nombre_limpio = nombre.strip()

        encontrado = self.buscar_archivo_por_nombre(nombre_limpio)
        if encontrado is not None:
            return encontrado

        for subcarpeta in self.listar_subcarpetas():
            encontrado = subcarpeta.buscar_archivo_recursivo(nombre_limpio)
            if encontrado is not None:
                return encontrado
        return None

    def buscar_archivo_por_id(self, id: int) -> Archivo | None:
        self.__validar_id(id)

        for archivo in self.__archivos:
            if archivo.id == id:
                return archivo
        return None

    def renombrar_archivo(self, id: int, nuevo_nombre: str) -> None:
        self.__validar_id(id)
        self.__validar_str(nuevo_nombre)
        archivo = self.buscar_archivo_por_id(id)
        if archivo is None:
            raise ValueError(f"No se encontro ningun archivo con el ID {id}.")

        nombre_limpio = nuevo_nombre.strip()
        existente = self.buscar_archivo_por_nombre(nombre_limpio)
        if (
            (existente is not None and existente is not archivo)
            or self.buscar_subcarpeta_por_nombre(nombre_limpio) is not None
        ):
            raise ValueError("Ya existe un elemento con ese nombre en esta carpeta.")

        archivo.renombrar(nombre_limpio)

    def extraer_archivo(self, id: int) -> Archivo:
        self.__validar_id(id)
        archivo = self.buscar_archivo_por_id(id)
        if archivo is None:
            raise ValueError(f"No se encontro ningun archivo con el ID {id}.")

        self.__archivos.remove(archivo)
        return archivo

    def eliminar_archivo(self, id: int) -> Archivo:
        return self.extraer_archivo(id)

    def clonar_archivo(self, id: int, nuevo_id: int) -> Archivo:
        self.__validar_id(nuevo_id)
        archivo = self.buscar_archivo_por_id(id)
        if archivo is None:
            raise ValueError(f"No se encontro ningun archivo con el ID {id}.")
        return archivo.clonar(nuevo_id)

    def pegar_archivo(self, archivo: Archivo) -> None:
        self.agregar_archivo(archivo)
