import csv
import json
from pathlib import Path
from network_os.logic.structure.hash_table.hash_map import HashMap


class PersistenciaUsuariosCSV:
    def __init__(self, ruta_csv):
        #guarda la ruta del archivo CSV que se utilizara
        self.ruta_csv = Path(ruta_csv)

    def guardar(self, usuarios):
        #escribe en el CSV las claves y valores del HashMap
        #crea las carpetas necesarias si todavia no existen
        self.ruta_csv.parent.mkdir(parents=True, exist_ok=True)

        #abre el archivo en modo escritura, si ya existe, lo reemplaza
        with self.ruta_csv.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)

            #escribe los nombres de las columnas
            escritor.writerow(["clave", "valor"])

            #guarda cada pareja del HashMap en una fila
            for clave, valor in usuarios.obtener_elementos():
                clave_json = json.dumps(clave, ensure_ascii=False)
                valor_json = json.dumps(valor, ensure_ascii=False, default=self._convertir_objeto)
                escritor.writerow([clave_json, valor_json])

    def cargar(self):
        usuarios = HashMap()

        #si el archivo no existe, devuelve un HashMap vacio
        if not self.ruta_csv.exists():
            return usuarios

        #abre el CSV y procesa sus filas usando los encabezados
        with self.ruta_csv.open("r", newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)

            for fila in lector:
                #convierte los textos JSON a sus tipos de dato originales
                clave = json.loads(fila["clave"])
                valor = json.loads(fila["valor"])

                #agrega la pareja al HashMap reconstruido
                usuarios.insertar(clave, valor)
        return usuarios

    def _convertir_objeto(self, objeto):
        #permite serializar objetos que guardan sus atributos
        if hasattr(objeto, "__dict__"):
            return objeto.__dict__

        raise TypeError(f"No se puede guardar un objeto de tipo " f"{type(objeto).__name__} en formato JSON.")