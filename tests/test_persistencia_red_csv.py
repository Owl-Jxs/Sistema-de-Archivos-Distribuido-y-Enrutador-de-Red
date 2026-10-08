import tempfile
import unittest
from pathlib import Path

from network_os.logic.controller.auditoria.auditoria import Auditoria
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import PersistenciaAuditoriaCSV

from network_os.logic.controller.servidor.servidor import Servidor
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed
from network_os.persistencia.persistencia_red.persistencia_red_csv import (
    PersistenciaRedCSV,
)


class PersistenciaRedCSVTests(unittest.TestCase):
    def setUp(self) -> None:
        temporal_auditoria = tempfile.TemporaryDirectory()
        self.addCleanup(temporal_auditoria.cleanup)
        self.auditoria = Auditoria("RED", PersistenciaAuditoriaCSV(
            Path(temporal_auditoria.name) / "network_audit_log.txt"
        ))

    @staticmethod
    def __escribir_csv(ruta: Path, contenido: str) -> None:
        ruta.write_text(contenido, encoding="utf-8")

    def test_rechaza_rutas_invalidas(self) -> None:
        with self.assertRaises(ValueError):
            PersistenciaRedCSV("   ")
        with self.assertRaises(TypeError):
            PersistenciaRedCSV(123)  # type: ignore[arg-type]

    def test_expone_la_ruta_como_path(self) -> None:
        persistencia = PersistenciaRedCSV("datos/red_conexiones.csv")

        self.assertIsInstance(persistencia.ruta_conexiones_csv, Path)
        self.assertEqual(
            Path("datos/red_conexiones.csv"),
            persistencia.ruta_conexiones_csv,
        )

    def test_cargar_sin_archivo_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            persistencia = PersistenciaRedCSV(
                Path(temporal) / "no_existe.csv",
            )

            with self.assertRaises(FileNotFoundError):
                persistencia.cargar(self.auditoria)

    def test_guardar_rechaza_objetos_que_no_son_grafo(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            persistencia = PersistenciaRedCSV(Path(temporal) / "red.csv")

            with self.assertRaises(TypeError):
                persistencia.guardar("no soy un grafo")  # type: ignore[arg-type]

    def test_cargar_sin_encabezados_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "red.csv"
            self.__escribir_csv(ruta, "")
            persistencia = PersistenciaRedCSV(ruta)

            with self.assertRaises(ValueError):
                persistencia.cargar(self.auditoria)

    def test_cargar_con_tipo_desconocido_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "red.csv"
            self.__escribir_csv(
                ruta,
                "tipo,nombre,id,direccion_base,origen,destino,latencia_ms\n"
                f"NODO,principal,1,{temporal},,,\n",
            )
            persistencia = PersistenciaRedCSV(ruta)

            with self.assertRaises(ValueError):
                persistencia.cargar(self.auditoria)

    def test_cargar_servidor_duplicado_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "red.csv"
            self.__escribir_csv(
                ruta,
                "tipo,nombre,id,direccion_base,origen,destino,latencia_ms\n"
                f"SERVIDOR,principal,1,{temporal},,,\n"
                f"SERVIDOR,principal,2,{temporal},,,\n",
            )
            persistencia = PersistenciaRedCSV(ruta)

            with self.assertRaises(ValueError):
                persistencia.cargar(self.auditoria)

    def test_cargar_conexion_a_servidor_inexistente_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "red.csv"
            self.__escribir_csv(
                ruta,
                "tipo,nombre,id,direccion_base,origen,destino,latencia_ms\n"
                f"SERVIDOR,principal,1,{temporal},,,\n"
                "CONEXION,,,,principal,fantasma,10\n",
            )
            persistencia = PersistenciaRedCSV(ruta)

            with self.assertRaises(ValueError):
                persistencia.cargar(self.auditoria)

    def test_cargar_con_latencia_no_numerica_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "red.csv"
            self.__escribir_csv(
                ruta,
                "tipo,nombre,id,direccion_base,origen,destino,latencia_ms\n"
                f"SERVIDOR,principal,1,{temporal},,,\n"
                f"SERVIDOR,secundario,2,{temporal},,,\n"
                "CONEXION,,,,principal,secundario,rapido\n",
            )
            persistencia = PersistenciaRedCSV(ruta)

            with self.assertRaises(ValueError):
                persistencia.cargar(self.auditoria)

    def test_cargar_sin_columnas_requeridas_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "red.csv"
            self.__escribir_csv(ruta, "tipo,nombre\nSERVIDOR,principal\n")
            persistencia = PersistenciaRedCSV(ruta)

            with self.assertRaises(ValueError):
                persistencia.cargar(self.auditoria)

    def test_guardar_y_cargar_roundtrip_completo(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            grafo = GrafoRed(ruta_base / "red_conexiones.csv", auditoria=self.auditoria)

            grafo.agregar_servidor(Servidor("principal", 1, ruta_base))
            grafo.agregar_servidor(Servidor("secundario", 2, ruta_base))
            grafo.agregar_servidor(Servidor("aislado", 3, ruta_base))
            grafo.agregar_conexion("principal", "secundario", 10)

            grafo.guardar()

            persistencia = PersistenciaRedCSV(ruta_base / "red_conexiones.csv")
            reconstruido = persistencia.cargar(self.auditoria)

            self.assertIsInstance(reconstruido, GrafoRed)
            self.assertEqual(3, len(reconstruido.vertices))

            filas = (
                persistencia.ruta_conexiones_csv.read_text(
                    encoding="utf-8",
                )
                .strip()
                .splitlines()
            )
            self.assertEqual(6, len(filas))
            self.assertTrue(filas[1].startswith("SERVIDOR,principal,1,"))
            self.assertEqual(
                "CONEXION,,,,principal,secundario,10",
                filas[4],
            )
            self.assertEqual(
                "CONEXION,,,,secundario,principal,10",
                filas[5],
            )

            principal = reconstruido.buscar_vertice("principal")
            secundario = reconstruido.buscar_vertice("secundario")
            self.assertEqual(1, len(principal.conexiones))
            self.assertEqual(
                10,
                principal.conexiones[0].latencia_ms,
            )
            self.assertEqual(1, len(secundario.conexiones))
            self.assertEqual(
                10,
                secundario.conexiones[0].latencia_ms,
            )


if __name__ == "__main__":
    unittest.main()
