import unittest
from datetime import datetime

from network_os.logic.model.paquete_datos.paquete_datos import PaqueteDatos


class PaqueteDatosTests(unittest.TestCase):
    def test_normaliza_los_datos_del_paquete(self) -> None:
        contenido = {"dato": 1}
        paquete = PaqueteDatos(
            origen=" origen ",
            destino=" destino ",
            tipo="subcarpeta",
            contenido=contenido,
        )

        self.assertEqual("origen", paquete.origen)
        self.assertEqual("destino", paquete.destino)
        self.assertEqual("SUBCARPETA", paquete.tipo)
        self.assertIs(contenido, paquete.contenido)
        self.assertIsInstance(paquete.fecha_envio, datetime)

    def test_rechaza_datos_invalidos(self) -> None:
        casos = (
            {"origen": "", "destino": "b", "tipo": "T", "contenido": 1},
            {"origen": "a", "destino": "", "tipo": "T", "contenido": 1},
            {"origen": "a", "destino": "b", "tipo": "", "contenido": 1},
            {"origen": "a", "destino": "b", "tipo": "T", "contenido": None},
        )

        for datos in casos:
            with self.subTest(datos=datos):
                with self.assertRaises(ValueError):
                    PaqueteDatos(**datos)


if __name__ == "__main__":
    unittest.main()
