from __future__ import annotations

from ..logic.controller.grafo_red.grafoRed import GrafoRed
from ..logic.controller.servidor.servidor import Servidor


class MenuConsola:
    """
    Menus de consola: la logica permanece en sus modulos.

    Cada submenu es un metodo de esta clase (no clases nuevas).
    Todos usan leer_option() para las entradas, un bucle while, y 0 vuelve al menu que
    llamo sin recursion. Despues de cada submenu, pausar() congela la salida para que
    el resultado no quede enterrado bajo el menu siguiente; reutilizarlo en los
    submenus que impriman listas largas.
    """

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
            self.pausar()

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
            contrasena = input("Contrasena: ")

            if servidor.autenticar_usuario(usuario, contrasena):
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
        input("\nPresione Enter para continuar...")

    def leer_option(self, validas: list[str], mensaje: str = "Opcion: ") -> str:
        """Pide una opcion hasta que este en la lista de valores validos."""
        while True:
            entrada = input(mensaje).strip()
            if entrada in validas:
                return entrada
            print(f"Opcion invalida: '{entrada}'. Intente de nuevo.")

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
            contrasena = input("Contrasena: ")
            try:
                servidor.agregar_usuario(usuario, contrasena)
            except (TypeError, ValueError) as error:
                print(f"Credenciales invalidas: {error}")
                continue
            print(f"Usuario '{usuario}' creado.")
            return True

    # === SUBMENUS PENDIENTES (especificación UML, indicaciones para implementar) ===
    # Al implementar cada submenu: borrar SOLO su print("Pendiente...").
    # Este encabezado se borra cuando no quede ninguno pendiente.
    # Los docstrings de abajo son la especificación; no se borran.

    
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

            opcion = self.leer_option(["0", "1", "2", "3", "4", "5"])

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
                    self.pausar()

            except (ValueError, TypeError, OSError) as error:
                print(f"\nNo se pudo completar la operacion: {error}")
                self.pausar()

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

        opcion = self.leer_option(["0", "1", "2"])

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

            servidor = Servidor(nombre, nuevo_id, "datos")
            self.__grafo.agregar_servidor(servidor)
            self.__grafo.guardar()

            print(
                f"Servidor '{nombre}' creado con ID {nuevo_id}."
            )

        elif opcion == "2":
            nombre = input("Nombre del servidor que desea eliminar: ").strip()
            self.__grafo.eliminar_servidor(nombre)
            self.__grafo.guardar()

            print(f"Servidor '{nombre}' eliminado correctamente.")

    def __menu_conexiones_red(self) -> None:
        """Permite agregar o eliminar conexiones entre servidores."""
        print("\n=== ADMINISTRAR CONEXIONES ===")
        print("1. Agregar conexion")
        print("2. Eliminar conexion")
        print("0. Cancelar")

        opcion = self.leer_option(["0", "1", "2"])

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


    def menu_servidor(self) -> None:
        """1. Archivos y carpetas
        2. Usuarios locales
        3. Enviar paquete
        0. Cerrar sesion (return; el estado lo limpia iniciar_sesion)

        Requiere sesion activa: self.__servidor_actual.
        """
        if self.__servidor_actual is None:
            print("No hay una sesion activa.")
            return
        print("Pendiente: menu del servidor.")

    def menu_archivos(self) -> None:
        """
        1. Listar contenido actual
        2. Entrar / subir / ir a raiz
        3. Crear carpeta
        4. Crear archivo
        5. Buscar archivo recursivamente
        6. Imprimir arbol indentado
        7. Eliminar archivo o carpeta (confirmar antes de borrar)
        0. Volver

        Logica: servidor.listar_contenido, obtener_carpeta_actual,
        entrar_subcarpeta, subir_nivel, volver_a_raiz, crear_subcarpeta,
        crear_nuevo_archivo, buscar_archivo, mostrar_arbol,
        eliminar_archivo, eliminar_subcarpeta. Usa self.__servidor_actual.
        """
        print("Pendiente: menu de archivos y carpetas.")

    def menu_usuarios(self) -> None:
        """
        1. Registrar usuario
        2. Eliminar usuario
        0. Volver

        El primer usuario ya se creó al iniciar sesion (ver iniciar_sesion);
        este menu es para gestionar los que ya existen.

        Logica: servidor.agregar_usuario(nombre, contrasena) y
        servidor.eliminar_usuario(nombre). Usa self.__servidor_actual.
        """
        print("Pendiente: menu de usuarios locales.")

    def enviar_paquete(self) -> None:
        """
        Origen: servidor de la sesion. Pide destino y contenido, informa
        cada salto y el costo total, o la falta de ruta. Vuelve al menu del
        servidor.

        Logica: servidor.crear_paquete(destino, contenido) y
        # PENDIENTE: GrafoRed.enviar_paquete(paquete) -> ResultadoEnvio
        imprimir resultado.entregado, resultado.ruta,
        resultado.latencia_total_ms y resultado.mensaje.
        """
        print("Pendiente: enviar paquete.")

    
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
                    continue

                print(f"\n=== REGISTROS DE AUDITORIA ({len(registros)}) ===")

                for indice, registro in enumerate(registros, start=1):
                    print(f"\n--- Registro {indice} ---")
                    print(f"Fecha y hora: {registro.fecha_hora}")
                    print(f"Origen:       {registro.origen}")
                    print(f"Categoria:    {registro.categoria}")
                    print(f"Accion:       {registro.accion}")
                    print(f"Resultado:    {registro.resultado}")
                    print(f"Detalle:      {registro.detalle}")

                self.pausar()

            except (OSError, ValueError, TypeError) as error:
                print(f"No se pudo consultar la auditoria: {error}")
