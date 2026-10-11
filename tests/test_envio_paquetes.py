import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from network_os.logic.controller.auditoria.auditoria import Auditoria
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed
from network_os.logic.controller.servidor.servidor import Servidor
from network_os.logic.model.paquete_datos.paquete_datos import PaqueteDatos
from network_os.logic.model.resultado_envio.resultadoEnvio import ResultadoEnvio
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)


class EnvioPaquetesTests(unittest.TestCase):
    def setUp(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.base = Path(temporal.name)
        self.grafo = GrafoRed(
            self.base / "red.csv",
            auditoria=Auditoria("RED", PersistenciaAuditoriaCSV(self.base / "network_audit_log.txt")),
        )
        self.origen = Servidor("origen", 1, self.base)
        self.destino = Servidor("destino", 2, self.base)
        for servidor in (self.origen, self.destino):
            self.grafo.agregar_servidor(servidor)
        self.grafo.agregar_conexion("origen", "destino", 20)

    def enviar(self, contenido="contenido privado") -> ResultadoEnvio:
        paquete = self.origen.crear_paquete("destino", contenido)
        return self.origen.enviar_paquete(self.grafo, paquete)

    def test_texto_entregado_en_carpeta_actual_y_conservado_al_recargar(self) -> None:
        carpeta = self.destino.crear_subcarpeta("entrada")
        self.destino.entrar_subcarpeta("entrada")
        resultado = self.enviar("hola\nsegunda linea, con coma")
        self.assertIsInstance(resultado, ResultadoEnvio)
        self.assertTrue(resultado.entregado)
        self.assertEqual(["origen", "destino"], resultado.ruta)
        self.assertEqual(20, resultado.latencia_total_ms)
        archivo = carpeta.listar_archivos()[0]
        self.assertTrue(archivo.nombre.startswith("mensaje_"))
        self.assertTrue(archivo.nombre.endswith(".txt"))
        recargado = Servidor("destino", 2, self.base)
        self.assertEqual("hola\nsegunda linea, con coma", recargado.buscar_archivo(archivo.nombre).contenido)
        self.assertEqual([], self.origen.listar_contenido())

    def test_ruta_indirecta_mas_barata_ciclo_y_una_sola_busqueda(self) -> None:
        intermedio = Servidor("intermedio", 3, self.base)
        self.grafo.agregar_servidor(intermedio)
        self.grafo.agregar_conexion("origen", "intermedio", 3)
        self.grafo.agregar_conexion("intermedio", "destino", 4)
        with patch.object(self.grafo, "dijkstra", wraps=self.grafo.dijkstra) as dijkstra, patch.object(
            self.destino, "recibir_paquete", wraps=self.destino.recibir_paquete,
        ) as recibir, patch.object(intermedio, "recibir_paquete") as recibir_intermedio:
            resultado = self.enviar()
        dijkstra.assert_called_once_with("origen")
        recibir.assert_called_once()
        recibir_intermedio.assert_not_called()
        self.assertTrue(resultado.entregado)
        self.assertEqual(["origen", "intermedio", "destino"], resultado.ruta)
        self.assertEqual(7, resultado.latencia_total_ms)
        self.assertEqual([], intermedio.consultar_auditoria())

    def test_destino_aislado_no_recibe_y_eventos_son_fallidos(self) -> None:
        self.grafo.eliminar_conexion("origen", "destino")
        with patch.object(self.destino, "recibir_paquete") as recibir:
            resultado = self.enviar()
        recibir.assert_not_called()
        self.assertFalse(resultado.entregado)
        self.assertEqual([], resultado.ruta)
        self.assertEqual(math.inf, resultado.latencia_total_ms)
        self.assertIn("No existe una ruta", resultado.mensaje)
        self.assertEqual([], self.destino.listar_contenido())
        self.assertEqual("FALLIDO", self.origen.consultar_auditoria()[-1].resultado)
        self.assertEqual("FALLIDO", self.grafo.consultar_auditoria()[-1].resultado)
        self.assertEqual([], self.destino.consultar_auditoria())

    def test_origen_igual_al_destino_con_costo_cero(self) -> None:
        paquete = self.origen.crear_paquete("origen", "mensaje local")
        resultado = self.origen.enviar_paquete(self.grafo, paquete)
        self.assertTrue(resultado.entregado)
        self.assertEqual(["origen"], resultado.ruta)
        self.assertEqual(0, resultado.latencia_total_ms)
        self.assertEqual(["RECIBIR_PAQUETE", "ENVIAR_PAQUETE"], [r.accion for r in self.origen.consultar_auditoria()])

    def test_origen_o_destino_inexistente_se_rechaza(self) -> None:
        for origen, destino in (("fantasma", "destino"), ("origen", "fantasma")):
            with self.subTest(origen=origen, destino=destino):
                with self.assertRaises(ValueError):
                    self.grafo.enviar_paquete(PaqueteDatos(origen, destino, "STR", "dato"))
                self.assertEqual("ERROR", self.grafo.consultar_auditoria()[-1].resultado)
        self.assertEqual([], self.destino.listar_contenido())

    def test_argumentos_invalidos_y_origen_ajeno(self) -> None:
        with self.assertRaises(TypeError):
            self.grafo.enviar_paquete("contenido privado")
        for grafo, paquete, error in (
            (None, self.origen.crear_paquete("destino", "hola"), TypeError),
            (self.grafo, None, TypeError),
            (self.grafo, self.destino.crear_paquete("destino", "hola"), ValueError),
        ):
            with self.subTest(error=error, grafo=grafo):
                with self.assertRaises(error):
                    self.origen.enviar_paquete(grafo, paquete)
        otro = Servidor("origen", 9, self.base)
        with self.assertRaises(ValueError):
            otro.enviar_paquete(self.grafo, otro.crear_paquete("destino", "hola"))
        self.assertEqual([], self.destino.listar_contenido())

    def test_latencia_negativa_no_confirma_entrega(self) -> None:
        self.grafo.buscar_vertice("origen").conexiones[0].latencia_ms = -1
        with self.assertRaises(ValueError):
            self.enviar()
        self.assertEqual([], self.destino.listar_contenido())
        self.assertEqual("ERROR", self.origen.consultar_auditoria()[-1].resultado)

    def test_tipos_incompatibles_y_texto_vacio_no_se_entregan(self) -> None:
        for tipo, contenido in (("ARCHIVO", "texto"), ("SUBCARPETA", 3), ("STR", "  "), ("LIST", [1])):
            with self.subTest(tipo=tipo, contenido=contenido):
                resultado = self.origen.enviar_paquete(
                    self.grafo, PaqueteDatos("origen", "destino", tipo, contenido),
                )
                self.assertFalse(resultado.entregado)
                self.assertEqual("ERROR", self.destino.consultar_auditoria()[-1].resultado)
                self.assertEqual("FALLIDO", self.grafo.consultar_auditoria()[-1].resultado)
        self.assertEqual([], self.destino.listar_contenido())

    def test_recibir_directamente_rechaza_paquete_ajeno_o_invalido(self) -> None:
        with self.assertRaises(TypeError):
            self.destino.recibir_paquete(None)
        with self.assertRaises(ValueError):
            self.destino.recibir_paquete(self.origen.crear_paquete("origen", "hola"))
        self.assertEqual([], self.destino.listar_contenido())

    def test_reenvio_de_texto_genera_nombres_unicos_sin_sobrescribir(self) -> None:
        paquete = self.origen.crear_paquete("destino", "hola")
        for _ in range(2):
            self.assertTrue(self.origen.enviar_paquete(self.grafo, paquete).entregado)
        archivos = self.destino.listar_contenido()
        self.assertNotEqual(archivos[0].nombre, archivos[1].nombre)
        self.assertNotEqual(archivos[0].id, archivos[1].id)
        self.assertEqual(["hola", "hola"], [a.contenido for a in archivos])

    def test_archivo_se_copia_con_id_propio_y_sin_compartir_contenido(self) -> None:
        original = self.origen.crear_nuevo_archivo("datos.txt", ["dato"])
        existente = self.destino.crear_nuevo_archivo("previo.txt", "previo")
        self.assertTrue(self.enviar(original).entregado)
        copia = self.destino.buscar_archivo("datos.txt")
        self.assertNotEqual(existente.id, copia.id)
        self.assertNotEqual(original.id, copia.id)
        self.assertIsNot(original, copia)
        copia.contenido.append("nuevo")
        self.assertEqual(["dato"], original.contenido)
        self.assertIs(original, self.origen.buscar_archivo("datos.txt"))

    def test_subarbol_copiado_conserva_hijos_hermanos_y_ids_unicos(self) -> None:
        carpeta = self.origen.crear_subcarpeta("docs")
        hermana = self.origen.crear_subcarpeta("hermana")
        self.origen.entrar_subcarpeta("docs")
        self.origen.crear_nuevo_archivo("raiz.txt", "raiz")
        self.origen.crear_subcarpeta("hijo")
        self.origen.crear_subcarpeta("otro")
        self.origen.entrar_subcarpeta("hijo")
        self.origen.crear_nuevo_archivo("interno.txt", "interno")
        self.origen.volver_a_raiz()
        self.destino.crear_subcarpeta("existente")
        paquete = self.origen.compartir_subcarpeta(carpeta.id, "destino")
        self.assertTrue(self.origen.enviar_paquete(self.grafo, paquete).entregado)
        recibida = self.destino.obtener_carpeta_actual().buscar_subcarpeta_por_nombre("docs")
        self.assertIsNot(carpeta, recibida)
        self.assertEqual(["hijo", "otro"], [c.nombre_carpeta for c in recibida.listar_subcarpetas()])
        self.assertEqual([carpeta, hermana], self.origen.obtener_carpeta_actual().listar_subcarpetas())
        self.assertIsNone(self.destino.obtener_carpeta_actual().buscar_subcarpeta_por_nombre("hermana"))
        ids = []
        pendientes = [self.destino.gestor_archivos.raiz]
        while pendientes:
            actual = pendientes.pop()
            ids.append(actual.id)
            ids.extend(a.id for a in actual.listar_archivos())
            pendientes.extend(actual.listar_subcarpetas())
        self.assertEqual(len(ids), len(set(ids)))
        recargado = Servidor("destino", 2, self.base)
        self.assertEqual("interno", recargado.buscar_archivo("interno.txt").contenido)

    def test_nombre_duplicado_no_sobrescribe_ni_confirma_entrega(self) -> None:
        original = self.origen.crear_nuevo_archivo("datos.txt", "nuevo")
        previo = self.destino.crear_nuevo_archivo("datos.txt", "anterior")
        self.destino.guardar_estado()
        resultado = self.enviar(original)
        self.assertFalse(resultado.entregado)
        self.assertIs(previo, self.destino.buscar_archivo("datos.txt"))
        self.assertEqual("anterior", Servidor("destino", 2, self.base).buscar_archivo("datos.txt").contenido)

    def test_guardado_fallido_revierte_copia_y_conserva_csv_y_hermanos(self) -> None:
        existente = self.destino.crear_subcarpeta("existente")
        otra = self.destino.crear_subcarpeta("otra")
        self.destino.guardar_estado()
        persistencia = self.destino.persistencia.archivos
        anterior = persistencia.ruta_csv.read_bytes()
        archivos_anteriores = set(persistencia.ruta_csv.parent.iterdir())
        for contenido in ("contenido privado", self.origen.crear_subcarpeta("docs")):
            with self.subTest(tipo=type(contenido).__name__), patch.object(
                persistencia, "_PersistenciaArbolCSV__guardar_carpeta",
                side_effect=OSError("contenido privado y ClaveSecreta123"),
            ):
                resultado = self.enviar(contenido)
                self.assertFalse(resultado.entregado)
                self.assertNotIn("ClaveSecreta123", resultado.mensaje)
            self.assertEqual(anterior, persistencia.ruta_csv.read_bytes())
            self.assertEqual([existente, otra], self.destino.listar_contenido())
            self.assertEqual([existente, otra], self.destino.obtener_carpeta_actual().listar_subcarpetas())
        self.assertEqual(archivos_anteriores, set(persistencia.ruta_csv.parent.iterdir()))

    def test_auditorias_separadas_sin_duplicados_ni_contenido(self) -> None:
        self.origen.agregar_usuario("ana", "ClaveSecreta123")
        red_antes = self.grafo.consultar_auditoria()
        origen_antes = self.origen.consultar_auditoria()
        self.assertTrue(self.enviar("contenido privado").entregado)
        locales = self.origen.consultar_auditoria()[len(origen_antes):]
        red = self.grafo.consultar_auditoria()[len(red_antes):]
        destino = self.destino.consultar_auditoria()
        self.assertEqual(["ENVIAR_PAQUETE"], [r.accion for r in locales])
        self.assertEqual(["ENVIAR_PAQUETE"], [r.accion for r in red])
        self.assertEqual(["RECIBIR_PAQUETE"], [r.accion for r in destino])
        self.assertEqual("RED", red[0].origen)
        self.assertIn("origen -> destino", red[0].detalle)
        self.assertIn("20 ms", red[0].detalle)
        for auditoria in (self.grafo.auditoria, self.origen.auditoria, self.destino.auditoria):
            texto = auditoria.persistencia.ruta_csv.read_text(encoding="utf-8")
            self.assertNotIn("contenido privado", texto)
            self.assertNotIn("ClaveSecreta123", texto)

    def test_red_recargada_entrega_a_servidores_recargados(self) -> None:
        self.grafo.guardar()
        recargado = GrafoRed(self.base / "red.csv", auditoria=self.grafo.auditoria)
        recargado.cargar()
        origen = recargado.buscar_vertice("origen").servidor
        resultado = origen.enviar_paquete(recargado, origen.crear_paquete("destino", "hola"))
        self.assertTrue(resultado.entregado)
        destino = recargado.buscar_vertice("destino").servidor
        self.assertEqual("hola", destino.listar_contenido()[0].contenido)
        self.assertEqual("RECIBIR_PAQUETE", destino.consultar_auditoria()[-1].accion)


if __name__ == "__main__":
    unittest.main()
