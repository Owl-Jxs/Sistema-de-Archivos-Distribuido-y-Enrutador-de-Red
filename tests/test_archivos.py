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
    def test_agrega_busca_lista_renombra_y_elimina_archivos(self) -> None:
        carpeta = Carpeta(0, "raiz")
        archivo = Archivo(1, "notas.txt", "hola")

        carpeta.agregar_archivo(archivo)
        carpeta.renombrar_archivo(archivo.id, "tareas.txt")

        self.assertEqual([archivo], carpeta.listar_archivos())
        self.assertIs(carpeta.buscar_archivo_por_nombre("tareas.txt"), archivo)
        self.assertIs(carpeta.buscar_archivo_por_id(archivo.id), archivo)
        self.assertIs(carpeta.eliminar_archivo(archivo.id), archivo)
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


if __name__ == "__main__":
    unittest.main()
