import tempfile
import unittest
from pathlib import Path

from network_os.logic.structure.hash_table.hash_map import HashMap
from network_os.persistencia.persistencia_usuarios.persistencia_usuarios_csv import (
    PersistenciaUsuariosCSV,
)


class PersistenciaUsuariosCSVTests(unittest.TestCase):
    @staticmethod
    def __crear_usuarios() -> HashMap:
        usuarios = HashMap()
        usuarios.insertar("ana_01", "clave123")
        usuarios.insertar("bryan", "contraseña1")
        return usuarios

    def test_roundtrip_conserva_las_credenciales(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            persistencia = PersistenciaUsuariosCSV(
                Path(temporal) / "usuarios.csv",
            )
            persistencia.guardar(self.__crear_usuarios())

            recargados = persistencia.cargar()

            self.assertEqual("clave123", recargados.obtener("ana_01"))
            self.assertEqual("contraseña1", recargados.obtener("bryan"))
            self.assertEqual(2, recargados.tamano())

    def test_guardar_no_deja_archivos_temporales(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            persistencia = PersistenciaUsuariosCSV(
                Path(temporal) / "usuarios.csv",
            )
            persistencia.guardar(self.__crear_usuarios())

            residuales = list(Path(temporal).glob("*.tmp"))
            self.assertEqual([], residuales)

    def test_cargar_archivo_vacio_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "usuarios.csv"
            ruta.write_text("", encoding="utf-8")
            persistencia = PersistenciaUsuariosCSV(ruta)

            with self.assertRaises(ValueError):
                persistencia.cargar()

    def test_cargar_fila_corrupta_lanza_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "usuarios.csv"
            ruta.write_text(
                'clave,valor\n"ana_01","clave123"\nesto-no-es-json,x\n',
                encoding="utf-8",
            )
            persistencia = PersistenciaUsuariosCSV(ruta)

            with self.assertRaises(ValueError):
                persistencia.cargar()

    def test_cargar_archivo_inexistente_devuelve_vacio(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            persistencia = PersistenciaUsuariosCSV(
                Path(temporal) / "no_existe.csv",
            )

            self.assertEqual(0, persistencia.cargar().tamano())


if __name__ == "__main__":
    unittest.main()
