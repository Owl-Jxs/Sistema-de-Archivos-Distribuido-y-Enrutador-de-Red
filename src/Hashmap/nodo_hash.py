class NodoHash:
    """Nodo de una cubeta de la tabla hash."""

    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.siguiente = None