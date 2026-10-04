class ResultadoEnvio:
    #guarda los datos y el resultado de un intento de envio
    def __init__(self, entregado, ruta, latencia_total_ms, mensaje):
        self.entregado = entregado
        self.ruta = ruta
        self.latencia_total_ms = latencia_total_ms
        self.mensaje = mensaje