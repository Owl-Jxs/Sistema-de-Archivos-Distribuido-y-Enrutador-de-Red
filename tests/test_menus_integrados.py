import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from network_os.consola.principal.menu_consola import MenuConsola
from network_os.consola.red.menu_red import MenuRed
from network_os.consola.servidor.menu_archivos import MenuArchivos
from network_os.consola.servidor.menu_servidor import MenuServidor
from network_os.consola.servidor.usuarios_locales import usuarios_locales
from network_os.logic.controller.auditoria.auditoria import Auditoria
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed
from network_os.logic.controller.servidor.servidor import Servidor
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)


class MenusIntegradosTests(unittest.TestCase):
    def setUp(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.base = Path(temporal.name)
        self.auditoria = Auditoria(
            "RED", PersistenciaAuditoriaCSV(self.base / "network_audit_log.txt"),
        )
        self.grafo = GrafoRed(self.base / "red.csv", auditoria=self.auditoria)
        self.servidor = Servidor("principal", 1, self.base)
        self.destino = Servidor("secundario", 2, self.base)
        self.grafo.agregar_servidor(self.servidor)
        self.grafo.agregar_servidor(self.destino)
        self.servidor.agregar_usuario("ana", "ClavePrivada123")
        self.menu = MenuConsola(self.grafo)
        self.archivos = MenuArchivos(self.servidor)
        self.menu_servidor = MenuServidor(self.grafo, self.servidor)

    def ejecutar_con_entradas(self, operacion, entradas) -> str:
        salida = io.StringIO()
        with patch("builtins.input", side_effect=entradas) as entrada, redirect_stdout(salida):
            operacion()
        self.assertEqual(len(entradas), entrada.call_count)
        return salida.getvalue()

    def test_submenus_regresan_con_cero_sin_pausas_adicionales(self) -> None:
        for operacion in (
            self.archivos.menu_archivos,
            self.menu_servidor.menu_servidor,
            MenuRed(self.grafo).menu_red,
        ):
            with self.subTest(menu=operacion):
                self.ejecutar_con_entradas(operacion, ["0"])

    def test_recorrido_completo_de_sesion_y_submenus(self) -> None:
        with patch("network_os.consola.principal.menu_consola.getpass", return_value="ClavePrivada123"):
            salida = self.ejecutar_con_entradas(self.menu.ejecutar, [
                "2", "principal", "ana", "1", "0", "2", "0",
                "3", "secundario", "contenido privado", "", "0", "0",
            ])
        self.assertIsNone(self.menu._MenuConsola__servidor_actual)
        self.assertEqual(1, salida.count("Sesion cerrada."))
        self.assertNotIn("ClavePrivada123", salida)
        self.assertNotIn("contenido privado", salida)
        self.assertIn("Paquete no entregado", salida)
        registros = self.grafo.consultar_auditoria()
        self.assertEqual(1, sum(r.accion == "ENVIAR_PAQUETE" for r in registros))
        self.assertFalse(any(r.accion == "RUTA_MAS_CORTA" for r in registros))

    def test_sesion_se_limpia_si_el_submenu_falla(self) -> None:
        with patch("network_os.consola.principal.menu_consola.getpass", return_value="ClavePrivada123"), patch.object(
            MenuConsola, "menu_servidor", side_effect=RuntimeError("prueba"),
        ), patch("builtins.input", side_effect=["principal", "ana"]), redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError):
                self.menu.iniciar_sesion()
        self.assertIsNone(self.menu._MenuConsola__servidor_actual)

    def test_metodos_anteriores_sin_sesion_no_piden_entradas(self) -> None:
        for operacion in (
            self.menu.menu_servidor, self.menu.menu_archivos,
            self.menu.menu_usuarios, self.menu.enviar_paquete,
        ):
            salida = self.ejecutar_con_entradas(operacion, [])
            self.assertIn("No hay una sesion activa", salida)

    def test_archivos_creacion_navegacion_busqueda_arbol_y_persistencia(self) -> None:
        red_antes = self.grafo.consultar_auditoria()
        salida = self.ejecutar_con_entradas(self.archivos.menu_archivos, [
            "x", "3", "docs", "", "2", "1", "docs", "",
            "4", "tarea.txt", "contenido de tarea", "", "1", "",
            "5", "tarea.txt", "", "6", "", "0",
        ])
        self.assertIn("Opcion invalida", salida)
        self.assertIn("[Archivo]", salida)
        self.assertIn("Archivo encontrado: tarea.txt", salida)
        self.assertIn("principal/", salida)
        recargado = Servidor("principal", 1, self.base)
        recargado.entrar_subcarpeta("docs")
        self.assertEqual("contenido de tarea", recargado.buscar_archivo("tarea.txt").contenido)
        self.assertEqual(red_antes, self.grafo.consultar_auditoria())
        registros = self.servidor.consultar_auditoria()
        self.assertEqual(1, sum(r.accion == "CREAR_SUBCARPETA" for r in registros))
        self.assertEqual(1, sum(r.accion == "CREAR_ARCHIVO" for r in registros))

    def test_navegacion_anidada_y_error_conservan_carpeta_actual(self) -> None:
        carpeta = self.servidor.crear_subcarpeta("docs")
        self.ejecutar_con_entradas(self.archivos.navegar, ["1", "docs"])
        hija = self.servidor.crear_subcarpeta("hija")
        self.ejecutar_con_entradas(self.archivos.navegar, ["1", "hija"])
        with patch("builtins.input", side_effect=["1", "fantasma"]):
            with self.assertRaises(ValueError):
                self.archivos.navegar()
        self.assertIs(hija, self.servidor.obtener_carpeta_actual())
        self.ejecutar_con_entradas(self.archivos.navegar, ["2"])
        self.assertIs(carpeta, self.servidor.obtener_carpeta_actual())
        self.ejecutar_con_entradas(self.archivos.navegar, ["3"])
        self.assertEqual(0, self.servidor.obtener_carpeta_actual().id)

    def test_listado_es_directo_y_busqueda_recursiva_desde_otra_carpeta(self) -> None:
        self.servidor.crear_subcarpeta("docs")
        self.servidor.crear_subcarpeta("otra")
        self.servidor.entrar_subcarpeta("docs")
        self.servidor.crear_nuevo_archivo("profundo.txt")
        self.servidor.volver_a_raiz()
        listado = self.ejecutar_con_entradas(self.archivos.listar_contenido, [])
        self.assertIn("docs", listado)
        self.assertIn("otra", listado)
        self.assertNotIn("profundo.txt", listado)
        self.servidor.entrar_subcarpeta("otra")
        self.assertIn("esta vacia", self.ejecutar_con_entradas(self.archivos.listar_contenido, []))
        self.assertIn("Archivo encontrado", self.ejecutar_con_entradas(self.archivos.buscar_archivo, ["profundo.txt"]))
        self.assertIn("No se encontro", self.ejecutar_con_entradas(self.archivos.buscar_archivo, ["ausente.txt"]))

    def test_eliminacion_carpeta_cancelada_y_confirmada_en_cascada(self) -> None:
        carpeta = self.servidor.crear_subcarpeta("docs")
        hermana = self.servidor.crear_subcarpeta("hermana")
        self.servidor.entrar_subcarpeta("docs")
        self.servidor.crear_subcarpeta("hija")
        self.servidor.crear_nuevo_archivo("privado.txt")
        self.servidor.volver_a_raiz()
        anteriores = self.servidor.consultar_auditoria()
        salida = self.ejecutar_con_entradas(self.archivos.eliminar_elemento, ["2", str(carpeta.id), "n"])
        self.assertIn("Eliminacion cancelada", salida)
        self.assertIn(carpeta, self.servidor.listar_contenido())
        self.assertEqual(anteriores, self.servidor.consultar_auditoria())
        self.ejecutar_con_entradas(self.archivos.eliminar_elemento, ["2", str(carpeta.id), "s"])
        recargado = Servidor("principal", 1, self.base)
        self.assertEqual([hermana.nombre_carpeta], [c.nombre_carpeta for c in recargado.listar_contenido()])
        self.assertIsNone(recargado.buscar_archivo("privado.txt"))

    def test_eliminar_archivo_persiste_sin_eliminar_la_carpeta(self) -> None:
        archivo = self.servidor.crear_nuevo_archivo("datos.txt")
        self.ejecutar_con_entradas(self.archivos.eliminar_elemento, ["1", str(archivo.id), "S"])
        recargado = Servidor("principal", 1, self.base)
        self.assertEqual([], recargado.listar_contenido())
        self.assertEqual(0, recargado.obtener_carpeta_actual().id)

    def test_menu_archivos_recupera_errores_y_protege_la_raiz(self) -> None:
        self.servidor.crear_nuevo_archivo("datos.txt")
        for entradas in (
            ["7", "2", "0", "", "0"],
            ["7", "1", "abc", "", "0"],
            ["3", "", "", "0"],
            ["2", "1", "fantasma", "", "0"],
        ):
            with self.subTest(entradas=entradas):
                salida = self.ejecutar_con_entradas(self.archivos.menu_archivos, entradas)
                self.assertIn("No se pudo completar", salida)
                self.assertEqual(0, self.servidor.obtener_carpeta_actual().id)
                self.assertIsNotNone(self.servidor.buscar_archivo("datos.txt"))

    def test_error_de_guardado_no_anuncia_creacion_exitosa(self) -> None:
        with patch.object(self.servidor, "guardar_estado", side_effect=OSError("sin espacio")):
            salida = self.ejecutar_con_entradas(self.archivos.menu_archivos, ["3", "docs", "", "0"])
        self.assertIn("No se pudo completar", salida)
        self.assertNotIn("creada con ID", salida)

    def test_usuarios_conserva_funciones_y_muestra_resultado_real(self) -> None:
        with patch("network_os.consola.servidor.usuarios_locales.getpass", return_value="OtraClave123"):
            salida = self.ejecutar_con_entradas(lambda: usuarios_locales(self.servidor), [
                "x", "1", "bea", "2", "fantasma", "s", "0",
            ])
        self.assertIn("Usuario 'bea' registrado", salida)
        self.assertIn("El usuario 'fantasma' no existe", salida)
        self.assertNotIn("OtraClave123", salida)
        self.assertTrue(self.servidor.autenticar_usuario("bea", "OtraClave123"))

    def test_red_conexiones_latencia_listado_ping_y_guardado(self) -> None:
        salida = self.ejecutar_con_entradas(MenuRed(self.grafo).menu_red, [
            "3", "1", "principal", "secundario", "",
            "4", "principal", "secundario", "2", "", "1", "",
            "5", "principal", "", "3", "2", "principal", "secundario", "", "0",
        ])
        self.assertEqual(1, salida.count("principal <-> secundario"))
        self.assertIn("secundario: 2.0 ms", salida)
        self.assertTrue(self.grafo.persistencia.ruta_conexiones_csv.exists())
        self.assertEqual([], self.grafo.buscar_vertice("principal").conexiones)

    def test_menu_crea_conexion_sin_pedir_ms_y_muestra_latencia_simulada(self) -> None:
        with patch(
            "network_os.logic.controller.grafo_red.grafoRed.randint", return_value=37,
        ):
            salida = self.ejecutar_con_entradas(MenuRed(self.grafo).menu_red, [
                "3", "1", "principal", "secundario", "", "0",
            ])
        self.assertIn("Latencia simulada: 37 ms", salida)
        principal = self.grafo.buscar_vertice("principal")
        secundario = self.grafo.buscar_vertice("secundario")
        self.assertEqual(37, principal.buscar_conexion(secundario).latencia_ms)
        self.assertEqual(37, secundario.buscar_conexion(principal).latencia_ms)
        self.assertEqual(1, sum(r.accion == "AGREGAR_CONEXION" for r in self.grafo.consultar_auditoria()))

    def test_ping_en_menu_red_conectada(self) -> None:
        self.grafo.agregar_conexion("principal", "secundario", 7)
        salida = self.ejecutar_con_entradas(MenuRed(self.grafo).menu_red, ["5", "principal", "", "0"])
        self.assertIn("Todos los servidores estan comunicados", salida)
        self.assertIn("Servidores aislados: ninguno", salida)
        self.assertIn("secundario: 7 ms", salida)

    def test_ping_en_menu_distingue_fragmentacion_y_aislamiento(self) -> None:
        for indice, nombre in enumerate(("C", "D", "E"), start=3):
            self.grafo.agregar_servidor(Servidor(nombre, indice, self.base))
        self.grafo.agregar_conexion("principal", "secundario", 7)
        self.grafo.agregar_conexion("C", "D", 3)
        salida = self.ejecutar_con_entradas(MenuRed(self.grafo).menu_red, ["5", "principal", "", "0"])
        self.assertIn("Red fragmentada", salida)
        self.assertIn("C: inalcanzable (en otro componente de la red)", salida)
        self.assertIn("D: inalcanzable (en otro componente de la red)", salida)
        self.assertIn("E: inalcanzable (servidor aislado)", salida)
        self.assertIn("Servidores aislados: E.", salida)
        self.assertEqual(1, sum(r.accion == "PING_GENERAL" for r in self.grafo.consultar_auditoria()))

    def test_ping_en_menu_incluye_origen_aislado(self) -> None:
        salida = self.ejecutar_con_entradas(MenuRed(self.grafo).menu_red, ["5", "principal", "", "0"])
        self.assertIn("secundario: inalcanzable (servidor aislado)", salida)
        self.assertIn("Servidores aislados: principal, secundario", salida)

    def test_ping_en_menu_con_un_solo_servidor(self) -> None:
        self.grafo.eliminar_servidor("secundario")
        salida = self.ejecutar_con_entradas(MenuRed(self.grafo).menu_red, ["5", "principal", "", "0"])
        self.assertIn("No hay otros servidores en la red", salida)
        self.assertIn("Servidores aislados: principal", salida)
        self.assertNotIn("Red fragmentada", salida)

    def test_red_agregar_servidor_usa_directorio_de_la_red(self) -> None:
        self.ejecutar_con_entradas(MenuRed(self.grafo).menu_red, ["2", "1", "nuevo", "", "0"])
        nuevo = self.grafo.buscar_vertice("nuevo").servidor
        self.assertEqual(3, nuevo.id)
        self.assertEqual(self.base / "servidores" / "nuevo_3", nuevo.persistencia.directorio)
        self.assertIsNot(self.auditoria, nuevo.auditoria)

    def test_red_eliminar_servidor_confirma_y_no_duplica_eventos(self) -> None:
        self.grafo.agregar_conexion("principal", "secundario", 4)
        self.ejecutar_con_entradas(MenuRed(self.grafo).menu_red, [
            "2", "2", "secundario", "n", "", "2", "2", "secundario", "s", "", "0",
        ])
        self.assertEqual(["principal"], [v.servidor.nombre for v in self.grafo.vertices])
        self.assertEqual([], self.grafo.buscar_vertice("principal").conexiones)
        self.assertEqual(1, sum(r.accion == "ELIMINAR_SERVIDOR" for r in self.grafo.consultar_auditoria()))

    def test_red_recupera_latencia_invalida(self) -> None:
        salida = self.ejecutar_con_entradas(MenuRed(self.grafo).menu_red, [
            "4", "principal", "secundario", "abc", "", "0",
        ])
        self.assertIn("No se pudo completar", salida)

    def test_paquete_muestra_saltos_costo_y_entrega_contenido(self) -> None:
        intermedio = Servidor("intermedio", 3, self.base)
        self.grafo.agregar_servidor(intermedio)
        self.grafo.agregar_conexion("principal", "secundario", 20)
        self.grafo.agregar_conexion("principal", "intermedio", 3)
        self.grafo.agregar_conexion("intermedio", "secundario", 4)
        red_antes = self.grafo.consultar_auditoria()
        with patch.object(self.destino, "recibir_paquete", wraps=self.destino.recibir_paquete) as recibir:
            salida = self.ejecutar_con_entradas(self.menu_servidor.enviar_paquete, ["secundario", "privado"])
        recibir.assert_called_once()
        self.assertIn("Salto 1: principal -> intermedio", salida)
        self.assertIn("Salto 2: intermedio -> secundario", salida)
        self.assertIn("Costo total: 7 ms", salida)
        self.assertIn("Paquete entregado.", salida)
        self.assertNotIn("privado", salida)
        nuevos = self.grafo.consultar_auditoria()[len(red_antes):]
        self.assertEqual(["ENVIAR_PAQUETE"], [r.accion for r in nuevos])
        self.assertEqual("privado", self.destino.listar_contenido()[0].contenido)
        recargado = Servidor("secundario", 2, self.base)
        self.assertEqual("privado", recargado.listar_contenido()[0].contenido)

    def test_paquete_inalcanzable_cancelacion_y_entrada_invalida(self) -> None:
        salida = self.ejecutar_con_entradas(self.menu_servidor.enviar_paquete, ["secundario", "hola"])
        self.assertIn("Paquete no entregado", salida)
        anteriores = self.grafo.consultar_auditoria()
        self.ejecutar_con_entradas(self.menu_servidor.enviar_paquete, [""])
        self.assertEqual(anteriores, self.grafo.consultar_auditoria())
        salida = self.ejecutar_con_entradas(self.menu_servidor.menu_servidor, ["3", "fantasma", "", "0"])
        self.assertIn("No se pudo enviar", salida)
        salida = self.ejecutar_con_entradas(self.menu_servidor.menu_servidor, ["3", "secundario", "", "", "0"])
        self.assertIn("contenido del paquete no puede estar vacio", salida)

    def test_consulta_general_no_mezcla_logs_locales_ni_agrega_eventos(self) -> None:
        self.servidor.crear_subcarpeta("carpeta_privada")
        anteriores = self.grafo.consultar_auditoria()
        salida = self.ejecutar_con_entradas(self.menu.menu_auditoria, ["1", "", "0"])
        self.assertIn("AGREGAR_SERVIDOR", salida)
        self.assertNotIn("carpeta_privada", salida)
        self.assertNotIn("ClavePrivada123", salida)
        self.assertEqual(anteriores, self.grafo.consultar_auditoria())

    def test_consulta_de_log_vacio_permite_volver(self) -> None:
        grafo = GrafoRed(
            self.base / "vacio.csv",
            auditoria=Auditoria("RED", PersistenciaAuditoriaCSV(self.base / "vacio.txt")),
        )
        salida = self.ejecutar_con_entradas(MenuConsola(grafo).menu_auditoria, ["1", "", "0"])
        self.assertIn("No hay registros", salida)

    def test_sesion_permite_consultar_solo_auditoria_del_servidor_activo(self) -> None:
        self.servidor.crear_subcarpeta("privada_principal")
        self.destino.crear_subcarpeta("privada_secundario")
        red_antes = self.grafo.consultar_auditoria()
        locales_antes = self.servidor.consultar_auditoria()
        destino_antes = self.destino.consultar_auditoria()
        with patch(
            "network_os.consola.principal.menu_consola.getpass", return_value="ClavePrivada123",
        ), patch.object(
            self.grafo, "consultar_auditoria", side_effect=AssertionError("Consulta de red inesperada"),
        ), patch.object(
            self.destino, "consultar_auditoria", side_effect=AssertionError("Consulta de otro servidor"),
        ):
            salida = self.ejecutar_con_entradas(self.menu.ejecutar, [
                "2", "principal", "ana", "4", "1", "", "0", "0", "0",
            ])
        self.assertIn("AUDITORIA LOCAL | principal", salida)
        self.assertIn("SERVIDOR:principal (1)", salida)
        self.assertIn("privada_principal", salida)
        self.assertNotIn("privada_secundario", salida)
        self.assertNotIn("AGREGAR_SERVIDOR", salida)
        self.assertNotIn("ClavePrivada123", salida)
        self.assertEqual(red_antes, self.grafo.consultar_auditoria())
        self.assertEqual(destino_antes, self.destino.consultar_auditoria())
        nuevos = self.servidor.consultar_auditoria()[len(locales_antes):]
        self.assertEqual(["AUTENTICAR_USUARIO"], [r.accion for r in nuevos])
        self.assertIsNone(self.menu._MenuConsola__servidor_actual)

    def test_consulta_local_de_servidor_sin_log_muestra_vacio(self) -> None:
        menu = MenuServidor(self.grafo, self.destino)
        red_antes = self.grafo.consultar_auditoria()
        salida = self.ejecutar_con_entradas(menu.menu_auditoria, ["1", "", "0"])
        self.assertIn("AUDITORIA LOCAL | secundario", salida)
        self.assertIn("No hay registros de auditoria local", salida)
        self.assertEqual([], self.destino.consultar_auditoria())
        self.assertFalse(self.destino.auditoria.persistencia.ruta_csv.exists())
        self.assertEqual(red_antes, self.grafo.consultar_auditoria())

    def test_consulta_local_recupera_errores_sin_modificar_logs(self) -> None:
        locales_antes = self.servidor.consultar_auditoria()
        red_antes = self.grafo.consultar_auditoria()
        for error in (OSError("sin acceso"), ValueError("registro invalido"), TypeError("tipo invalido")):
            with self.subTest(error=type(error).__name__), patch.object(
                self.servidor, "consultar_auditoria", side_effect=error,
            ):
                salida = self.ejecutar_con_entradas(self.menu_servidor.menu_auditoria, ["1", "", "0"])
            self.assertIn("No se pudo consultar la auditoria local", salida)
        self.assertEqual(locales_antes, self.servidor.consultar_auditoria())
        self.assertEqual(red_antes, self.grafo.consultar_auditoria())

    def test_auditoria_local_vuelve_con_cero_sin_leer_registros(self) -> None:
        with patch.object(self.servidor, "consultar_auditoria") as consultar:
            self.ejecutar_con_entradas(self.menu_servidor.menu_auditoria, ["0"])
        consultar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
