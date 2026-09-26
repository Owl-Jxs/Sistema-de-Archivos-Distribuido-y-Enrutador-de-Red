from nodo_hash import NodoHash

class HashMap:

    def __init__(self, capacidad_inicial=10):
        #tabla vacía con la capacidad inicial indicada
        if capacidad_inicial <= 0:
            raise ValueError("La capacidad inicial debe ser mayor que cero.")
        self.capacidad = capacidad_inicial
        self.cantidad = 0
        self.factor_carga_maximo = 0.75
        self.tabla = [None] * self.capacidad

    def insertar(self, clave, valor):
        indice = self._obtener_indice(clave)
        actual = self.tabla[indice]

        #recorre para buscar la clave
        while actual is not None:
            if actual.clave == clave:
                actual.valor = valor
                return
            actual = actual.siguiente

        #si la clave no existe, agrega un nodo al inicio
        nuevo_nodo = NodoHash(clave, valor)
        nuevo_nodo.siguiente = self.tabla[indice]
        self.tabla[indice] = nuevo_nodo
        self.cantidad += 1

        #aumenta la capacidad si la tabla supera la carga máxima
        if self._calcular_factor_carga() > self.factor_carga_maximo:
            self._redimensionar()

    def obtener(self, clave):
        indice = self._obtener_indice(clave)
        actual = self.tabla[indice]

        #busca la clave dentro de la cubeta correspondiente
        while actual is not None:
            if actual.clave == clave:
                return actual.valor
            actual = actual.siguiente
        return None

    def eliminar(self, clave):
        indice = self._obtener_indice(clave)
        actual = self.tabla[indice]
        anterior = None

        #recorre la lista enlazada para encontrar el nodo que se eliminará
        while actual is not None:
            if actual.clave == clave:
                if anterior is None:
                    #el nodo que se elimina es el primero de la cubeta
                    self.tabla[indice] = actual.siguiente
                else:
                    #salta el nodo eliminado y enlaza sus nodos vecinos
                    anterior.siguiente = actual.siguiente
                self.cantidad -= 1
                return True
            anterior = actual
            actual = actual.siguiente
        return False

    def contiene(self, clave):
        indice = self._obtener_indice(clave)
        actual = self.tabla[indice]

        #revisa todos los nodos
        while actual is not None:
            if actual.clave == clave:
                return True
            actual = actual.siguiente
        return False

    def tamano(self):
        return self.cantidad

    def esta_vacio(self):
        return self.cantidad == 0



