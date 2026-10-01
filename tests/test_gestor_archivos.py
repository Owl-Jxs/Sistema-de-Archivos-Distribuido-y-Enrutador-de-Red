import unittest
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


if __name__ == "__main__":
    unittest.main()
