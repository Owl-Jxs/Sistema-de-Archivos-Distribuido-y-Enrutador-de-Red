from conexion import conexion

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
        for indice, conexion in enumerate(self.conexiones):
            if conexion.destino is destino:
                del self.conexiones[indice]
                return True
        return False

    def buscar_conexion(self, destino):
        #devuelve la conexion al destino
        for conexion in self.conexiones:
            if conexion.destino is destino:
                return conexion
        return None

    def esta_aislado(self):
        #devuelve true si el vertice no tiene conexiones
        return len(self.conexiones) == 0