import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from network_os.consola.menu_consola import MenuConsola
from network_os.logic.controller.auditoria.auditoria import Auditoria
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed
from network_os.logic.controller.servidor.servidor import Servidor
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)


class MenuConsolaTests(unittest.TestCase):
    def setUp(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.ruta_base = Path(temporal.name)
        self.grafo = GrafoRed(
            self.ruta_base / "red_conexiones.csv",
            auditoria=Auditoria(
                "RED",
                PersistenciaAuditoriaCSV(self.ruta_base / "network_audit_log.txt"),
            ),
        )
        self.menu = MenuConsola(self.grafo)

    def __agregar_servidor(
        self, nombre: str = "principal", id_servidor: int = 1
    ) -> Servidor:
        servidor = Servidor(nombre, id_servidor, self.ruta_base)
        self.grafo.agregar_servidor(servidor)
        return servidor

    @property
    def __servidor_actual(self):
        return self.menu._MenuConsola__servidor_actual

    def test_rechaza_grafo_invalido(self) -> None:
        with self.assertRaises(TypeError):
            MenuConsola("no soy un grafo")

    def test_el_menu_principal_sale_con_cero(self) -> None:
        with patch("builtins.input", side_effect=["0"]) as entrada, patch(
            "builtins.print"
        ):
            self.menu.ejecutar()

        self.assertEqual(1, entrada.call_count)

    def test_leer_option_vuelve_a_preguntar_si_la_opcion_es_invalida(self) -> None:
        with patch("builtins.input", side_effect=["x", "2"]) as entrada, patch(
            "builtins.print"
        ) as salida:
            opcion = self.menu.leer_option(["1", "2"])

        self.assertEqual("2", opcion)
        self.assertEqual(2, entrada.call_count)
        salida.assert_called_once()

    def test_sin_servidores_en_la_red_no_pide_credenciales(self) -> None:
        with patch("builtins.input", side_effect=[]):
            self.menu.iniciar_sesion()

        self.assertIsNone(self.__servidor_actual)

    def test_servidor_inexistente_permite_cancelar_el_acceso(self) -> None:
        self.__agregar_servidor()

        with patch("builtins.input", side_effect=["fantasma", ""]):
            self.menu.iniciar_sesion()

        self.assertIsNone(self.__servidor_actual)

    def test_acceso_valido_entra_al_menu_del_servidor_y_limpia_la_sesion(self) -> None:
        servidor = self.__agregar_servidor()
        servidor.agregar_usuario("ana", "clave1234")

        with patch("builtins.input", side_effect=["principal", "ana", "clave1234"]):
            with patch.object(MenuConsola, "menu_servidor") as menu_servidor:
                self.menu.iniciar_sesion()

        menu_servidor.assert_called_once()
        self.assertIsNone(self.__servidor_actual)

    def test_acceso_fallido_puede_reintentar_o_cancelar(self) -> None:
        servidor = self.__agregar_servidor()
        servidor.agregar_usuario("ana", "clave1234")

        with patch(
            "builtins.input",
            side_effect=["principal", "ana", "clave9999", "0"],
        ):
            with patch.object(MenuConsola, "menu_servidor") as menu_servidor:
                self.menu.iniciar_sesion()

        menu_servidor.assert_not_called()
        self.assertIsNone(self.__servidor_actual)

    def test_servidor_sin_usuarios_crea_el_primero_y_entra(self) -> None:
        servidor = self.__agregar_servidor()
        self.assertTrue(servidor.usuarios_vacios())

        with patch(
            "builtins.input",
            side_effect=["principal", "ana", "clave1234", "ana", "clave1234"],
        ):
            with patch.object(MenuConsola, "menu_servidor") as menu_servidor:
                self.menu.iniciar_sesion()

        menu_servidor.assert_called_once()
        self.assertFalse(servidor.usuarios_vacios())

    def test_primer_usuario_se_puede_cancelar(self) -> None:
        self.__agregar_servidor()

        with patch("builtins.input", side_effect=["principal", ""]):
            with patch.object(MenuConsola, "menu_servidor") as menu_servidor:
                self.menu.iniciar_sesion()

        menu_servidor.assert_not_called()
        self.assertIsNone(self.__servidor_actual)


if __name__ == "__main__":
    unittest.main()
