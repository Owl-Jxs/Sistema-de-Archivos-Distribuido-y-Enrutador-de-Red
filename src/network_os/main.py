from network_os.consola.menu_consola import MenuConsola
from network_os.logic.controller.auditoria.auditoria import Auditoria
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)


class NetworkOS:
    """Punto de entrada de la entrega en consola."""

    @staticmethod
    def ejecutar_menu() -> None:
        grafo = GrafoRed(auditoria=Auditoria("RED", PersistenciaAuditoriaCSV()))
        try:
            grafo.cargar()
        except FileNotFoundError:
            print("Sin datos de red previos; se inicia una red vacia.")

        MenuConsola(grafo).ejecutar()


if __name__ == "__main__":
    NetworkOS.ejecutar_menu()
