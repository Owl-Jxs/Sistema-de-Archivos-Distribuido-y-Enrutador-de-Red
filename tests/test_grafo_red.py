import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from network_os.logic.controller.servidor.servidor import Servidor
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed


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

    def test_agrega_conexion_bidireccional_entre_dos_vertices(self) -> None:
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
            self.assertEqual(1, len(destino.conexiones))
            self.assertIs(origen, destino.conexiones[0].destino)
            self.assertFalse(origen.esta_aislado())
            self.assertFalse(destino.esta_aislado())

    def test_rechaza_conexion_duplicada(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)
            self.__agregar_servidor(grafo, ruta_base, "principal", 1)
            self.__agregar_servidor(grafo, ruta_base, "secundario", 2)
            grafo.agregar_conexion("principal", "secundario", 10)

            with self.assertRaises(ValueError):
                grafo.agregar_conexion("principal", "secundario", 20)

            with self.assertRaises(ValueError):
                grafo.agregar_conexion("secundario", "principal", 20)

    def test_eliminar_conexion_borra_las_dos_direcciones(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)
            self.__agregar_servidor(grafo, ruta_base, "principal", 1)
            self.__agregar_servidor(grafo, ruta_base, "secundario", 2)
            grafo.agregar_conexion("principal", "secundario", 10)

            grafo.eliminar_conexion("secundario", "principal")

            self.assertTrue(
                grafo.buscar_vertice("principal").esta_aislado(),
            )
            self.assertTrue(
                grafo.buscar_vertice("secundario").esta_aislado(),
            )

            with self.assertRaises(ValueError):
                grafo.eliminar_conexion("principal", "secundario")

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

    def test_rechaza_latencias_no_finitas(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = self.__construir_grafo(ruta_base)
            self.__agregar_servidor(grafo, ruta_base, "principal", 1)

            for latencia in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(latencia=latencia):
                    with self.assertRaises(ValueError):
                        grafo.agregar_conexion(
                            "principal", "principal", latencia,
                        )

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
            self.assertEqual(1, len(secundario.conexiones))
            self.assertIs(principal, secundario.conexiones[0].destino)

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


class AlgoritmosRedTests(unittest.TestCase):
    def setUp(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.ruta_base = Path(temporal.name)
        self.grafo = GrafoRed(self.ruta_base / "red.csv")
        for indice, nombre in enumerate(("A", "B", "C", "D", "E")):
            self.grafo.agregar_servidor(Servidor(nombre, indice, self.ruta_base))
        for origen, destino, latencia in (
            ("A", "B", 10), ("A", "C", 2), ("C", "B", 1),
            ("B", "D", 4), ("C", "D", 20),
        ):
            self.grafo.agregar_conexion(origen, destino, latencia)

    def test_bfs_por_niveles_con_ciclos_y_desconexion(self) -> None:
        self.assertEqual(["A", "B", "C", "D"], self.grafo.bfs(" A "))
        self.assertEqual(["E"], self.grafo.bfs("E"))

    def test_grafo_conectado(self) -> None:
        self.grafo.agregar_conexion("D", "E", 0.5)
        self.assertEqual(["A", "B", "C", "D", "E"], self.grafo.bfs("A"))
        distancias, _ = self.grafo.dijkstra("A")
        self.assertEqual({"A": 0, "B": 3, "C": 2, "D": 7, "E": 7.5}, distancias)
        self.assertEqual((["A", "C", "B", "D", "E"], 7.5),
                         self.grafo.ruta_mas_corta("A", "E"))

    def test_dijkstra_distancias_y_predecesores(self) -> None:
        distancias, anteriores = self.grafo.dijkstra(" A ")
        self.assertEqual({"A": 0, "B": 3, "C": 2, "D": 7, "E": float("inf")},
                         distancias)
        self.assertEqual({"A": None, "B": "C", "C": "A", "D": "B", "E": None},
                         anteriores)

    def test_origen_aislado(self) -> None:
        distancias, anteriores = self.grafo.dijkstra("E")
        self.assertEqual({"A": float("inf"), "B": float("inf"),
                          "C": float("inf"), "D": float("inf"), "E": 0},
                         distancias)
        self.assertTrue(all(anterior is None for anterior in anteriores.values()))
        self.assertEqual({"A": None, "B": None, "C": None, "D": None},
                         self.grafo.ping_general("E"))

    def test_ruta_indirecta_mas_barata_y_sentido_inverso(self) -> None:
        self.assertEqual((["A", "C", "B"], 3),
                         self.grafo.ruta_mas_corta(" A ", " B "))
        self.assertEqual((["D", "B", "C", "A"], 7),
                         self.grafo.ruta_mas_corta("D", "A"))
        self.assertEqual((["A", "C"], 2), self.grafo.ruta_mas_corta("A", "C"))

    def test_origen_igual_destino_e_inalcanzable(self) -> None:
        for nombre in ("A", "E"):
            with self.subTest(nombre=nombre):
                self.assertEqual(([nombre], 0),
                                 self.grafo.ruta_mas_corta(nombre, nombre))
        self.assertIsNone(self.grafo.ruta_mas_corta("A", "E"))

    def test_identificadores_invalidos_o_inexistentes(self) -> None:
        for nombre in ("fantasma", "", "   ", None, 1):
            for metodo in (self.grafo.bfs, self.grafo.dijkstra, self.grafo.ping_general):
                with self.subTest(metodo=metodo.__name__, nombre=nombre):
                    with self.assertRaises(ValueError):
                        metodo(nombre)
            for origen, destino in ((nombre, "A"), ("A", nombre), (nombre, nombre)):
                with self.subTest(origen=origen, destino=destino):
                    with self.assertRaises(ValueError):
                        self.grafo.ruta_mas_corta(origen, destino)

    def test_grafo_vacio_rechaza_origen_inexistente(self) -> None:
        grafo = GrafoRed(self.ruta_base / "vacio.csv")
        for metodo in (grafo.bfs, grafo.dijkstra, grafo.ping_general):
            with self.subTest(metodo=metodo.__name__):
                with self.assertRaises(ValueError):
                    metodo("A")
        with self.assertRaises(ValueError):
            grafo.ruta_mas_corta("A", "A")

    def test_ping_de_unico_vertice(self) -> None:
        grafo = GrafoRed(self.ruta_base / "unico.csv")
        grafo.agregar_servidor(Servidor("unico", 8, self.ruta_base))
        self.assertEqual({}, grafo.ping_general("unico"))

    def test_ping_y_ruta_reutilizan_una_ejecucion_de_dijkstra(self) -> None:
        with patch.object(self.grafo, "dijkstra", wraps=self.grafo.dijkstra) as calculo:
            self.assertEqual({"B": 3, "C": 2, "D": 7, "E": None},
                             self.grafo.ping_general(" A "))
            calculo.assert_called_once_with(" A ")
        with patch.object(self.grafo, "dijkstra", wraps=self.grafo.dijkstra) as calculo:
            self.assertEqual((["A", "C", "B", "D"], 7),
                             self.grafo.ruta_mas_corta("A", "D"))
            calculo.assert_called_once_with("A")

    def test_ciclos_y_autoconexiones_de_peso_cero(self) -> None:
        self.grafo.agregar_conexion("A", "A", 0)
        self.grafo.agregar_conexion("A", "D", 0)
        self.grafo.agregar_conexion("D", "E", 0)
        self.grafo.agregar_conexion("E", "A", 0)
        self.assertEqual(["A", "B", "C", "D", "E"], self.grafo.bfs("A"))
        self.assertEqual((["A", "E"], 0), self.grafo.ruta_mas_corta("A", "E"))
        self.assertEqual((["A"], 0), self.grafo.ruta_mas_corta("A", "A"))

    def test_rechaza_latencias_modificadas_invalidas(self) -> None:
        conexion = self.grafo.buscar_vertice("A").conexiones[0]
        for latencia, error in ((-1, ValueError), (float("nan"), ValueError),
                                (float("inf"), ValueError), (True, TypeError),
                                ("rapido", TypeError)):
            conexion.actualizar_latencia(latencia)
            for metodo in (self.grafo.dijkstra, self.grafo.ping_general):
                with self.subTest(latencia=latencia, metodo=metodo.__name__):
                    with self.assertRaises(error):
                        metodo("A")
            with self.assertRaises(error):
                self.grafo.ruta_mas_corta("A", "A")

    def test_rechaza_peso_negativo_en_componente_desconectado(self) -> None:
        self.grafo.agregar_conexion("E", "E", 1)
        self.grafo.buscar_vertice("E").conexiones[0].actualizar_latencia(-1)
        with self.assertRaises(ValueError):
            self.grafo.dijkstra("A")

    def test_algoritmos_con_red_reconstruida(self) -> None:
        self.grafo.guardar()
        self.grafo.cargar()
        self.assertEqual(["A", "B", "C", "D"], self.grafo.bfs("A"))
        self.assertEqual((["A", "C", "B", "D"], 7),
                         self.grafo.ruta_mas_corta("A", "D"))
        self.assertEqual({"B": 3, "C": 2, "D": 7, "E": None},
                         self.grafo.ping_general("A"))


if __name__ == "__main__":
    unittest.main()
