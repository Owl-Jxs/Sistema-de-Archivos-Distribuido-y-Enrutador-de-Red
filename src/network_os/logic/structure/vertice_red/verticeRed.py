from ...model.conexion.conexion import Conexion

class VerticeRed:
    #representa un servidor y sus conexiones dentro del grafo de red

    def __init__(self, servidor):
        #asocia un servidor al vertice
        self.servidor = servidor
        self.conexiones = []

    def agregar_conexion(self, conexion):
        #agrega una conexion a la lista de conexiones del vertice
        self.conexiones.append(conexion)

    def eliminar_conexion(self, destino):
        #elimina la conexion al destino y devuelve si pudo encontrarla
        #compara por nombre de servidor: tras cargar() las referencias
        #de los vertices se reconstruyen y la identidad (is) deja de valer
        for indice, conexion in enumerate(self.conexiones):
            if self.__mismo_destino(conexion.destino, destino):
                del self.conexiones[indice]
                return True
        return False

    def buscar_conexion(self, destino):
        #devuelve la conexion al destino
        for conexion in self.conexiones:
            if self.__mismo_destino(conexion.destino, destino):
                return conexion
        return None

    @staticmethod
    def __mismo_destino(actual, esperado):
        #compara dos vertices por el nombre de su servidor
        return actual.servidor.nombre == esperado.servidor.nombre

    def esta_aislado(self):
        #devuelve true si el vertice no tiene conexiones
        return len(self.conexiones) == 0