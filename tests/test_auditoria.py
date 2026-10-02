import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from network_os.logic.controller.AuditoriaServidor.auditoria_servidor import (
    AuditoriaServidor,
)
from network_os.logic.model.registro_auditoria.registro_auditoria import (
    RegistroAuditoria,
)
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)


class AuditoriaTests(unittest.TestCase):
    def test_registro_rechaza_datos_invalidos(self) -> None:
        casos_invalidos = (
            ("fecha", "categoria", "accion", "resultado", "detalle"),
            (datetime.now(), "", "accion", "resultado", "detalle"),
            (datetime.now(), "categoria", "", "resultado", "detalle"),
            (datetime.now(), "categoria", "accion", "", "detalle"),
            (datetime.now(), "categoria", "accion", "resultado", None),
        )

        for datos in casos_invalidos:
            with self.subTest(datos=datos):
                with self.assertRaises((TypeError, ValueError)):
                    RegistroAuditoria(*datos)

    def test_persistencia_rechaza_ruta_y_registro_invalidos(self) -> None:
        with self.assertRaises(TypeError):
            PersistenciaAuditoriaCSV("auditoria.csv")

        with tempfile.TemporaryDirectory() as directorio:
            persistencia = PersistenciaAuditoriaCSV(
                Path(directorio) / "auditoria.csv"
            )

            with self.assertRaises(TypeError):
                persistencia.agregar("registro")

    def test_persistencia_crea_directorios_y_escapa_datos_csv(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "logs" / "auditoria.csv"
            persistencia = PersistenciaAuditoriaCSV(ruta)
            registro = RegistroAuditoria(
                datetime(2026, 9, 27, 12, 30),
                "archivos, carpetas",
                "crear",
                "exito",
                "Detalle con coma, y salto\nde linea",
            )

            persistencia.agregar(registro)

            self.assertTrue(ruta.exists())
            self.assertEqual([registro], persistencia.consultar_todo())

    def test_consultar_archivo_inexistente_devuelve_lista_vacia(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            persistencia = PersistenciaAuditoriaCSV(
                Path(directorio) / "inexistente.csv"
            )

            self.assertEqual([], persistencia.consultar_todo())

    def test_persistencia_reconstruye_registros_desde_csv(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            persistencia = PersistenciaAuditoriaCSV(
                Path(directorio) / "auditoria.csv"
            )
            registro = RegistroAuditoria(
                datetime(2026, 9, 27, 12, 30),
                "archivos",
                "crear",
                "exito",
                "Se creo la carpeta documentos",
            )

            persistencia.agregar(registro)

            self.assertEqual([registro], persistencia.consultar_todo())

    def test_consultar_ultimos_conserva_el_orden_de_insercion(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            persistencia = PersistenciaAuditoriaCSV(
                Path(directorio) / "auditoria.csv"
            )
            registros = [
                RegistroAuditoria(
                    datetime(2026, 9, 27, indice),
                    "red",
                    "accion",
                    "ok",
                    str(indice),
                )
                for indice in range(3)
            ]
            for registro in registros:
                persistencia.agregar(registro)

            self.assertEqual(registros[1:], persistencia.consultar_ultimos(2))
            self.assertEqual([], persistencia.consultar_ultimos(0))

    def test_auditoria_servidor_crea_y_consulta_registro(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            persistencia = PersistenciaAuditoriaCSV(
                Path(directorio) / "auditoria.csv"
            )
            auditoria = AuditoriaServidor("servidor-1", persistencia)

            auditoria.registrar(
                "usuarios", "autenticar", "exito", "Acceso concedido"
            )

            registros = auditoria.consultar_todo()
            self.assertEqual(1, len(registros))
            self.assertEqual("usuarios", registros[0].categoria)
            self.assertEqual("autenticar", registros[0].accion)
            self.assertIsInstance(registros[0].fecha_hora, datetime)
            self.assertEqual(
                timedelta(hours=-6), registros[0].fecha_hora.utcoffset()
            )

    def test_rechaza_cantidad_invalida(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            persistencia = PersistenciaAuditoriaCSV(
                Path(directorio) / "auditoria.csv"
            )

            for cantidad in (-1, 1.5, True):
                with self.subTest(cantidad=cantidad):
                    with self.assertRaises(ValueError):
                        persistencia.consultar_ultimos(cantidad)


if __name__ == "__main__":
    unittest.main()
