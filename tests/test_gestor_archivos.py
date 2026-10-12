import io
import unittest
from contextlib import redirect_stdout
## TESTS hechos por AI para ver vulnerabilidades
from network_os.logic.controller.gestor_archivos.gestor_archivos import GestorArchivos
from network_os.logic.structure.carpeta.carpeta import Carpeta


class CarpetaTests(unittest.TestCase):
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

    def test_cascada_libre_3_niveles(self) -> None:
        # La rubrica prohibe dejar nodos huerfanos: tras eliminar la carpeta
        # ninguna referencia del subarbol debe seguir enlazada al arbol.
        gestor = GestorArchivos("servidor")
        eliminada = gestor.crear_nueva_subcarpeta("eliminada")
        hermana = gestor.crear_nueva_subcarpeta("hermana")

        gestor.bajar_a_subcarpeta("eliminada")
        nivel2 = gestor.crear_nueva_subcarpeta("nivel2")
        gestor.crear_nuevo_archivo("a.txt", "contenido")
        gestor.bajar_a_subcarpeta("nivel2")
        nivel3 = gestor.crear_nueva_subcarpeta("nivel3")
        gestor.crear_nuevo_archivo("b.txt", "contenido")
        gestor.volver_a_raiz()

        gestor.eliminar_subcarpeta(eliminada.id)

        self.assertEqual([hermana], gestor.raiz.listar_subcarpetas())
        self.assertIs(hermana.carpeta_padre, gestor.raiz)

        for carpeta in (eliminada, nivel2, nivel3):
            self.assertIsNone(carpeta.carpeta_padre)
            self.assertEqual([], carpeta.listar_subcarpetas())
            self.assertEqual([], carpeta.listar_archivos())

        # La carpeta eliminada ya no se encuentra desde la raiz.
        self.assertIsNone(gestor.buscar_archivo("a.txt"))
        self.assertIsNone(gestor.buscar_archivo("b.txt"))

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
