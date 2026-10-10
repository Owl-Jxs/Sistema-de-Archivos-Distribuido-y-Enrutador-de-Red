from __future__ import annotations

from getpass import getpass

from ...logic.controller.grafo_red.grafoRed import GrafoRed
from ...logic.controller.servidor.servidor import Servidor
from ..entrada import leer_opcion, pausar
from ..red.menu_red import MenuRed
from ..servidor.menu_servidor import MenuServidor


class MenuConsola:
    """Menu principal, autenticacion y acceso a los submenus de consola."""

    def __init__(self, grafo: GrafoRed) -> None:
        if not isinstance(grafo, GrafoRed):
            raise TypeError("El grafo debe ser una instancia de GrafoRed.")
        self.__grafo = grafo
        self.__servidor_actual: Servidor | None = None

    def ejecutar(self) -> None:
        self.menu_principal()

    def menu_principal(self) -> None:
        while True:
            print("\n=== NETWORK OS | Menu principal ===")
            print("1. Administrar / diagnosticar red")
            print("2. Acceder a un servidor")
            print("3. Consultar auditoria")
            print("0. Salir")
            opcion = self.leer_option(["0", "1", "2", "3"])

            if opcion == "1":
                self.menu_red()
            elif opcion == "2":
                self.iniciar_sesion()
            elif opcion == "3":
                self.menu_auditoria()
            else:
                return

    def iniciar_sesion(self) -> None:
        """Selecciona servidor, pide credenciales y autentica con Servidor."""
        servidor = self.__pedir_servidor()
        if servidor is None:
            return

        if servidor.usuarios_vacios():
            print(f"El servidor '{servidor.nombre}' no tiene usuarios todavia.")
            print("Cree el primero para poder iniciar sesion (vacio para cancelar).")
            if not self.__crear_primer_usuario(servidor):
                print("Acceso cancelado.")
                return

        while True:
            usuario = input("Usuario: ").strip()
            contrasena = getpass("Contrasena: ")
            try:
                autenticado = servidor.autenticar_usuario(usuario, contrasena)
            except OSError as error:
                print(f"No se pudo iniciar sesion: {error}")
                return

            if autenticado:
                print(f"Sesion iniciada en '{servidor.nombre}'.")
                self.__servidor_actual = servidor
                try:
                    self.menu_servidor()
                finally:
                    self.__servidor_actual = None
                print("Sesion cerrada.")
                return

            print("Usuario o contrasena incorrectos.")
            if self.leer_option(["0", "1"], "1. Reintentar\n0. Cancelar\nOpcion: ") == "0":
                print("Acceso cancelado.")
                return

    def pausar(self) -> None:
        """Detiene la salida hasta que el usuario confirme con Enter."""
        pausar()

    def leer_option(self, validas: list[str], mensaje: str = "Opcion: ") -> str:
        """Conserva el nombre usado por el menu original."""
        return self.leer_opcion(validas, mensaje)

    def leer_opcion(self, validas: list[str], mensaje: str = "Opcion: ") -> str:
        return leer_opcion(validas, mensaje)

    def __pedir_servidor(self) -> Servidor | None:
        """Devuelve el servidor elegido, o None si no hay o se cancela."""
        vertices = self.__grafo.vertices
        if not vertices:
            print("No hay servidores en la red.")
            return None

        while True:
            print("\nServidores en la red:")
            for vertice in vertices:
                servidor = vertice.servidor
                print(f"  - {servidor.nombre} (ID {servidor.id})")

            nombre = input(
                "Nombre del servidor (vacio para cancelar): "
            ).strip()
            if not nombre:
                return None

            for vertice in vertices:
                if vertice.servidor.nombre == nombre:
                    return vertice.servidor
            print(f"No existe un servidor llamado '{nombre}'.")

    def __crear_primer_usuario(self, servidor: Servidor) -> bool:
        """Pide credenciales y registra el primer usuario. False si se cancela."""
        while True:
            usuario = input("Usuario: ").strip()
            if not usuario:
                return False
            contrasena = getpass("Contrasena: ")
            try:
                servidor.agregar_usuario(usuario, contrasena)
            except (TypeError, ValueError) as error:
                print(f"Credenciales invalidas: {error}")
                continue
            except OSError as error:
                print(f"No se pudo crear el primer usuario: {error}")
                return False
            print(f"Usuario '{usuario}' creado.")
            return True

    def menu_red(self) -> None:
        MenuRed(self.__grafo).menu_red()

    def menu_servidor(self) -> None:
        menu = self.__obtener_menu_servidor()
        if menu is not None:
            menu.menu_servidor()

    def menu_archivos(self) -> None:
        menu = self.__obtener_menu_servidor()
        if menu is not None:
            menu.menu_archivos()

    def menu_usuarios(self) -> None:
        menu = self.__obtener_menu_servidor()
        if menu is not None:
            menu.menu_usuarios()

    def enviar_paquete(self) -> None:
        menu = self.__obtener_menu_servidor()
        if menu is not None:
            try:
                menu.enviar_paquete()
            except (ValueError, TypeError, OSError) as error:
                print(f"No se pudo enviar el paquete: {error}")

    def __obtener_menu_servidor(self) -> MenuServidor | None:
        if self.__servidor_actual is None:
            print("No hay una sesion activa.")
            return None
        return MenuServidor(self.__grafo, self.__servidor_actual)

    def menu_auditoria(self) -> None:
        """Consulta y muestra los registros de auditoría de la red."""
        while True:
            print("\n=== MENU DE AUDITORIA ===")
            print("1. Leer y mostrar registros")
            print("0. Volver al menu principal")

            opcion = self.leer_option(["0", "1"])

            if opcion == "0":
                return

            try:
                registros = self.__grafo.consultar_auditoria()

                if not registros:
                    print("\nNo hay registros de auditoria.")
                else:
                    print(f"\n=== REGISTROS DE AUDITORIA ({len(registros)}) ===")
                    for indice, registro in enumerate(registros, start=1):
                        print(f"\n--- Registro {indice} ---")
                        print(f"Fecha y hora: {registro.fecha_hora}")
                        print(f"Origen:       {registro.origen}")
                        print(f"Categoria:    {registro.categoria}")
                        print(f"Accion:       {registro.accion}")
                        print(f"Resultado:    {registro.resultado}")
                        print(f"Detalle:      {registro.detalle}")

            except (OSError, ValueError, TypeError) as error:
                print(f"No se pudo consultar la auditoria: {error}")
            self.pausar()
