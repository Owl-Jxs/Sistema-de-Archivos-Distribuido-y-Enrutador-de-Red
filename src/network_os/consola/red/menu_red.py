from __future__ import annotations

from ...logic.controller.grafo_red.grafoRed import GrafoRed
from ...logic.controller.servidor.servidor import Servidor
from ..entrada import leer_opcion, pausar


class MenuRed:
    """Administra la red delegando las operaciones en GrafoRed."""

    def __init__(self, grafo: GrafoRed) -> None:
        if not isinstance(grafo, GrafoRed):
            raise TypeError("El grafo debe ser una instancia de GrafoRed.")
        self.__grafo = grafo

    def menu_red(self) -> None:
        """Administra servidores, conexiones, latencias y diagnosticos de red."""
        while True:
            print("\n=== MENU DE RED ===")
            print("1. Listar servidores y conexiones")
            print("2. Agregar / eliminar servidor")
            print("3. Agregar / eliminar conexion")
            print("4. Cambiar latencia de una conexion")
            print("5. Ejecutar ping general")
            print("0. Volver al menu principal")

            opcion = leer_opcion(["0", "1", "2", "3", "4", "5"])

            if opcion == "0":
                return

            try:
                if opcion == "1":
                    self.__listar_red()

                elif opcion == "2":
                    self.__menu_servidores_red()

                elif opcion == "3":
                    self.__menu_conexiones_red()

                elif opcion == "4":
                    origen = input("Servidor de origen: ").strip()
                    destino = input("Servidor de destino: ").strip()
                    latencia = float(input("Nueva latencia en ms: ").strip())

                    self.__grafo.actualizar_latencia(
                        origen, destino, latencia
                    )
                    self.__grafo.guardar()
                    print("Latencia actualizada correctamente.")

                elif opcion == "5":
                    origen = input("Servidor desde el que realizar el ping: ").strip()
                    resultados = self.__grafo.ping_general(origen)

                    print(f"\n=== PING GENERAL DESDE {origen} ===")
                    if not resultados:
                        print("No hay otros servidores en la red.")
                    else:
                        for destino, latencia in resultados.items():
                            if latencia is None:
                                print(f"{destino}: inalcanzable")
                            else:
                                print(f"{destino}: {latencia} ms")

                if opcion in ["1", "2", "3", "4", "5"]:
                    pausar()

            except (ValueError, TypeError, OSError) as error:
                print(f"\nNo se pudo completar la operacion: {error}")
                pausar()


    def __listar_red(self) -> None:
        """Muestra todos los servidores y las conexiones sin duplicarlas."""
        vertices = self.__grafo.vertices

        if not vertices:
            print("\nNo hay servidores registrados en la red.")
            return

        print("\n=== SERVIDORES ===")
        for vertice in vertices:
            servidor = vertice.servidor
            print(f"ID: {servidor.id} | Nombre: {servidor.nombre}")

        print("\n=== CONEXIONES ===")
        conexiones_mostradas: set[tuple[str, str]] = set()

        for vertice in vertices:
            origen = vertice.servidor.nombre

            for conexion in vertice.conexiones:
                destino = conexion.destino.servidor.nombre
                identificador = tuple(sorted((origen, destino)))

                if identificador in conexiones_mostradas:
                    continue

                conexiones_mostradas.add(identificador)
                print(
                    f"{origen} <-> {destino} | "
                    f"Latencia: {conexion.latencia_ms} ms"
                )

        if not conexiones_mostradas:
            print("No hay conexiones registradas.")


    def __menu_servidores_red(self) -> None:
        """Permite agregar o eliminar servidores."""
        print("\n=== ADMINISTRAR SERVIDORES ===")
        print("1. Agregar servidor")
        print("2. Eliminar servidor")
        print("0. Cancelar")

        opcion = leer_opcion(["0", "1", "2"])

        if opcion == "0":
            return

        if opcion == "1":
            nombre = input("Nombre del nuevo servidor: ").strip()

            if not nombre:
                raise ValueError("El nombre no puede estar vacio.")

            ids = [
                vertice.servidor.id
                for vertice in self.__grafo.vertices
            ]
            nuevo_id = max(ids, default=-1) + 1

            direccion_base = self.__grafo.persistencia.ruta_conexiones_csv.parent
            servidor = Servidor(nombre, nuevo_id, direccion_base)
            self.__grafo.agregar_servidor(servidor)
            self.__grafo.guardar()

            print(
                f"Servidor '{nombre}' creado con ID {nuevo_id}."
            )

        elif opcion == "2":
            nombre = input("Nombre del servidor que desea eliminar: ").strip()
            self.__grafo.buscar_vertice(nombre)
            confirmacion = leer_opcion(
                ["s", "S", "n", "N"],
                f"¿Eliminar el servidor '{nombre}' y sus conexiones? (s/n): ",
            ).lower()
            if confirmacion != "s":
                print("Eliminacion cancelada.")
                return
            self.__grafo.eliminar_servidor(nombre)
            self.__grafo.guardar()

            print(f"Servidor '{nombre}' eliminado correctamente.")


    def __menu_conexiones_red(self) -> None:
        """Permite agregar o eliminar conexiones entre servidores."""
        print("\n=== ADMINISTRAR CONEXIONES ===")
        print("1. Agregar conexion")
        print("2. Eliminar conexion")
        print("0. Cancelar")

        opcion = leer_opcion(["0", "1", "2"])

        if opcion == "0":
            return

        origen = input("Servidor de origen: ").strip()
        destino = input("Servidor de destino: ").strip()

        if opcion == "1":
            latencia = float(input("Latencia en ms: ").strip())

            self.__grafo.agregar_conexion(
                origen, destino, latencia
            )
            self.__grafo.guardar()

            print(
                f"Conexion entre '{origen}' y '{destino}' creada."
            )

        elif opcion == "2":
            self.__grafo.eliminar_conexion(origen, destino)
            self.__grafo.guardar()

            print(
                f"Conexion entre '{origen}' y '{destino}' eliminada."
            )
