class Conexion:
    #representa una conexion hacia otro vertice de la red
    def __init__(self, destino, latencia_ms):
        #inicializa el vertice de destino y la latencia de la conexion
        self.destino = destino
        self.latencia_ms = latencia_ms

    def actualizar_latencia(self, latencia):
        #actualiza la latencia de la conexion
        self.latencia_ms = latencia