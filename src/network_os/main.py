from network_os.consola.principal.menu_consola import MenuConsola
from network_os.logic.controller.auditoria.auditoria import Auditoria
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)


class NetworkOS:
    """Punto de entrada de la entrega en consola."""

    @staticmethod
    def ejecutar_menu() -> None:
        auditoria_red = Auditoria("RED", PersistenciaAuditoriaCSV())
        grafo = GrafoRed(auditoria=auditoria_red)
        try:
            grafo.cargar()
        except (OSError, ValueError) as error:
            # Un CSV de red o de servidor corrupto no debe tumbar el arranque.
            print(f"No se pudieron cargar los datos de red: {error}")
            print("Se inicia una red vacia.")

        MenuConsola(grafo).ejecutar()


def main() -> None:
    """Inicializa el sistema y abre el menu principal de consola."""
    NetworkOS.ejecutar_menu()


if __name__ == "__main__":
    main()
