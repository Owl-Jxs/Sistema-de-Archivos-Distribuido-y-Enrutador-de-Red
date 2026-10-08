import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from network_os.logic.controller.auditoria.auditoria import (
    Auditoria,
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

    def test_conserva_y_amplia_log_antiguo_sin_origen(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "auditoria.csv"
            ruta.write_text(
                "fecha_hora,categoria,accion,resultado,detalle\n"
                "2026-09-27T12:30:00,USUARIOS,AGREGAR_USUARIO,EXITOSO,Usuario ana\n",
                encoding="utf-8",
            )
            historial = ruta.read_bytes()
            auditoria = Auditoria("SERVIDOR:principal (1)", PersistenciaAuditoriaCSV(ruta))

            auditoria.registrar("ARCHIVOS", "CREAR_ARCHIVO", "EXITOSO", "Archivo tarea")

            self.assertTrue(ruta.read_bytes().startswith(historial))
            registros = auditoria.consultar_todo()
            self.assertEqual(2, len(registros))
            self.assertEqual("DESCONOCIDO", registros[0].origen)
            self.assertEqual("Usuario ana", registros[0].detalle)
            self.assertEqual(auditoria.origen, registros[1].origen)
            self.assertEqual("CREAR_ARCHIVO", registros[1].accion)
            self.assertEqual("Archivo tarea", registros[1].detalle)

    def test_append_respeta_orden_del_encabezado_existente(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "network_audit_log.txt"
            ruta.write_text(
                "fecha_hora,origen,categoria,accion,resultado,detalle\n"
                "2026-09-27T12:30:00,RED,RED,AGREGAR_SERVIDOR,EXITOSO,Servidor principal\n",
                encoding="utf-8",
            )
            historial = ruta.read_bytes()
            auditoria = Auditoria("RED", PersistenciaAuditoriaCSV(ruta))

            auditoria.registrar("RED", "PING_GENERAL", "EXITOSO", "Origen principal")

            self.assertTrue(ruta.read_bytes().startswith(historial))
            registros = auditoria.consultar_todo()
            self.assertEqual(2, len(registros))
            self.assertEqual("RED", registros[1].origen)
            self.assertEqual("PING_GENERAL", registros[1].accion)
            self.assertEqual("Origen principal", registros[1].detalle)

    def test_auditoria_crea_y_consulta_registro(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            persistencia = PersistenciaAuditoriaCSV(
                Path(directorio) / "auditoria.csv"
            )
            auditoria = Auditoria("servidor-1", persistencia)

            auditoria.registrar(
                "usuarios", "autenticar", "exito", "Acceso concedido"
            )

            registros = auditoria.consultar_todo()
            self.assertEqual(1, len(registros))
            self.assertEqual("servidor-1", registros[0].origen)
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
