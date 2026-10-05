import unittest

from network_os.logic.structure.hash_table.hash_map import HashMap


class ClaveConColision:
    def __init__(self, identificador: int) -> None:
        self.identificador = identificador

    def __hash__(self) -> int:
        return 42

    def __eq__(self, otra: object) -> bool:
        return (
            isinstance(otra, ClaveConColision)
            and self.identificador == otra.identificador
        )


class HashMapTests(unittest.TestCase):
    def test_rechaza_capacidades_invalidas(self) -> None:
        for capacidad in (0, -1, 1.5, True):
            with self.subTest(capacidad=capacidad):
                with self.assertRaises(ValueError):
                    HashMap(capacidad)

    def test_inserta_obtiene_y_actualiza_sin_duplicar(self) -> None:
        tabla = HashMap()
        tabla.insertar("usuario", "clave-inicial")
        tabla.insertar("usuario", "clave-nueva")

        self.assertEqual("clave-nueva", tabla.obtener("usuario"))
        self.assertEqual(1, tabla.tamano())
        self.assertTrue(tabla.contiene("usuario"))

    def test_resuelve_colisiones_con_lista_enlazada(self) -> None:
        tabla = HashMap(8)
        primera = ClaveConColision(1)
        segunda = ClaveConColision(2)
        tabla.insertar(primera, "uno")
        tabla.insertar(segunda, "dos")

        self.assertEqual("uno", tabla.obtener(primera))
        self.assertEqual("dos", tabla.obtener(segunda))
        self.assertTrue(tabla.eliminar(primera))
        self.assertEqual("dos", tabla.obtener(segunda))

    def test_claves_equivalentes_recuperan_el_mismo_valor(self) -> None:
        tabla = HashMap()
        insertada = ClaveConColision(7)
        equivalente = ClaveConColision(7)

        tabla.insertar(insertada, "valor")

        self.assertEqual("valor", tabla.obtener(equivalente))
        self.assertTrue(tabla.contiene(equivalente))

    def test_redimensiona_y_conserva_los_datos(self) -> None:
        tabla = HashMap(2)

        for numero in range(20):
            tabla.insertar(f"clave-{numero}", numero)

        self.assertGreater(tabla.capacidad, 2)
        self.assertEqual(20, tabla.tamano())
        for numero in range(20):
            self.assertEqual(numero, tabla.obtener(f"clave-{numero}"))

    def test_elimina_y_reporta_claves_ausentes(self) -> None:
        tabla = HashMap()
        tabla.insertar("existente", None)

        self.assertTrue(tabla.contiene("existente"))
        self.assertIsNone(tabla.obtener("existente"))
        self.assertTrue(tabla.eliminar("existente"))
        self.assertFalse(tabla.eliminar("existente"))
        self.assertFalse(tabla.contiene("existente"))
        self.assertTrue(tabla.esta_vacio())

    def test_rechaza_claves_mutables(self) -> None:
        tabla = HashMap()

        with self.assertRaises(TypeError):
            tabla.insertar(["clave"], "valor")

    def test_recupera_la_misma_clave_aunque_no_sea_reflexiva(self) -> None:
        tabla = HashMap()
        clave = float("nan")

        tabla.insertar(clave, "valor")

        self.assertEqual("valor", tabla.obtener(clave))

    def test_dispersion_separa_permutaciones_de_los_mismos_caracteres(self) -> None:
        tabla = HashMap(1000)
        permutaciones = ("abcd", "badc", "cdab", "dcba")

        indices = {tabla._obtener_indice(nombre) for nombre in permutaciones}

        self.assertEqual(len(permutaciones), len(indices))

    def test_nombres_structurados_no_se_aglomeran_en_una_cubeta(self) -> None:
        tabla = HashMap()
        nombres = [f"user{numero:03d}" for numero in range(1, 201)]

        for nombre in nombres:
            tabla.insertar(nombre, nombre)

        largas = [
            longitud
            for longitud in (self.__longitud_cadena(cubo) for cubo in tabla.tabla)
            if longitud > 0
        ]
        self.assertLess(max(largas), 20)
        for nombre in nombres:
            self.assertEqual(nombre, tabla.obtener(nombre))

    @staticmethod
    def __longitud_cadena(nodo) -> int:
        cantidad = 0
        while nodo is not None:
            cantidad += 1
            nodo = nodo.siguiente
        return cantidad

    def test_contiene_y_eliminar_funcionan_tras_redimensionar(self) -> None:
        tabla = HashMap(2)

        for numero in range(20):
            tabla.insertar(f"clave-{numero}", numero)

        self.assertTrue(tabla.contiene("clave-7"))
        self.assertTrue(tabla.eliminar("clave-7"))
        self.assertFalse(tabla.contiene("clave-7"))
        self.assertIsNone(tabla.obtener("clave-7"))
        self.assertEqual(19, tabla.tamano())


if __name__ == "__main__":
    unittest.main()
