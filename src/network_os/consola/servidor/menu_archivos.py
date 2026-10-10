from __future__ import annotations

from ...logic.controller.servidor.servidor import Servidor
from ...logic.model.archivo.archivo import Archivo
from ...logic.structure.carpeta.carpeta import Carpeta
from ..entrada import leer_opcion, pausar


class MenuArchivos:
    """Presenta las operaciones del repositorio del servidor activo."""

    def __init__(self, servidor: Servidor) -> None:
        if not isinstance(servidor, Servidor):
            raise TypeError("El servidor debe ser una instancia de Servidor.")
        self.__servidor = servidor

    def menu_archivos(self) -> None:
        while True:
            actual = self.__servidor.obtener_carpeta_actual()
            print(f"\n=== ARCHIVOS Y CARPETAS | {actual.direccion_carpeta} ===")
            print("1. Listar contenido actual")
            print("2. Entrar / subir / ir a raiz")
            print("3. Crear carpeta")
            print("4. Crear archivo")
            print("5. Buscar archivo recursivamente")
            print("6. Imprimir arbol indentado")
            print("7. Eliminar archivo o carpeta")
            print("0. Volver")
            opcion = leer_opcion(["0", "1", "2", "3", "4", "5", "6", "7"])
            if opcion == "0":
                return

            try:
                if opcion == "1":
                    self.listar_contenido()
                elif opcion == "2":
                    self.navegar()
                elif opcion == "3":
                    self.crear_carpeta()
                elif opcion == "4":
                    self.crear_archivo()
                elif opcion == "5":
                    self.buscar_archivo()
                elif opcion == "6":
                    self.imprimir_arbol()
                elif opcion == "7":
                    self.eliminar_elemento()
            except (ValueError, TypeError, OSError) as error:
                print(f"No se pudo completar la operacion: {error}")
            pausar()

    def listar_contenido(self) -> None:
        elementos = self.__servidor.listar_contenido()
        if not elementos:
            print("La carpeta actual esta vacia.")
            return
        for elemento in elementos:
            if isinstance(elemento, Carpeta):
                print(f"[Carpeta] ID {elemento.id} | {elemento.nombre_carpeta}")
            else:
                print(f"[Archivo] ID {elemento.id} | {elemento.nombre}")

    def navegar(self) -> None:
        print("1. Entrar a una subcarpeta")
        print("2. Subir al directorio padre")
        print("3. Ir a la raiz")
        print("0. Cancelar")
        opcion = leer_opcion(["0", "1", "2", "3"])
        if opcion == "0":
            return
        if opcion == "1":
            nombre = input("Nombre de la subcarpeta: ").strip()
            self.__servidor.entrar_subcarpeta(nombre)
        elif opcion == "2":
            self.__servidor.subir_nivel()
        else:
            self.__servidor.volver_a_raiz()
        actual = self.__servidor.obtener_carpeta_actual()
        print(f"Carpeta actual: {actual.direccion_carpeta}")

    def crear_carpeta(self) -> None:
        nombre = input("Nombre de la nueva carpeta: ").strip()
        carpeta = self.__servidor.crear_subcarpeta(nombre)
        self.__servidor.guardar_estado()
        print(f"Carpeta '{carpeta.nombre_carpeta}' creada con ID {carpeta.id}.")

    def crear_archivo(self) -> None:
        nombre = input("Nombre del nuevo archivo: ").strip()
        contenido = input("Contenido del archivo (puede estar vacio): ")
        archivo = self.__servidor.crear_nuevo_archivo(nombre, contenido)
        self.__servidor.guardar_estado()
        print(f"Archivo '{archivo.nombre}' creado con ID {archivo.id}.")

    def buscar_archivo(self) -> None:
        nombre = input("Nombre del archivo a buscar desde la raiz: ").strip()
        archivo = self.__servidor.buscar_archivo(nombre)
        if archivo is None:
            print(f"No se encontro el archivo '{nombre}'.")
        else:
            print(f"Archivo encontrado: {archivo.nombre} | ID {archivo.id}")
            print(f"Ultima modificacion: {archivo.ultima_modificacion}")

    def imprimir_arbol(self) -> None:
        self.__servidor.mostrar_arbol()

    def eliminar_elemento(self) -> None:
        elementos = self.__servidor.listar_contenido()
        if not elementos:
            print("La carpeta actual esta vacia.")
            return
        self.listar_contenido()
        print("1. Eliminar archivo")
        print("2. Eliminar carpeta y todo su contenido")
        print("0. Cancelar")
        opcion = leer_opcion(["0", "1", "2"])
        if opcion == "0":
            return
        tipo = Archivo if opcion == "1" else Carpeta
        id_elemento = int(input("ID del elemento en la carpeta actual: ").strip())
        elemento = next(
            (item for item in elementos if isinstance(item, tipo) and item.id == id_elemento),
            None,
        )
        if elemento is None:
            raise ValueError("No existe un elemento de ese tipo e ID en la carpeta actual.")

        nombre = elemento.nombre if isinstance(elemento, Archivo) else elemento.nombre_carpeta
        alcance = " y todo su contenido" if isinstance(elemento, Carpeta) else ""
        confirmacion = leer_opcion(
            ["s", "S", "n", "N"], f"¿Eliminar '{nombre}'{alcance}? (s/n): ",
        ).lower()
        if confirmacion != "s":
            print("Eliminacion cancelada.")
            return
        if isinstance(elemento, Archivo):
            self.__servidor.eliminar_archivo(id_elemento)
        else:
            self.__servidor.eliminar_subcarpeta(id_elemento)
        self.__servidor.guardar_estado()
        print(f"'{nombre}' eliminado correctamente.")
