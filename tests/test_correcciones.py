"""Verificacion de las cinco fases de correccion (incluye humo del menu)."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from network_os.consola.principal.menu_consola import MenuConsola
from network_os.consola.servidor.menu_archivos import MenuArchivos
from network_os.logic.controller.auditoria.auditoria import Auditoria
from network_os.logic.controller.gestor_archivos.gestor_archivos import GestorArchivos
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed
from network_os.logic.controller.servidor.servidor import Servidor
from network_os.logic.model.archivo.archivo import Archivo
from network_os.logic.model.fecha_hora import fecha_hora_actual_costa_rica
from network_os.logic.model.registro_auditoria.registro_auditoria import (
    RegistroAuditoria,
)
from network_os.logic.structure.carpeta.carpeta import Carpeta
from network_os.main import NetworkOS
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import (
    PersistenciaAuditoriaCSV,
)
from network_os.persistencia.persistencia_carpetas.persistencia_arbol_csv import (
    PersistenciaArbolCSV,
)


class PortapapelesTests(unittest.TestCase):
    """Fase 1: el corte pendiente no se pierde al guardar."""

    def setUp(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.ruta_csv = Path(temporal.name) / "archivos.csv"

    def test_guardar_incluye_el_corte_pendiente_antes_de_escribir_el_csv(self) -> None:
        gestor = GestorArchivos("servidor", PersistenciaArbolCSV(self.ruta_csv))
        gestor.crear_nueva_subcarpeta("origen")
        gestor.bajar_a_subcarpeta("origen")
        movida = gestor.crear_nueva_subcarpeta("movida")
        gestor.extraer_subcarpeta(movida.id)
        gestor.volver_a_raiz()

        gestor.guardar_todo()

        recargado = GestorArchivos("servidor", PersistenciaArbolCSV(self.ruta_csv))
        recargado.cargar_servidor()
        recargado.bajar_a_subcarpeta("origen")
        restaurada = recargado.carpeta_actual.buscar_subcarpeta_por_nombre("movida")
        self.assertIsNotNone(restaurada)
        assert restaurada is not None
        self.assertEqual("origen", restaurada.carpeta_padre.nombre_carpeta)
        # El corte quedo resuelto: recargar no deja nada que pegar.
        with self.assertRaises(ValueError):
            recargado.pegar_subcarpeta()

    def test_guardar_con_nombre_duplicado_lanza_error_y_conserva_el_corte(self) -> None:
        gestor = GestorArchivos("servidor", PersistenciaArbolCSV(self.ruta_csv))
        gestor.crear_nueva_subcarpeta("movida")
        destino = gestor.crear_nueva_subcarpeta("destino")
        cortada = gestor.raiz.buscar_subcarpeta_por_nombre("movida")
        assert cortada is not None
        gestor.extraer_subcarpeta(cortada.id)
        gestor.crear_nueva_subcarpeta("movida")  # nombre repetido en el origen

        with self.assertRaises(ValueError):
            gestor.guardar_todo()

        gestor.bajar_a_subcarpeta("destino")
        gestor.pegar_subcarpeta()
        pegada = destino.buscar_subcarpeta_por_nombre("movida")
        self.assertIs(cortada, pegada)  # ni renombrada con sufijo ni descartada
        self.assertIsNone(destino.buscar_subcarpeta_por_nombre("movida_1"))

    def test_pegar_con_nombre_duplicado_lanza_error_y_deja_el_corte(self) -> None:
        gestor = GestorArchivos("servidor")
        origen = gestor.crear_nueva_subcarpeta("origen")
        destino = gestor.crear_nueva_subcarpeta("destino")
        gestor.bajar_a_subcarpeta("origen")
        movida = gestor.crear_nueva_subcarpeta("movida")
        gestor.extraer_subcarpeta(movida.id)
        gestor.volver_a_raiz()
        gestor.bajar_a_subcarpeta("destino")
        gestor.crear_nueva_subcarpeta("movida")  # nombre repetido en el destino

        with self.assertRaises(ValueError):
            gestor.pegar_subcarpeta()

        # El corte sigue atrapado y sin sufijo: se puede pegar despues.
        gestor.volver_a_raiz()
        gestor.bajar_a_subcarpeta("origen")
        gestor.pegar_subcarpeta()
        self.assertIs(movida, origen.buscar_subcarpeta_por_nombre("movida"))
        self.assertIsNone(destino.buscar_subcarpeta_por_nombre("movida_1"))


class PersistenciaTests(unittest.TestCase):
    """Fase 2: contenido en JSON, directorios limpios y arranque tolerante."""

    def test_contenido_serializado_con_json_y_texto_legado_se_lee(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "archivos.csv"
            persistencia = PersistenciaArbolCSV(ruta)
            raiz = Carpeta(0, "raiz")
            raiz.agregar_archivo(Archivo(1, "datos.txt", {"clave": [1, 2]}))
            raiz.agregar_archivo(Archivo(2, "numero.txt", 42))
            raiz.agregar_archivo(Archivo(3, "texto.txt", "hola, mundo"))

            persistencia.guardar(raiz)
            cargada = persistencia.cargar()

            self.assertEqual(
                {"clave": [1, 2]}, cargada.buscar_archivo_por_id(1).contenido
            )
            self.assertEqual(42, cargada.buscar_archivo_por_id(2).contenido)
            self.assertEqual("hola, mundo", cargada.buscar_archivo_por_id(3).contenido)

            ruta.write_text(
                "tipo,id,nombre,id_padre,contenido,ultima_modificacion\n"
                "CARPETA,0,raiz,,,\n"
                "ARCHIVO,1,viejo.txt,0,contenido viejo,2026-01-01T00:00:00\n",
                encoding="utf-8",
            )
            legada = persistencia.cargar()
            self.assertEqual(
                "contenido viejo", legada.buscar_archivo_por_id(1).contenido
            )

    def test_eliminar_servidor_borra_su_directorio(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            base = Path(temporal)
            grafo = GrafoRed(
                base / "red.csv",
                auditoria=Auditoria(
                    "RED", PersistenciaAuditoriaCSV(base / "network_audit_log.txt")
                ),
            )
            grafo.agregar_servidor(Servidor("principal", 1, base))
            secundario = Servidor("secundario", 2, base)
            grafo.agregar_servidor(secundario)
            secundario.agregar_usuario("ana", "Clave1234")
            secundario.crear_subcarpeta("docs")
            directorio = secundario.persistencia.directorio

            grafo.eliminar_servidor("secundario")

            self.assertFalse(directorio.exists())
            recreado = Servidor("secundario", 2, base)
            self.assertTrue(recreado.usuarios_vacios())
            self.assertEqual([], recreado.listar_contenido())

    def test_arranque_tolerante_a_un_csv_de_red_corrupto(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        anterior = Path.cwd()
        os.chdir(temporal.name)
        # El orden importa: se vuelve al directorio original antes de borrar.
        self.addCleanup(os.chdir, anterior)
        datos = Path("datos")
        datos.mkdir()
        (datos / "red_conexiones.csv").write_text(
            "basura\nsin formato\n", encoding="utf-8"
        )
        salida = io.StringIO()

        with patch.object(MenuConsola, "ejecutar") as ejecutar, redirect_stdout(
            salida
        ):
            NetworkOS.ejecutar_menu()

        ejecutar.assert_called_once()
        self.assertIn("se inicia una red vacia", salida.getvalue())


class IdentidadTests(unittest.TestCase):
    """Fase 3: enviar_paquete no depende de la identidad del objeto."""

    def test_enviar_con_la_instancia_previa_a_la_recarga_y_rechaza_al_homonimo(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        base = Path(temporal.name)
        grafo = GrafoRed(
            base / "red.csv",
            auditoria=Auditoria("RED", PersistenciaAuditoriaCSV(base / "red_log.txt")),
        )
        origen = Servidor("origen", 1, base)
        destino = Servidor("destino", 2, base)
        for servidor in (origen, destino):
            grafo.agregar_servidor(servidor)
        grafo.agregar_conexion("origen", "destino", 5)
        grafo.guardar()

        grafo.cargar()  # los vertices pasan a guardar otras instancias

        resultado = origen.enviar_paquete(
            grafo, origen.crear_paquete("destino", "hola")
        )
        self.assertTrue(resultado.entregado)
        recibido = grafo.buscar_vertice("destino").servidor.listar_contenido()
        self.assertEqual("hola", recibido[0].contenido)

        homonimo = Servidor("origen", 9, base)
        with self.assertRaises(ValueError):
            homonimo.enviar_paquete(
                grafo, homonimo.crear_paquete("destino", "hola")
            )


def recorrer(operacion, entradas) -> str:
    """Ejecuta una operacion de menu con un guion de entradas pregrabado."""
    salida = io.StringIO()
    pendientes = list(entradas)

    def input_mock(mensaje: str = "") -> str:
        if not pendientes:
            raise AssertionError("El guion de entradas termino antes que el menu.")
        return pendientes.pop(0)

    with patch("builtins.input", side_effect=input_mock), redirect_stdout(salida):
        operacion()

    if pendientes:
        raise AssertionError(f"Entradas del guion sin usar: {pendientes}")
    return salida.getvalue()


class CompartirConsolaTests(unittest.TestCase):
    """Fase 4: compartir archivo o carpeta desde MenuArchivos."""

    def setUp(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        base = Path(temporal.name)
        auditoria = Auditoria(
            "RED", PersistenciaAuditoriaCSV(base / "network_audit_log.txt")
        )
        self.grafo = GrafoRed(base / "red.csv", auditoria=auditoria)
        self.origen = Servidor("origen", 1, base)
        self.destino = Servidor("destino", 2, base)
        for servidor in (self.origen, self.destino):
            self.grafo.agregar_servidor(servidor)
        self.grafo.agregar_conexion("origen", "destino", 5)
        self.menu = MenuArchivos(self.origen, self.grafo)

    def test_compartir_carpeta_y_archivo_llegan_al_otro_servidor(self) -> None:
        carpeta = self.origen.crear_subcarpeta("docs")
        archivo = self.origen.crear_nuevo_archivo("datos.txt", ["dato"])

        salida = recorrer(
            self.menu.menu_archivos,
            ["8", "2", str(carpeta.id), "destino", "", "0"],
        )
        self.assertIn("Paquete entregado.", salida)
        recibida = self.destino.obtener_carpeta_actual().buscar_subcarpeta_por_nombre(
            "docs"
        )
        self.assertIsNotNone(recibida)

        salida = recorrer(
            self.menu.menu_archivos,
            ["8", "1", str(archivo.id), "destino", "", "0"],
        )
        self.assertIn("Paquete entregado.", salida)
        copia = self.destino.buscar_archivo("datos.txt")
        self.assertIsNotNone(copia)
        assert copia is not None
        self.assertEqual(["dato"], copia.contenido)
        self.assertIsNot(archivo, copia)

        # El origen no se vacia y el portapapeles queda intacto.
        self.assertIsNotNone(
            self.origen.obtener_carpeta_actual().buscar_subcarpeta_por_nombre("docs")
        )
        self.assertEqual(["dato"], self.origen.buscar_archivo("datos.txt").contenido)
        self.assertEqual(
            1,
            sum(
                r.accion == "COMPARTIR_SUBCARPETA"
                for r in self.origen.consultar_auditoria()
            ),
        )
        self.assertEqual(
            1,
            sum(
                r.accion == "COMPARTIR_ARCHIVO"
                for r in self.origen.consultar_auditoria()
            ),
        )

    def test_destino_inexistente_y_menu_sin_red_no_envian_nada(self) -> None:
        carpeta = self.origen.crear_subcarpeta("docs")

        salida = recorrer(
            self.menu.menu_archivos,
            ["8", "2", str(carpeta.id), "fantasma", "", "0"],
        )
        self.assertIn("No se pudo completar la operacion", salida)
        self.assertIn("No existe un servidor llamado fantasma", salida)
        self.assertEqual(
            [], self.destino.obtener_carpeta_actual().listar_subcarpetas()
        )

        sin_red = MenuArchivos(self.origen)
        salida = recorrer(sin_red.menu_archivos, ["8", "", "0"])
        self.assertIn("no tiene la red configurada", salida)
        self.assertEqual(
            [], self.destino.obtener_carpeta_actual().listar_subcarpetas()
        )


class HumoMenuCompletoTests(unittest.TestCase):
    """Humo: recorrido completo de los menus con mocks en un directorio temporal."""

    def setUp(self) -> None:
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.base = Path(temporal.name)
        self.grafo = GrafoRed(
            self.base / "red.csv",
            auditoria=Auditoria(
                "RED",
                PersistenciaAuditoriaCSV(self.base / "network_audit_log.txt"),
            ),
        )
        self.principal = Servidor("principal", 1, self.base)
        self.secundario = Servidor("secundario", 2, self.base)
        for servidor in (self.principal, self.secundario):
            self.grafo.agregar_servidor(servidor)
        self.principal.agregar_usuario("ana", "Clave1234")
        self.menu = MenuConsola(self.grafo)

    def test_recorrido_completo_incluye_la_opcion_de_compartir(self) -> None:
        guion = [
            "1",  # menu principal -> red
            "1", "",  # listar servidores y conexiones
            "3", "1", "principal", "secundario", "",  # agregar conexion
            "5", "principal", "",  # ping general
            "0",  # volver
            "2", "principal", "ana",  # iniciar sesion (getpass mockeado)
            "1",  # archivos y carpetas
            "3", "docs", "",  # crear carpeta
            "4", "nota.txt", "contenido de nota", "",  # crear archivo
            "1", "",  # listar contenido
            "8", "2", "1", "secundario", "",  # compartir la carpeta docs
            "5", "nota.txt", "",  # buscar archivo
            "6", "",  # imprimir arbol
            "0",  # volver al menu del servidor
            "2", "1", "bea", "0",  # usuarios locales: registrar bea
            "3", "secundario", "hola", "",  # enviar paquete de texto
            "4", "1", "", "0",  # auditoria local
            "0",  # cerrar sesion
            "3", "1", "", "0",  # auditoria de la red
            "0",  # salir
        ]

        with patch(
            "network_os.consola.principal.menu_consola.getpass",
            return_value="Clave1234",
        ), patch(
            "network_os.consola.servidor.usuarios_locales.getpass",
            return_value="OtraClave123",
        ):
            salida = recorrer(self.menu.ejecutar, guion)

        self.assertEqual(2, salida.count("Paquete entregado."))
        self.assertIn("Sesion cerrada.", salida)
        self.assertIn("creada con ID 1", salida)
        self.assertIn("Archivo encontrado: nota.txt", salida)
        self.assertIn("Todos los servidores estan comunicados", salida)
        self.assertIn("Usuario 'bea' registrado", salida)
        self.assertNotIn("Clave1234", salida)
        self.assertNotIn("contenido de nota", salida)

        # El contenido compartido y el paquete de texto llegaron al destino.
        recibida = self.secundario.obtener_carpeta_actual().buscar_subcarpeta_por_nombre(
            "docs"
        )
        self.assertIsNotNone(recibida)
        mensajes = [
            archivo
            for archivo in self.secundario.listar_contenido()
            if getattr(archivo, "nombre", "").startswith("mensaje_")
        ]
        self.assertEqual(1, len(mensajes))
        self.assertEqual("hola", mensajes[0].contenido)
        self.assertEqual(
            2,
            sum(
                r.accion == "ENVIAR_PAQUETE"
                for r in self.grafo.consultar_auditoria()
            ),
        )
        self.assertEqual(
            1,
            sum(
                r.accion == "COMPARTIR_SUBCARPETA"
                for r in self.principal.consultar_auditoria()
            ),
        )
        # El estado quedo persistido: otro arranque del servidor lo ve.
        recargado = Servidor("principal", 1, self.base)
        self.assertIsNotNone(recargado.buscar_archivo("nota.txt"))
        self.assertTrue(recargado.autenticar_usuario("ana", "Clave1234"))


class HigieneTests(unittest.TestCase):
    """Fase 5: el log cachea la validacion de su encabezado."""

    def test_validacion_cacheada_por_instancia_y_al_validar_en_otra(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "auditoria.csv"
            persistencia = PersistenciaAuditoriaCSV(ruta)
            registro = RegistroAuditoria(
                fecha_hora=fecha_hora_actual_costa_rica(),
                categoria="ARCHIVOS",
                accion="CREAR_ARCHIVO",
                resultado="EXITOSO",
                detalle="Archivo tarea.",
            )
            persistencia.agregar(registro)

            # Otra proceso corrompe el encabezado: la instancia que ya
            # valido no vuelve a leerlo y sigue agregando.
            ruta.write_text("rotura,invalida\n", encoding="utf-8")
            persistencia.agregar(registro)

            # Una instancia nueva si valida y rechaza el archivo.
            with self.assertRaises(ValueError):
                PersistenciaAuditoriaCSV(ruta).agregar(registro)


if __name__ == "__main__":
    unittest.main()
