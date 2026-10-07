import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from network_os.logic.controller.auditoria.auditoria import Auditoria
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed
from network_os.logic.controller.servidor.servidor import Servidor
from network_os.logic.model.paquete_datos.paquete_datos import PaqueteDatos
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)


class AuditoriaDescentralizadaTests(unittest.TestCase):
    def setUp(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.base = Path(temporal.name)
        self.red = Auditoria("RED", PersistenciaAuditoriaCSV(self.base / "network_audit_log.txt"))
        self.grafo = GrafoRed(self.base / "red.csv", auditoria=self.red)
        self.principal = Servidor("principal", 1, self.base)
        self.secundario = Servidor("secundario", 2, self.base)
        self.grafo.agregar_servidor(self.principal)
        self.grafo.agregar_servidor(self.secundario)

    def comprobar_evento(self, auditoria, operacion, accion, resultado, error=None):
        instancias = (self.red, self.principal.auditoria, self.secundario.auditoria)
        anteriores = {instancia: instancia.consultar_todo() for instancia in instancias}
        if error is None:
            operacion()
        else:
            with self.assertRaises(error):
                operacion()
        for instancia in instancias:
            registros = instancia.consultar_todo()
            if instancia is auditoria:
                self.assertEqual(anteriores[instancia], registros[:-1])
                self.assertEqual(len(anteriores[instancia]) + 1, len(registros))
                self.assertEqual((instancia.origen, accion, resultado),
                                 (registros[-1].origen, registros[-1].accion, registros[-1].resultado))
            else:
                self.assertEqual(anteriores[instancia], registros)
        return auditoria.consultar_ultimos(1)[0]

    def texto_logs(self):
        rutas = [self.red.persistencia.ruta_csv]
        rutas.extend(ruta for ruta in self.base.rglob("auditoria.csv"))
        return "\n".join(ruta.read_text(encoding="utf-8") for ruta in rutas if ruta.exists())

    def test_instancias_archivos_y_consultas_independientes(self) -> None:
        instancias = (self.red, self.principal.auditoria, self.secundario.auditoria)
        self.assertEqual(3, len({id(instancia) for instancia in instancias}))
        self.assertTrue(all(isinstance(instancia, Auditoria) for instancia in instancias))
        self.assertEqual(3, len({instancia.persistencia.ruta_csv for instancia in instancias}))
        self.principal.crear_subcarpeta("docs")
        self.secundario.crear_nuevo_archivo("datos.txt", "contenido privado")
        for instancia in instancias:
            self.assertEqual({instancia.origen}, {r.origen for r in instancia.consultar_todo()})
        self.assertEqual(self.red.consultar_todo(), self.grafo.consultar_auditoria())
        self.assertEqual(self.principal.auditoria.consultar_todo(), self.principal.consultar_auditoria())
        self.assertEqual(self.base / "servidores" / "principal_1" / "auditoria.csv",
                         self.principal.auditoria.persistencia.ruta_csv)
        self.assertNotIn("contenido privado", self.texto_logs())

    def test_agregar_servidor_conserva_su_auditoria_y_registros(self) -> None:
        nuevo = Servidor("nuevo", 3, self.base)
        instancia = nuevo.auditoria
        nuevo.crear_subcarpeta("antes")
        anteriores = nuevo.consultar_auditoria()
        self.comprobar_evento(self.red, lambda: self.grafo.agregar_servidor(nuevo),
                             "AGREGAR_SERVIDOR", "EXITOSO")
        self.assertIs(instancia, nuevo.auditoria)
        self.assertEqual(anteriores, nuevo.consultar_auditoria())
        red_antes = self.grafo.consultar_auditoria()
        nuevo.crear_subcarpeta("despues")
        self.assertEqual(red_antes, self.grafo.consultar_auditoria())
        self.comprobar_evento(self.red, lambda: self.grafo.agregar_servidor(nuevo),
                             "AGREGAR_SERVIDOR", "ERROR", ValueError)

    def test_append_y_consulta_despues_de_reabrir(self) -> None:
        self.principal.crear_subcarpeta("docs")
        self.secundario.crear_subcarpeta("fotos")
        for instancia in (self.red, self.principal.auditoria, self.secundario.auditoria):
            with self.subTest(origen=instancia.origen):
                ruta = instancia.persistencia.ruta_csv
                anteriores = instancia.consultar_todo()
                contenido = ruta.read_bytes()
                reabierta = Auditoria(instancia.origen, PersistenciaAuditoriaCSV(ruta))
                reabierta.registrar("PERSISTENCIA", "REABRIR", "EXITOSO", "Nueva sesion.")
                self.assertTrue(ruta.read_bytes().startswith(contenido))
                self.assertEqual(anteriores, reabierta.consultar_todo()[:-1])
                self.assertEqual("REABRIR", reabierta.consultar_ultimos(1)[0].accion)
                self.assertEqual(1, ruta.read_text().count("fecha_hora,"))

    def test_carga_preserva_logs_locales_sin_repetir_altas(self) -> None:
        self.principal.agregar_usuario("ana", "Secreto123")
        self.principal.guardar_estado()
        self.grafo.agregar_conexion("principal", "secundario", 7)
        self.grafo.guardar()
        anteriores = self.principal.consultar_auditoria()
        self.comprobar_evento(self.red, self.grafo.cargar, "CARGAR_RED", "EXITOSO")
        cargado = self.grafo.buscar_vertice("principal").servidor
        self.assertIs(self.red, self.grafo.auditoria)
        self.assertIsNot(self.red, cargado.auditoria)
        self.assertIsNot(self.principal.auditoria, cargado.auditoria)
        self.assertEqual(anteriores, cargado.consultar_auditoria())
        self.assertEqual(self.principal.auditoria.persistencia.ruta_csv, cargado.auditoria.persistencia.ruta_csv)
        red_antes = self.grafo.consultar_auditoria()
        self.assertTrue(cargado.autenticar_usuario("ana", "Secreto123"))
        self.assertEqual(red_antes, self.grafo.consultar_auditoria())
        self.assertEqual(len(anteriores) + 1, len(cargado.consultar_auditoria()))

    def test_carga_fallida_no_registra_altas_parciales(self) -> None:
        self.grafo.persistencia.ruta_conexiones_csv.write_text(
            "tipo,nombre,id,direccion_base,origen,destino,latencia_ms\n"
            f"SERVIDOR,nuevo,4,{self.base},,,\n"
            "CONEXION,,,,nuevo,fantasma,2\n", encoding="utf-8",
        )
        vertices = list(self.grafo.vertices)
        self.comprobar_evento(self.red, self.grafo.cargar, "CARGAR_RED", "ERROR", ValueError)
        self.assertEqual(vertices, self.grafo.vertices)

    def test_conexiones_y_errores_registran_una_vez(self) -> None:
        agregar = lambda: self.grafo.agregar_conexion("principal", "secundario", 5)
        self.comprobar_evento(self.red, agregar, "AGREGAR_CONEXION", "EXITOSO")
        self.comprobar_evento(self.red, agregar, "AGREGAR_CONEXION", "ERROR", ValueError)
        eliminar = lambda: self.grafo.eliminar_conexion("principal", "secundario")
        self.comprobar_evento(self.red, eliminar, "ELIMINAR_CONEXION", "EXITOSO")
        self.comprobar_evento(self.red, eliminar, "ELIMINAR_CONEXION", "ERROR", ValueError)
        self.comprobar_evento(self.red, lambda: self.grafo.agregar_conexion("principal", "secundario", -1),
                             "AGREGAR_CONEXION", "ERROR", ValueError)

    def test_rutas_y_ping_sin_duplicados_ni_entrega_ficticia(self) -> None:
        ruta = lambda: self.grafo.ruta_mas_corta("principal", "secundario")
        registro = self.comprobar_evento(self.red, ruta, "RUTA_MAS_CORTA", "FALLIDO")
        self.assertIn("No existe una ruta", registro.detalle)
        registro = self.comprobar_evento(self.red, lambda: self.grafo.ping_general("principal"),
                                        "PING_GENERAL", "EXITOSO")
        self.assertIn("secundario: inalcanzable", registro.detalle)
        self.grafo.agregar_conexion("principal", "secundario", 6)
        registro = self.comprobar_evento(self.red, ruta, "RUTA_MAS_CORTA", "EXITOSO")
        for dato in ("Origen: principal", "destino: secundario", "principal -> secundario", "6 ms"):
            self.assertIn(dato, registro.detalle)
        self.comprobar_evento(self.red, lambda: self.grafo.ping_general("fantasma"),
                             "PING_GENERAL", "ERROR", ValueError)
        self.assertFalse(any(r.accion in ("ENVIAR_PAQUETE", "RECIBIR_PAQUETE")
                             for r in self.grafo.consultar_auditoria()))

    def test_usuarios_y_accesos_sin_contrasenas_ni_duplicados(self) -> None:
        servidor = self.principal
        auditoria = servidor.auditoria
        clave = "MiClavePrivada123"
        self.comprobar_evento(auditoria, lambda: servidor.agregar_usuario("ana", clave),
                             "AGREGAR_USUARIO", "EXITOSO")
        self.comprobar_evento(auditoria, lambda: servidor.agregar_usuario("ana", clave),
                             "AGREGAR_USUARIO", "ERROR", ValueError)
        self.comprobar_evento(auditoria, lambda: servidor.agregar_usuario("bea", "corta"),
                             "AGREGAR_USUARIO", "ERROR", ValueError)
        for contrasena, resultado in ((clave, "EXITOSO"), ("OtraClave123", "FALLIDO"), ("corta", "FALLIDO")):
            self.comprobar_evento(auditoria, lambda: servidor.autenticar_usuario("ana", contrasena),
                                 "AUTENTICAR_USUARIO", resultado)
        self.comprobar_evento(auditoria, lambda: servidor.eliminar_usuario("ana"), "ELIMINAR_USUARIO", "EXITOSO")
        self.comprobar_evento(auditoria, lambda: servidor.eliminar_usuario("ana"), "ELIMINAR_USUARIO", "FALLIDO")
        for secreto in (clave, "OtraClave123", "corta"):
            self.assertNotIn(secreto, self.texto_logs())

    def test_error_de_persistencia_no_filtra_la_contrasena(self) -> None:
        clave = "SecretoEnError123"
        with patch.object(self.principal.persistencia.usuarios, "guardar", side_effect=RuntimeError(clave)):
            self.comprobar_evento(self.principal.auditoria,
                                 lambda: self.principal.agregar_usuario("ana", clave),
                                 "AGREGAR_USUARIO", "ERROR", RuntimeError)
        self.assertNotIn(clave, self.texto_logs())
        self.assertFalse(self.principal.autenticar_usuario("ana", clave))

    def test_archivos_y_carpetas_con_resultados_y_sin_contenido_privado(self) -> None:
        servidor = self.principal
        auditoria = servidor.auditoria
        self.comprobar_evento(auditoria, lambda: servidor.crear_subcarpeta("docs"), "CREAR_SUBCARPETA", "EXITOSO")
        self.comprobar_evento(auditoria, lambda: servidor.crear_subcarpeta("docs"), "CREAR_SUBCARPETA", "ERROR", ValueError)
        self.comprobar_evento(auditoria, lambda: servidor.crear_nuevo_archivo("datos.txt", "Privado123"), "CREAR_ARCHIVO", "EXITOSO")
        archivo = servidor.buscar_archivo("datos.txt")
        self.comprobar_evento(auditoria, lambda: servidor.renombrar_archivo(archivo.id, "nuevo.txt"), "RENOMBRAR_ARCHIVO", "EXITOSO")
        self.comprobar_evento(auditoria, lambda: servidor.actualizar_contenido_archivo(archivo.id, "Privado456"), "ACTUALIZAR_ARCHIVO", "EXITOSO")
        self.comprobar_evento(auditoria, lambda: servidor.cortar_archivo(archivo.id), "CORTAR_ARCHIVO", "EXITOSO")
        servidor.entrar_subcarpeta("docs")
        self.comprobar_evento(auditoria, servidor.pegar_archivo, "PEGAR_ARCHIVO", "EXITOSO")
        self.comprobar_evento(auditoria, lambda: servidor.copiar_archivo(archivo.id), "COPIAR_ARCHIVO", "EXITOSO")
        servidor.volver_a_raiz()
        self.comprobar_evento(auditoria, servidor.pegar_archivo, "PEGAR_ARCHIVO", "EXITOSO")
        servidor.entrar_subcarpeta("docs")
        self.comprobar_evento(auditoria, lambda: servidor.eliminar_archivo(archivo.id), "ELIMINAR_ARCHIVO", "EXITOSO")
        self.comprobar_evento(auditoria, lambda: servidor.eliminar_archivo(archivo.id), "ELIMINAR_ARCHIVO", "ERROR", ValueError)
        self.assertNotIn("Privado123", self.texto_logs())
        self.assertNotIn("Privado456", self.texto_logs())

    def test_preparacion_y_recepcion_en_logs_distintos(self) -> None:
        carpeta = self.principal.crear_subcarpeta("docs")
        paquete = self.principal.compartir_subcarpeta(carpeta.id, "secundario")
        self.assertIn("preparado", self.principal.auditoria.consultar_ultimos(1)[0].detalle)
        self.comprobar_evento(self.secundario.auditoria, lambda: self.secundario.recibir_paquete(paquete), "RECIBIR_PAQUETE", "EXITOSO")
        self.comprobar_evento(self.secundario.auditoria, lambda: self.secundario.recibir_paquete(paquete), "RECIBIR_PAQUETE", "ERROR", ValueError)
        incorrecto = PaqueteDatos("principal", "fantasma", "SUBCARPETA", carpeta)
        self.comprobar_evento(self.secundario.auditoria, lambda: self.secundario.recibir_paquete(incorrecto), "RECIBIR_PAQUETE", "ERROR", ValueError)

    def test_servidores_con_mismo_nombre_y_distinto_id_separan_logs(self) -> None:
        otro = Servidor("principal", 7, self.base)
        self.principal.crear_subcarpeta("original")
        otro.crear_subcarpeta("distinta")
        self.assertNotEqual(self.principal.auditoria.persistencia.ruta_csv, otro.auditoria.persistencia.ruta_csv)
        self.assertEqual({"SERVIDOR:principal (1)"}, {r.origen for r in self.principal.consultar_auditoria()})
        self.assertEqual({"SERVIDOR:principal (7)"}, {r.origen for r in otro.consultar_auditoria()})


if __name__ == "__main__":
    unittest.main()
