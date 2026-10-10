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
            print("0. Cerrar sesion")
            opcion = leer_opcion(["0", "1", "2", "3"])
            if opcion == "0":
                return
            if opcion == "1":
                self.menu_archivos()
            elif opcion == "2":
                self.menu_usuarios()
            else:
                try:
                    self.enviar_paquete()
                except (ValueError, TypeError, OSError) as error:
                    print(f"No se pudo enviar el paquete: {error}")
                pausar()

    def menu_archivos(self) -> None:
        self.__archivos.menu_archivos()

    def menu_usuarios(self) -> None:
        usuarios_locales(self.__servidor)

    def enviar_paquete(self) -> None:
        """Prepara contenido y utiliza la simulacion de envio disponible."""
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
        print("Simulacion de envio; la transferencia del contenido esta pendiente.")
        recorrido = self.__grafo.enviar_paquete(paquete.origen, paquete.destino)
        if recorrido is None:
            print("Paquete no entregado: el destino es inalcanzable.")
        else:
            print("Simulacion completada. El contenido del paquete no fue entregado.")

        # PENDIENTE: GrafoRed solo admite origen/destino y simula el recorrido.
        # Cuando admita PaqueteDatos y retorne ResultadoEnvio, sustituir la
        # simulacion anterior por esta integracion:
        # resultado = self.__grafo.enviar_paquete(paquete)
        # for indice in range(len(resultado.ruta) - 1):
        #     print(f"Salto {indice + 1}: {resultado.ruta[indice]} -> "
        #           f"{resultado.ruta[indice + 1]}")
        # print(f"Costo total: {resultado.latencia_total_ms} ms.")
        # print(resultado.mensaje)
        # print("Paquete entregado." if resultado.entregado else "Paquete no entregado.")
