import tempfile
import unittest
from pathlib import Path

from network_os.logic.model.archivo.archivo import Archivo
from network_os.logic.structure.carpeta.carpeta import Carpeta
from network_os.persistencia.persistencia_carpetas.persistencia_arbol_csv import (
    PersistenciaArbolCSV,
)


class PersistenciaArbolCSVTests(unittest.TestCase):
    def test_guardar_y_cargar_reconstruye_el_arbol_completo(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            ruta_csv = Path(directorio) / "archivos.csv"
            persistencia = PersistenciaArbolCSV(ruta_csv)

            raiz = Carpeta(id=0, nombre_carpeta="Documentos")
            universidad = Carpeta(id=1, nombre_carpeta="Universidad")
            proyectos = Carpeta(id=2, nombre_carpeta="Proyectos")
            raiz.agregar_subcarpeta(universidad)
            universidad.agregar_subcarpeta(proyectos)

            archivo_raiz = Archivo(10, "tarea.txt", "Contenido de tarea.")
            notas = Archivo(11, "notas.txt", "Notas de estructuras de datos.")
            proyecto = Archivo(
                12, "proyecto.txt", "Sistema de archivos distribuido."
            )
            raiz.agregar_archivo(archivo_raiz)
            universidad.agregar_archivo(notas)
            proyectos.agregar_archivo(proyecto)

            persistencia.guardar(raiz)
            raiz_cargada = persistencia.cargar()

            self.assertTrue(ruta_csv.exists())
            self.assertEqual(
                (0, "Documentos"),
                (raiz_cargada.id, raiz_cargada.nombre_carpeta),
            )
            self.assertEqual(
                archivo_raiz.ultima_modificacion,
                raiz_cargada.buscar_archivo_por_id(10).ultima_modificacion,
            )
            self.assertEqual(
                "Contenido de tarea.",
                raiz_cargada.buscar_archivo_por_id(10).contenido,
            )

            universidad_cargada = raiz_cargada.buscar_subcarpeta_por_nombre(
                "Universidad"
            )
            self.assertIsNotNone(universidad_cargada)
            assert universidad_cargada is not None
            self.assertEqual(1, universidad_cargada.id)
            self.assertEqual(
                "Notas de estructuras de datos.",
                universidad_cargada.buscar_archivo_por_id(11).contenido,
            )

            proyectos_cargados = (
                universidad_cargada.buscar_subcarpeta_por_nombre("Proyectos")
            )
            self.assertIsNotNone(proyectos_cargados)
            assert proyectos_cargados is not None
            self.assertEqual(2, proyectos_cargados.id)
            self.assertEqual(
                "Sistema de archivos distribuido.",
                proyectos_cargados.buscar_archivo_por_id(12).contenido,
            )
            self.assertEqual(
                proyecto.ultima_modificacion,
                proyectos_cargados.buscar_archivo_por_id(
                    12
                ).ultima_modificacion,
            )


if __name__ == "__main__":
    unittest.main()
