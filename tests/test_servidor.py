import tempfile
import unittest
from pathlib import Path

from network_os.logic.controller.servidor.servidor import Servidor
from network_os.persistencia.persistencias_servidorCSV.persistencias_servidorCSV import (
    PersistenciaServidorCSV,
)


class ServidorTests(unittest.TestCase):
    def test_construye_persistencias_y_registra_auditoria(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            servidor = Servidor("principal", 7, ruta_base)

            directorio_esperado = ruta_base / "servidores" / "principal_7"
            self.assertEqual("principal", servidor.nombre)
            self.assertEqual(7, servidor.id)
            self.assertEqual(directorio_esperado, servidor.persistencia.directorio)
            self.assertTrue(directorio_esperado.is_dir())

            servidor.auditoria.registrar(
                "SERVIDOR",
                "INICIAR",
                "EXITOSO",
                "Servidor iniciado.",
            )

            ruta_auditoria = directorio_esperado / "auditoria.csv"
            self.assertTrue(ruta_auditoria.is_file())
            self.assertEqual(1, len(servidor.auditoria.consultar_todo()))

    def test_rechaza_nombres_invalidos(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            for nombre in (None, "", "   ", "servidor/uno", "servidor\\uno"):
                with self.subTest(nombre=nombre):
                    with self.assertRaises(ValueError):
                        Servidor(nombre, 1, ruta_base)  # type: ignore[arg-type]

    def test_rechaza_ids_invalidos(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            for id_servidor in (None, -1, True, 1.5, "1"):
                with self.subTest(id_servidor=id_servidor):
                    with self.assertRaises(ValueError):
                        Servidor(
                            "principal",
                            id_servidor,  # type: ignore[arg-type]
                            ruta_base,
                        )

    def test_persistencia_rechaza_ruta_base_invalida(self) -> None:
        with self.assertRaises(ValueError):
            PersistenciaServidorCSV("   ", "principal", 1)
        with self.assertRaises(TypeError):
            PersistenciaServidorCSV(123, "principal", 1)  # type: ignore[arg-type]

    def test_agrega_y_persiste_un_usuario_valido(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            servidor = Servidor("principal", 1, Path(temporal))

            servidor.agregar_usuario("ana_01", "clave123")

            usuarios = servidor.persistencia.usuarios.cargar()
            self.assertEqual("clave123", usuarios.obtener("ana_01"))

    def test_rechaza_usuario_repetido(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            servidor = Servidor("principal", 1, Path(temporal))
            servidor.agregar_usuario("ana_01", "clave123")

            with self.assertRaises(ValueError):
                servidor.agregar_usuario("ana_01", "otra456")

    def test_rechaza_nombres_de_usuario_invalidos(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            servidor = Servidor("principal", 1, Path(temporal))

            for nombre in (None, "ab", "a" * 31, "ana maria", "ana@correo"):
                with self.subTest(nombre=nombre):
                    with self.assertRaises((TypeError, ValueError)):
                        servidor.agregar_usuario(
                            nombre,  # type: ignore[arg-type]
                            "clave123",
                        )

    def test_rechaza_contrasenas_invalidas(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            servidor = Servidor("principal", 1, Path(temporal))

            for contrasena in (None, "corta1", "sololetras", "12345678"):
                with self.subTest(contrasena=contrasena):
                    with self.assertRaises((TypeError, ValueError)):
                        servidor.agregar_usuario(
                            "ana_01",
                            contrasena,  # type: ignore[arg-type]
                        )

    def test_autentica_y_elimina_usuarios(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            servidor = Servidor("principal", 1, Path(temporal))
            servidor.agregar_usuario("ana_01", "clave123")

            self.assertTrue(servidor.autenticar_usuario("ana_01", "clave123"))
            self.assertFalse(servidor.autenticar_usuario("ana_01", "otra123"))
            self.assertTrue(servidor.eliminar_usuario("ana_01"))
            self.assertFalse(servidor.eliminar_usuario("ana_01"))
            self.assertFalse(servidor.autenticar_usuario("ana_01", "clave123"))

    def test_autentica_contrasenas_con_caracteres_no_ascii(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            servidor = Servidor("principal", 1, Path(temporal))
            servidor.agregar_usuario("bryan", "contraseña1")

            self.assertTrue(servidor.autenticar_usuario("bryan", "contraseña1"))
            self.assertFalse(servidor.autenticar_usuario("bryan", "contraseña2"))
            self.assertFalse(servidor.autenticar_usuario("bryan", "otra123"))

    def test_expone_operaciones_de_carpetas(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            servidor = Servidor("principal", 1, Path(temporal))

            documentos = servidor.crear_subcarpeta("documentos")
            self.assertEqual([documentos], servidor.listar_contenido())

            servidor.entrar_subcarpeta("documentos")
            servidor.renombrar_carpeta("archivos")
            servidor.crear_subcarpeta("internos")
            servidor.subir_nivel()

            self.assertEqual("archivos", documentos.nombre_carpeta)
            servidor.volver_a_raiz()
            self.assertIs(servidor.obtener_carpeta_actual(), servidor.gestor_archivos.raiz)

    def test_compartir_no_modifica_el_portapapeles_y_receptor_importa(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            origen = Servidor("origen", 1, ruta_base)
            destino = Servidor("destino", 2, ruta_base)

            compartida = origen.crear_subcarpeta("compartida")
            pendiente = origen.crear_subcarpeta("pendiente")
            origen.entrar_subcarpeta("compartida")
            origen.crear_subcarpeta("interna")
            origen.gestor_archivos.crear_nuevo_archivo("datos.txt", ["dato"])
            origen.volver_a_raiz()

            origen.cortar_subcarpeta(pendiente.id)
            paquete = origen.compartir_subcarpeta(compartida.id, destino.nombre)
            origen.pegar_subcarpeta()

            self.assertEqual("SUBCARPETA", paquete.tipo)
            self.assertIsNot(paquete.contenido, compartida)
            self.assertIsNotNone(
                origen.obtener_carpeta_actual().buscar_subcarpeta_por_nombre(
                    "pendiente"
                )
            )

            destino.recibir_paquete(paquete)
            recibida = destino.obtener_carpeta_actual().buscar_subcarpeta_por_nombre(
                "compartida"
            )
            self.assertIsNotNone(recibida)
            assert recibida is not None
            self.assertIsNot(recibida, paquete.contenido)
            self.assertIsNotNone(recibida.buscar_subcarpeta_por_nombre("interna"))
            self.assertEqual("datos.txt", recibida.listar_archivos()[0].nombre)

    def test_guarda_y_carga_el_estado_completo(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta_base = Path(temporal)
            servidor = Servidor("principal", 1, ruta_base)
            servidor.agregar_usuario("ana_01", "clave123")
            documentos = servidor.crear_subcarpeta("documentos")
            servidor.entrar_subcarpeta("documentos")
            archivo = servidor.gestor_archivos.crear_nuevo_archivo(
                "datos.txt",
                "contenido",
            )
            servidor.guardar_estado()

            recargado = Servidor("principal", 1, ruta_base)
            self.assertTrue(recargado.autenticar_usuario("ana_01", "clave123"))
            documentos_cargados = (
                recargado.obtener_carpeta_actual().buscar_subcarpeta_por_nombre(
                    "documentos"
                )
            )
            self.assertIsNotNone(documentos_cargados)
            assert documentos_cargados is not None
            self.assertEqual("datos.txt", documentos_cargados.listar_archivos()[0].nombre)

            nueva = recargado.crear_subcarpeta("nueva")
            self.assertGreater(nueva.id, max(documentos.id, archivo.id))


if __name__ == "__main__":
    unittest.main()
