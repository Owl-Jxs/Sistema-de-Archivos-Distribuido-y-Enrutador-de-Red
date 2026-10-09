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
        """
        1. Listar servidores y conexiones
        2. Agregar / eliminar servidor   # PENDIENTE: GrafoRed.eliminar_servidor(nombre)
        3. Agregar / eliminar conexion
        4. Cambiar latencia              # PENDIENTE: GrafoRed.actualizar_latencia(origen, destino, latencia)
        5. Ping general
        0. Volver

        Logica: grafo.vertices, grafo.agregar_servidor(Servidor(nombre, id, "datos")),
        grafo.agregar_conexion(o, d, ms), grafo.eliminar_conexion(o, d),
        grafo.ping_general(origen), grafo.guardar(). Cada operacion delega en
        el grafo; 0 hace return.

        La base "datos" deja cada servidor en datos/servidores/<id>/ y el CSV
        de la red al lado, en datos/red_conexiones.csv (default de GrafoRed).
        """
        print("Pendiente: menu de red.")

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
