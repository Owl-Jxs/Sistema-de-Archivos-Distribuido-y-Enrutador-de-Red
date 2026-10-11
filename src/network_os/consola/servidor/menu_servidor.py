from __future__ import annotations

from ...logic.controller.grafo_red.grafoRed import GrafoRed
from ...logic.controller.servidor.servidor import Servidor
from ..entrada import leer_opcion, pausar
from .usuarios_locales import usuarios_locales
from .menu_archivos import MenuArchivos


class MenuServidor:
    """Submenus de una sesion autenticada en un servidor."""

    def __init__(self, grafo: GrafoRed, servidor: Servidor) -> None:
        if not isinstance(grafo, GrafoRed):
            raise TypeError("El grafo debe ser una instancia de GrafoRed.")
        if not isinstance(servidor, Servidor):
            raise TypeError("El servidor debe ser una instancia de Servidor.")
        self.__grafo = grafo
        self.__servidor = servidor
        self.__archivos = MenuArchivos(servidor)

    def menu_servidor(self) -> None:
        while True:
            print(f"\n=== MENU DEL SERVIDOR | {self.__servidor.nombre} ===")
            print("1. Archivos y carpetas")
            print("2. Usuarios locales")
            print("3. Enviar paquete")
            print("4. Consultar auditoria local")
            print("0. Cerrar sesion")
            opcion = leer_opcion(["0", "1", "2", "3", "4"])
            if opcion == "0":
                return
            if opcion == "1":
                self.menu_archivos()
            elif opcion == "2":
                self.menu_usuarios()
            elif opcion == "3":
                try:
                    self.enviar_paquete()
                except (ValueError, TypeError, OSError) as error:
                    print(f"No se pudo enviar el paquete: {error}")
                pausar()
            elif opcion == "4":
                self.menu_auditoria()

    def menu_archivos(self) -> None:
        self.__archivos.menu_archivos()

    def menu_usuarios(self) -> None:
        usuarios_locales(self.__servidor)

    def menu_auditoria(self) -> None:
        """Consulta unicamente los registros del servidor de esta sesion."""
        while True:
            print(f"\n=== AUDITORIA LOCAL | {self.__servidor.nombre} ===")
            print("1. Leer y mostrar registros locales")
            print("0. Volver al menu del servidor")
            opcion = leer_opcion(["0", "1"])
            if opcion == "0":
                return

            try:
                registros = self.__servidor.consultar_auditoria()
                if not registros:
                    print("No hay registros de auditoria local.")
                else:
                    print(f"\n=== REGISTROS LOCALES ({len(registros)}) ===")
                    for indice, registro in enumerate(registros, start=1):
                        print(f"\n--- Registro {indice} ---")
                        print(f"Fecha y hora: {registro.fecha_hora}")
                        print(f"Origen:       {registro.origen}")
                        print(f"Categoria:    {registro.categoria}")
                        print(f"Accion:       {registro.accion}")
                        print(f"Resultado:    {registro.resultado}")
                        print(f"Detalle:      {registro.detalle}")
            except (OSError, ValueError, TypeError) as error:
                print(f"No se pudo consultar la auditoria local: {error}")
            pausar()

    def enviar_paquete(self) -> None:
        """Envia contenido y muestra el recorrido y la confirmacion del destino."""
        destino = input("Servidor de destino (vacio para cancelar): ").strip()
        if not destino:
            print("Envio cancelado.")
            return
        self.__grafo.buscar_vertice(destino)
        contenido = input("Contenido del paquete: ")
        if not contenido.strip():
            raise ValueError("El contenido del paquete no puede estar vacio.")
        paquete = self.__servidor.crear_paquete(destino, contenido)
        print(f"Origen: {paquete.origen} | Destino: {paquete.destino}")
        resultado = self.__servidor.enviar_paquete(self.__grafo, paquete)
        for indice in range(len(resultado.ruta) - 1):
            print(f"Salto {indice + 1}: {resultado.ruta[indice]} -> "
                  f"{resultado.ruta[indice + 1]}")
        if resultado.ruta:
            print(f"Costo total: {resultado.latencia_total_ms} ms.")
        print(resultado.mensaje)
        print("Paquete entregado." if resultado.entregado else "Paquete no entregado.")
