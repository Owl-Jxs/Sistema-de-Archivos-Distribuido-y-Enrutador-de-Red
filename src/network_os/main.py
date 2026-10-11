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
        except FileNotFoundError:
            print("Sin datos de red previos; se inicia una red vacia.")
        except (OSError, ValueError) as error:
            # Un CSV corrupto no debe impedir arrancar: se ignora y se
            # empieza con una red vacia.
            print(
                "No se pudo leer el CSV de la red "
                f"({type(error).__name__}: {error}); se inicia una red vacia."
            )

        MenuConsola(grafo).ejecutar()


def main() -> None:
    """Inicializa el sistema y abre el menu principal de consola."""
    NetworkOS.ejecutar_menu()


if __name__ == "__main__":
    main()
