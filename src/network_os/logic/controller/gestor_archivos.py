#Gestor de los archivos y carpetas
from structure.carpeta import carpeta
# GestorArchivos.py
from __future__ import annotations
from Carpeta import Carpeta

class GestorArchivos:
    """Clase que funciona como el controlador del árbol de carpetas."""
    CORTAR = "Cortar"
    COPIAR = "Copiar"
    def __init__(self, nombre_repertorio: str) -> None:
        self.__validar_str(nombre_repertorio)

        self.__nombre_repertorio: str = nombre_repertorio.strip()

        # Instanciación corregida (parámetros correctos y clase en mayúscula)
        self.__raiz: Carpeta = Carpeta(
            id=0,
            nombre_carpeta=self.__nombre_repertorio,
            direccion_carpeta=f"/{self.__nombre_repertorio}"
        )

        # Puntero de navegación
        self.__carpeta_actual: Carpeta = self.__raiz
        self.__siguiente_id: int = 1

        # Atributos relacionados a las operaciones de portapapeles
        self.__elemento_portapapeles: Carpeta | None = None # + Archivo en el futuro
        self.__operacion_portapapeles: CORTAR | COPIAR | None = None    # Ej: 'cortar', 'copiar'
        self.__carpeta_origen: Carpeta | None = None

    # --- Validaciones privadas ---

    def __validar_str(self, entrada: str | None) -> None:
        if not isinstance(entrada, str) or not entrada.strip():
            raise ValueError("El texto debe ser una cadena no vacía.")

    def __validar_id(self, id: int | None) -> None:
        if not isinstance(id, int) or isinstance(id, bool) or id < 0:
            raise ValueError("El ID debe ser un entero no negativo.")

    def __validar_registros_portapapeles () -> None:
        if (self.__elemento_portapapeles is not None):
            if (self.__operacion_portapapeles is self.CORTAR):
                self.__carpeta_origen.agregar_subcarpeta (self.__elemento_portapapeles)
            self.__operacion_portapapeles = None
            self.__elemento_portapapeles = None
            self.__carpeta_origen = None

   def __limpiar_portapapeles () -> None:
       self.__operacion_portapapeles = None
       self.__elemento_portapapeles = None
       self.__carpeta_origen = None

    # --- Properties (Getters) ---

    @property
   def nombre_repertorio(self) -> str:
        return self.__nombre_repertorio

    @property
   def carpeta_actual(self) -> Carpeta:
        return self.__carpeta_actual

    @property
   def raiz(self) -> Carpeta:
        return self.__raiz

    # --- Métodos de Navegación ---

   def bajar_a_subcarpeta(self, nombre_subcarpeta: str) -> None:
        """Navega hacia una subcarpeta hija dentro de la carpeta actual."""
        self.__validar_str(nombre_subcarpeta)

        subcarpeta = self.__carpeta_actual.buscar_subcarpeta_por_nombre(nombre_subcarpeta.strip())

        if subcarpeta is None:
            raise ValueError(f"No existe la subcarpeta '{nombre_subcarpeta}' aquí.")

        self.__carpeta_actual = subcarpeta

   def subir_nivel(self) -> None:
        """Navega a la carpeta padre. No hace nada si ya está en la raíz."""
        padre = self.__carpeta_actual.carpeta_padre
        if padre is not None:
            self.__carpeta_actual = padre

   def volver_a_raiz(self) -> None:
        """Reinicia la navegación al directorio principal."""
        self.__carpeta_actual = self.__raiz

    # --- Métodos de Modificacion en carpeta ---

   def crear_nueva_subcarpeta(self, nombre: str) -> None:
        """Crea una carpeta nueva dentro de la carpeta actual gestionando el ID."""
        nueva_carpeta = Carpeta(
            id=self.__siguiente_id,
            nombre_carpeta=nombre,
        )
        self.__carpeta_actual.agregar_subcarpeta(nueva_carpeta)
        self.__siguiente_id += 1

   def renombrar_subcarpeta (self, nombre : str) -> None:
        self.__validar_str (nombre)
        self.__carpeta_actual.renombrar_subcarpeta (nombre)

   def eliminar_subcarpeta (self, id : int) -> carpeta:
        self.__validar_id (id)
        return self.__carpeta_actual.extraer_subcarpeta (id)

    # --- Métodos de Portapapeles en carpeta ---

   def extraer_subcarpeta (self, id: int):
        self.__validar_id (id)
        self.__validar_registros_portapapeles ()

        self.__elemento_portapapeles = self.__carpeta_actual.extraer_subcarpeta (id)
        self.__operacion_portapapeles = self.CORTAR
        self.__carpeta_origen = self.__carpeta_actual

   def copiar_subcarpeta (self, id : int):
        self.__validar_id (id)
        self.__validar_registros_portapapeles ()

        self.__elemento_portapapeles, __siguiente_id = self.__carpeta_actual.clonar_subcarpeta (id, self.__siguiente_id)
        self.__operacion_portapapeles = self.COPIAR
        self.__carpeta_origen = self.__carpeta_actual

   def pegar_subcarpeta (self):
       self.__carpeta_actual.pegar_subcarpeta (self.__elemento_portapapeles)
       self.__limpiar_portapapeles ()



