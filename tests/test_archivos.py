import unittest

from network_os.logic.controller.gestor_archivos.gestor_archivos import GestorArchivos
from network_os.logic.model.archivo.archivo import Archivo
from network_os.logic.structure.carpeta.carpeta import Carpeta


class ArchivoTests(unittest.TestCase):
    def test_renombrar_y_actualizar_contenido_modifican_la_fecha(self) -> None:
        archivo = Archivo(1, "original.txt", "contenido")
        fecha_inicial = archivo.ultima_modificacion

        archivo.renombrar("nuevo.txt")
        archivo.actualizar_contenido("actualizado")

        self.assertEqual("nuevo.txt", archivo.nombre)
        self.assertEqual("actualizado", archivo.contenido)
        self.assertGreaterEqual(archivo.ultima_modificacion, fecha_inicial)

    def test_clonar_crea_contenido_independiente(self) -> None:
        archivo = Archivo(1, "datos.txt", ["original"])

        copia = archivo.clonar(2)
        copia.contenido.append("copia")

        self.assertEqual(2, copia.id)
        self.assertEqual(["original"], archivo.contenido)
        self.assertEqual(["original", "copia"], copia.contenido)


class ArchivosEnCarpetaTests(unittest.TestCase):
    def test_agrega_busca_lista_renombra_y_extrae_archivos(self) -> None:
        carpeta = Carpeta(0, "raiz")
        archivo = Archivo(1, "notas.txt", "hola")

        carpeta.agregar_archivo(archivo)
        carpeta.renombrar_archivo(archivo.id, "tareas.txt")

        self.assertEqual([archivo], carpeta.listar_archivos())
        self.assertIs(carpeta.buscar_archivo_por_nombre("tareas.txt"), archivo)
        self.assertIs(carpeta.buscar_archivo_por_id(archivo.id), archivo)
        self.assertIs(carpeta.extraer_archivo(archivo.id), archivo)
        self.assertEqual([], carpeta.listar_archivos())

    def test_impide_nombres_repetidos_entre_archivos_y_carpetas(self) -> None:
        carpeta = Carpeta(0, "raiz")
        carpeta.agregar_archivo(Archivo(1, "documentos"))

        with self.assertRaises(ValueError):
            carpeta.agregar_subcarpeta(Carpeta(2, "documentos"))

    def test_impide_ids_repetidos_en_todo_el_arbol(self) -> None:
        raiz = Carpeta(0, "raiz")
        hija = Carpeta(1, "hija")
        raiz.agregar_subcarpeta(hija)

        with self.assertRaises(ValueError):
            hija.agregar_archivo(Archivo(0, "repetido.txt"))


class ArchivosEnGestorTests(unittest.TestCase):
    def test_carpetas_y_archivos_comparten_la_secuencia_de_ids(self) -> None:
        gestor = GestorArchivos("servidor")
        carpeta = gestor.crear_nueva_subcarpeta("documentos")
        archivo = gestor.crear_nuevo_archivo("notas.txt")

        self.assertEqual((1, 2), (carpeta.id, archivo.id))

    def test_corta_y_pega_archivo_entre_carpetas(self) -> None:
        gestor = GestorArchivos("servidor")
        origen = gestor.crear_nueva_subcarpeta("origen")
        destino = gestor.crear_nueva_subcarpeta("destino")
        gestor.bajar_a_subcarpeta("origen")
        archivo = gestor.crear_nuevo_archivo("datos.txt", "contenido")

        gestor.cortar_archivo(archivo.id)
        gestor.volver_a_raiz()
        gestor.bajar_a_subcarpeta("destino")
        gestor.pegar_archivo()

        self.assertEqual([], origen.listar_archivos())
        self.assertEqual([archivo], destino.listar_archivos())

    def test_copiar_archivo_asigna_id_y_contenido_independientes(self) -> None:
        gestor = GestorArchivos("servidor")
        destino = gestor.crear_nueva_subcarpeta("destino")
        original = gestor.crear_nuevo_archivo("datos.txt", ["original"])

        gestor.copiar_archivo(original.id)
        gestor.bajar_a_subcarpeta("destino")
        gestor.pegar_archivo()

        copia = destino.buscar_archivo_por_nombre("datos.txt")
        self.assertIsNotNone(copia)
        assert copia is not None
        self.assertEqual(3, copia.id)
        copia.contenido.append("copia")
        self.assertEqual(["original"], original.contenido)

    def test_copiar_carpeta_incluye_sus_archivos(self) -> None:
        gestor = GestorArchivos("servidor")
        original = gestor.crear_nueva_subcarpeta("original")
        destino = gestor.crear_nueva_subcarpeta("destino")
        gestor.bajar_a_subcarpeta("original")
        gestor.crear_nuevo_archivo("contenido.txt", "datos")
        gestor.volver_a_raiz()

        gestor.copiar_subcarpeta(original.id)
        gestor.bajar_a_subcarpeta("destino")
        gestor.pegar_subcarpeta()

        copia = destino.buscar_subcarpeta_por_nombre("original")
        self.assertIsNotNone(copia)
        assert copia is not None
        self.assertEqual(4, copia.id)
        self.assertEqual(5, copia.listar_archivos()[0].id)
        self.assertEqual("contenido.txt", copia.listar_archivos()[0].nombre)

    def test_no_pega_un_archivo_con_el_metodo_de_subcarpetas(self) -> None:
        gestor = GestorArchivos("servidor")
        destino = gestor.crear_nueva_subcarpeta("destino")
        archivo = gestor.crear_nuevo_archivo("datos.txt")
        gestor.copiar_archivo(archivo.id)
        gestor.bajar_a_subcarpeta("destino")

        with self.assertRaises(ValueError):
            gestor.pegar_subcarpeta()

        gestor.pegar_archivo()
        self.assertEqual(1, len(destino.listar_archivos()))


if __name__ == "__main__":
    unittest.main()
