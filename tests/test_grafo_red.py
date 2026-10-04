import tempfile
import unittest
from pathlib import Path

from network_os.logic.controller.servidor.servidor import Servidor
from network_os.logic.structure.grafo_red.grafoRed import GrafoRed


class GrafoRedTests(unittest.TestCase):
    def __construir_grafo(self, ruta_base: Path) -> GrafoRed:
        return GrafoRed(ruta_base / "red_conexiones.csv")

    @staticmethod
    def __agregar_servidor(
        grafo: GrafoRed,
        ruta_base: Path,
        nombre: str,
        id_servidor: int,
    ) -> Servidor:
        servidor = Servidor(nombre, id_servidor, ruta_base)
        grafo.agregar_servidor(servidor)
        return servidor

    def test_agrega_y_busca_un_vertice(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)
            servidor = self.__agregar_servidor(
                grafo, ruta_base, "principal", 1,
            )

            vertice = grafo.buscar_vertice("principal")

            self.assertEqual(1, len(grafo.vertices))
            self.assertIs(servidor, vertice.servidor)

    def test_buscar_vertice_inexistente_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            grafo = self.__construir_grafo(Path(temporal))

            with self.assertRaises(ValueError):
                grafo.buscar_vertice("fantasma")

    def test_rechaza_servidor_invalido_o_duplicado(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)

            with self.assertRaises(TypeError):
                grafo.agregar_servidor("principal")  # type: ignore[arg-type]

            self.__agregar_servidor(grafo, ruta_base, "principal", 1)

            with self.assertRaises(ValueError):
                self.__agregar_servidor(grafo, ruta_base, "principal", 2)

    def test_agrega_conexion_entre_dos_vertices(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)
            self.__agregar_servidor(grafo, ruta_base, "principal", 1)
            self.__agregar_servidor(grafo, ruta_base, "secundario", 2)

            grafo.agregar_conexion("principal", "secundario", 10)

            origen = grafo.buscar_vertice("principal")
            destino = grafo.buscar_vertice("secundario")

            self.assertEqual(1, len(origen.conexiones))
            self.assertIs(destino, origen.conexiones[0].destino)
            self.assertEqual(10, origen.conexiones[0].latencia_ms)
            self.assertEqual([], destino.conexiones)
            self.assertFalse(origen.esta_aislado())

    def test_conexion_requiere_vertices_y_latencia_validos(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)
            self.__agregar_servidor(grafo, ruta_base, "principal", 1)

            with self.assertRaises(ValueError):
                grafo.agregar_conexion("principal", "fantasma", 10)

            with self.assertRaises(ValueError):
                grafo.agregar_conexion("fantasma", "principal", 10)

            with self.assertRaises(ValueError):
                grafo.agregar_conexion("principal", "principal", -1)

            with self.assertRaises(TypeError):
                grafo.agregar_conexion("principal", "principal", "rapido")

    def test_guardar_y_cargar_conserva_la_red(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)
            self.__agregar_servidor(grafo, ruta_base, "principal", 1)
            self.__agregar_servidor(grafo, ruta_base, "secundario", 2)
            grafo.agregar_conexion("principal", "secundario", 10)

            grafo.guardar()

            reconstruido = self.__construir_grafo(ruta_base)
            reconstruido.cargar()

            self.assertEqual(2, len(reconstruido.vertices))

            principal = reconstruido.buscar_vertice("principal")
            secundario = reconstruido.buscar_vertice("secundario")

            self.assertEqual(1, principal.servidor.id)
            self.assertEqual(
                ruta_base,
                principal.servidor.persistencia.directorio.parent.parent,
            )
            self.assertEqual(1, len(principal.conexiones))
            self.assertIs(secundario, principal.conexiones[0].destino)
            self.assertEqual(10, principal.conexiones[0].latencia_ms)
            self.assertEqual([], secundario.conexiones)

    def test_servidor_aislado_sobrevive_al_guardado(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)
            self.__agregar_servidor(grafo, ruta_base, "aislado", 9)

            grafo.guardar()

            reconstruido = self.__construir_grafo(ruta_base)
            reconstruido.cargar()

            vertice = reconstruido.buscar_vertice("aislado")

            self.assertEqual(1, len(reconstruido.vertices))
            self.assertTrue(vertice.esta_aislado())

    def test_grafo_vacio_guarda_encabezados_y_carga_vacio(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)

            grafo.guardar()

            contenido = (
                grafo.persistencia.ruta_conexiones_csv.read_text(
                    encoding="utf-8",
                )
                .strip()
                .splitlines()
            )
            self.assertEqual(
                ["tipo,nombre,id,direccion_base,origen,destino,latencia_ms"],
                contenido,
            )

            reconstruido = self.__construir_grafo(ruta_base)
            reconstruido.cargar()

            self.assertEqual([], reconstruido.vertices)


if __name__ == "__main__":
    unittest.main()
