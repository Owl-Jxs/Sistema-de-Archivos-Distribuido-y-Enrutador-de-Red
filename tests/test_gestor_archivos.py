import io
import unittest
from contextlib import redirect_stdout
## TESTS hechos por AI para ver vulnerabilidades
from network_os.logic.controller.gestor_archivos.gestor_archivos import GestorArchivos
from network_os.logic.structure.carpeta.carpeta import Carpeta


class CarpetaTests(unittest.TestCase):
    def test_extraer_desconecta_padre_y_hermana(self) -> None:
        raiz = Carpeta(0, "raiz")
        primera = Carpeta(1, "primera")
        segunda = Carpeta(2, "segunda")
        raiz.agregar_subcarpeta(primera)
        raiz.agregar_subcarpeta(segunda)

        extraida = raiz.extraer_subcarpeta(1)

        self.assertIsNone(extraida.carpeta_padre)
        self.assertEqual([segunda], raiz.listar_contenido())

        destino = Carpeta(3, "destino")
        destino.pegar_subcarpeta(extraida)
        self.assertEqual([primera], destino.listar_contenido())
        self.assertIs(primera.carpeta_padre, destino)

    def test_impide_nombres_repetidos_y_ciclos(self) -> None:
        raiz = Carpeta(0, "raiz")
        hija = Carpeta(1, "hija")
        raiz.agregar_subcarpeta(hija)

        with self.assertRaises(ValueError):
            raiz.agregar_subcarpeta(Carpeta(2, "hija"))

        with self.assertRaises(ValueError):
            hija.agregar_subcarpeta(raiz)

    def test_impide_ids_repetidos_en_distintos_niveles(self) -> None:
        raiz = Carpeta(0, "raiz")
        hija = Carpeta(1, "hija")
        raiz.agregar_subcarpeta(hija)

        with self.assertRaises(ValueError):
            hija.agregar_subcarpeta(Carpeta(0, "id_repetido"))

    def test_renombrar_actualiza_direcciones_logicas(self) -> None:
        raiz = Carpeta(0, "raiz")
        hija = Carpeta(1, "hija")
        nieta = Carpeta(2, "nieta")
        raiz.agregar_subcarpeta(hija)
        hija.agregar_subcarpeta(nieta)

        hija.renombrar_carpeta("documentos")

        self.assertEqual("/raiz/documentos", hija.direccion_carpeta)
        self.assertEqual("/raiz/documentos/nieta", nieta.direccion_carpeta)


class GestorArchivosTests(unittest.TestCase):
    def test_crea_ids_consecutivos_y_navega(self) -> None:
        gestor = GestorArchivos("servidor")
        documentos = gestor.crear_nueva_subcarpeta("documentos")
        fotos = gestor.crear_nueva_subcarpeta("fotos")

        self.assertEqual((1, 2), (documentos.id, fotos.id))
        gestor.bajar_a_subcarpeta("documentos")
        self.assertIs(gestor.carpeta_actual, documentos)
        gestor.subir_nivel()
        self.assertIs(gestor.carpeta_actual, gestor.raiz)

    def test_corta_y_pega_una_subcarpeta(self) -> None:
        gestor = GestorArchivos("servidor")
        origen = gestor.crear_nueva_subcarpeta("origen")
        destino = gestor.crear_nueva_subcarpeta("destino")
        gestor.bajar_a_subcarpeta("origen")
        movida = gestor.crear_nueva_subcarpeta("movida")
        gestor.extraer_subcarpeta(movida.id)

        gestor.volver_a_raiz()
        gestor.bajar_a_subcarpeta("destino")
        gestor.pegar_subcarpeta()

        self.assertEqual([], origen.listar_contenido())
        self.assertEqual([movida], destino.listar_contenido())
        self.assertIs(movida.carpeta_padre, destino)

    def test_copia_arbol_y_conserva_ids_unicos(self) -> None:
        gestor = GestorArchivos("servidor")
        original = gestor.crear_nueva_subcarpeta("original")
        destino = gestor.crear_nueva_subcarpeta("destino")
        gestor.bajar_a_subcarpeta("original")
        hija = gestor.crear_nueva_subcarpeta("hija")
        gestor.volver_a_raiz()

        gestor.copiar_subcarpeta(original.id)
        gestor.bajar_a_subcarpeta("destino")
        gestor.pegar_subcarpeta()

        copia = destino.buscar_subcarpeta_por_nombre("original")
        self.assertIsNotNone(copia)
        assert copia is not None
        copia_hija = copia.buscar_subcarpeta_por_nombre("hija")
        self.assertIsNotNone(copia_hija)
        assert copia_hija is not None
        self.assertEqual((4, 5), (copia.id, copia_hija.id))
        self.assertNotEqual(original.id, copia.id)
        self.assertNotEqual(hija.id, copia_hija.id)

    def test_elimina_subarbol(self) -> None:
        gestor = GestorArchivos("servidor")
        eliminada = gestor.crear_nueva_subcarpeta("eliminada")
        gestor.bajar_a_subcarpeta("eliminada")
        hija = gestor.crear_nueva_subcarpeta("hija")
        gestor.volver_a_raiz()

        gestor.eliminar_subcarpeta(eliminada.id)

        self.assertEqual([], gestor.raiz.listar_contenido())
        self.assertEqual([], eliminada.listar_contenido())
        self.assertIsNone(hija.carpeta_padre)

    def test_pegar_sin_portapapeles_falla(self) -> None:
        gestor = GestorArchivos("servidor")

        with self.assertRaises(ValueError):
            gestor.pegar_subcarpeta()

    def test_operacion_invalida_no_descarta_el_corte_pendiente(self) -> None:
        gestor = GestorArchivos("servidor")
        movida = gestor.crear_nueva_subcarpeta("movida")
        destino = gestor.crear_nueva_subcarpeta("destino")
        gestor.extraer_subcarpeta(movida.id)

        with self.assertRaises(ValueError):
            gestor.copiar_subcarpeta(999)

        gestor.bajar_a_subcarpeta(destino.nombre_carpeta)
        gestor.pegar_subcarpeta()
        self.assertEqual([movida], destino.listar_contenido())

    def test_nueva_operacion_restaura_un_corte_pendiente(self) -> None:
        gestor = GestorArchivos("servidor")
        cortada = gestor.crear_nueva_subcarpeta("cortada")
        copiada = gestor.crear_nueva_subcarpeta("copiada")
        gestor.extraer_subcarpeta(cortada.id)

        gestor.copiar_subcarpeta(copiada.id)

        self.assertIs(
            gestor.raiz.buscar_subcarpeta_por_nombre("cortada"), cortada
        )

    def test_busca_archivo_recursivo_en_todo_el_arbol(self) -> None:
        gestor = GestorArchivos("servidor")
        gestor.crear_nuevo_archivo("raiz.txt")
        gestor.crear_nueva_subcarpeta("documentos")
        gestor.bajar_a_subcarpeta("documentos")
        gestor.crear_nuevo_archivo("tarea.txt")
        gestor.crear_nueva_subcarpeta("internos")
        gestor.bajar_a_subcarpeta("internos")
        oculto = gestor.crear_nuevo_archivo("profundo.txt")
        gestor.volver_a_raiz()

        encontrado = gestor.buscar_archivo("profundo.txt")

        self.assertIsNotNone(encontrado)
        assert encontrado is not None
        self.assertEqual(oculto.id, encontrado.id)
        self.assertEqual(
            "tarea.txt",
            gestor.buscar_archivo("tarea.txt").nombre,  # type: ignore[union-attr]
        )
        self.assertIsNone(gestor.buscar_archivo("no_existe.txt"))

    def test_mostrar_arbol_imprime_con_indentacion(self) -> None:
        gestor = GestorArchivos("servidor")
        gestor.crear_nuevo_archivo("usuarios.csv")
        documentos = gestor.crear_nueva_subcarpeta("documentos")
        gestor.bajar_a_subcarpeta("documentos")
        gestor.crear_nuevo_archivo("tarea.txt")
        gestor.volver_a_raiz()

        salida = io.StringIO()
        with redirect_stdout(salida):
            gestor.mostrar_arbol()

        lineas = salida.getvalue().splitlines()
        self.assertEqual(
            [
                "servidor/",
                "    usuarios.csv",
                "    documentos/",
                "        tarea.txt",
            ],
            lineas,
        )

    def test_lineas_arbol_incluye_subcarpetas_anidadas(self) -> None:
        raiz = Carpeta(0, "raiz")
        hija = Carpeta(1, "hija")
        nieta = Carpeta(2, "nieta")
        raiz.agregar_subcarpeta(hija)
        hija.agregar_subcarpeta(nieta)

        self.assertEqual(
            ["raiz/", "    hija/", "        nieta/"],
            raiz.lineas_arbol(),
        )


class ImpresionArbolTests(unittest.TestCase):
    def test_repositorio_vacio_muestra_solo_la_raiz(self) -> None:
        gestor = GestorArchivos("raiz")
        self.assertEqual(["raiz"], gestor.raiz.lineas_estructura())
        salida = io.StringIO()
        with redirect_stdout(salida):
            self.assertIsNone(gestor.imprimir_arbol())
        self.assertEqual("raiz\n", salida.getvalue())

    def test_archivos_sin_subcarpetas(self) -> None:
        gestor = GestorArchivos("raiz")
        gestor.crear_nuevo_archivo("uno.txt")
        gestor.crear_nuevo_archivo("dos.txt")
        self.assertEqual(["raiz", "|", "|-- uno.txt", "|-- dos.txt"],
                         gestor.raiz.lineas_estructura())

    def test_hermanas_vacias_con_primer_hijo_y_siguiente_hermana(self) -> None:
        segunda = Carpeta(2, "segunda")
        primera = Carpeta(1, "primera", siguiente_subcarpeta=segunda)
        raiz = Carpeta(0, "raiz", primer_subcarpeta=primera)
        self.assertEqual(["raiz", "|", "|-- primera", "|-- segunda"],
                         raiz.lineas_estructura())
        self.assertEqual(["primera"], primera.lineas_estructura())
        self.assertEqual([primera, segunda], raiz.listar_subcarpetas())

    def test_niveles_archivos_y_hermanas_sin_modificar_el_arbol(self) -> None:
        gestor = GestorArchivos("raiz")
        juegos = gestor.crear_nueva_subcarpeta("juegos")
        documentos = gestor.crear_nueva_subcarpeta("documentos")
        readme = gestor.crear_nuevo_archivo("Readme.txt", "contenido")
        gestor.bajar_a_subcarpeta("juegos")
        lol = gestor.crear_nueva_subcarpeta("LoL")
        minecraft = gestor.crear_nueva_subcarpeta("Minecraft")
        gestor.bajar_a_subcarpeta("Minecraft")
        config = gestor.crear_nuevo_archivo("config.txt")
        gestor.volver_a_raiz()
        gestor.bajar_a_subcarpeta("documentos")
        tarea = gestor.crear_nuevo_archivo("tarea.pdf")

        carpetas = (gestor.raiz, juegos, documentos, lol, minecraft)
        def estado_arbol():
            return [
                (carpeta.id, carpeta.nombre_carpeta, carpeta.direccion_carpeta,
                 carpeta.carpeta_padre, tuple(carpeta.listar_subcarpetas()),
                 tuple(carpeta.listar_archivos()))
                for carpeta in carpetas
            ]

        estado_anterior = estado_arbol()
        archivos_antes = [vars(archivo).copy() for archivo in (readme, config, tarea)]
        esperadas = [
            "raiz", "|", "|-- juegos", "|   |", "|   |-- LoL",
            "|   |-- Minecraft", "|       |", "|       |-- config.txt",
            "|-- documentos", "|   |", "|   |-- tarea.pdf", "|-- Readme.txt",
        ]
        salida = io.StringIO()
        with redirect_stdout(salida):
            self.assertEqual(esperadas, gestor.raiz.lineas_estructura())
        self.assertEqual("", salida.getvalue())
        with redirect_stdout(salida):
            gestor.imprimir_arbol()
        self.assertEqual(esperadas, salida.getvalue().splitlines())
        self.assertIs(documentos, gestor.carpeta_actual)
        self.assertEqual(estado_anterior, estado_arbol())
        self.assertEqual(archivos_antes,
                         [vars(archivo).copy() for archivo in (readme, config, tarea)])


if __name__ == "__main__":
    unittest.main()
