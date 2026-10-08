from __future__ import annotations

from typing import Any

from ...model.nodo_hash.nodo_hash import NodoHash


class HashMap:
    """Tabla hash con encadenamiento separado para resolver colisiones."""

    def __init__(self, capacidad_inicial: int = 10) -> None:
        if (
            not isinstance(capacidad_inicial, int)
            or isinstance(capacidad_inicial, bool)
            or capacidad_inicial <= 0
        ):
            raise ValueError("La capacidad inicial debe ser un entero mayor que cero.")

        self.capacidad = capacidad_inicial
        self.cantidad = 0
        self.factor_carga_maximo = 0.75
        self.tabla: list[NodoHash | None] = [None] * self.capacidad

    @staticmethod
    def _validar_clave(clave: object) -> None:
        try:
            hash(clave)
        except TypeError as error:
            raise TypeError("La clave debe ser un objeto hashable.") from error

    @staticmethod
    def _claves_iguales(primera: object, segunda: object) -> bool:
        return primera is segunda or primera == segunda

    def _obtener_indice(self, clave: object) -> int:
        """Calcula la cubeta usando una dispersion polinomial y mezcla de bits."""
        self._validar_clave(clave)

        if isinstance(clave, str):
            valor_hash = 0
            for byte in clave.encode("utf-8"):
                valor_hash = ((valor_hash * 31) + byte) & 0xFFFFFFFFFFFFFFFF
        else:
            # Para claves genericas se respeta su contrato de igualdad/hash.
            valor_hash = hash(clave) & 0xFFFFFFFFFFFFFFFF

        # Mezcla final de bits (avalanche): sin ella, 31 == 1 (mod 2^k * 5)
        # hace que permutaciones de los mismos caracteres caigan en la misma
        # cubeta y la tabla degenere a O(n) con pocos usuarios.
        valor_hash ^= valor_hash >> 33
        valor_hash = (valor_hash * 0xFF51AFD7ED558CCD) & 0xFFFFFFFFFFFFFFFF
        valor_hash ^= valor_hash >> 33

        return valor_hash % self.capacidad

    def _calcular_factor_carga(self) -> float:
        return self.cantidad / self.capacidad

    def _redimensionar(self) -> None:
        tabla_anterior = self.tabla
        self.capacidad *= 2
        self.tabla = [None] * self.capacidad

        for primer_nodo in tabla_anterior:
            actual = primer_nodo
            while actual is not None:
                siguiente = actual.siguiente
                indice = self._obtener_indice(actual.clave)
                actual.siguiente = self.tabla[indice]
                self.tabla[indice] = actual
                actual = siguiente

    def insertar(self, clave: object, valor: Any) -> None:
        indice = self._obtener_indice(clave)
        actual = self.tabla[indice]

        while actual is not None:
            if self._claves_iguales(actual.clave, clave):
                actual.valor = valor
                return
            actual = actual.siguiente

        nuevo_nodo = NodoHash(clave, valor)
        nuevo_nodo.siguiente = self.tabla[indice]
        self.tabla[indice] = nuevo_nodo
        self.cantidad += 1

        if self._calcular_factor_carga() > self.factor_carga_maximo:
            self._redimensionar()

    def obtener(self, clave: object) -> Any | None:
        indice = self._obtener_indice(clave)
        actual = self.tabla[indice]

        while actual is not None:
            if self._claves_iguales(actual.clave, clave):
                return actual.valor
            actual = actual.siguiente
        return None

    def eliminar(self, clave: object) -> bool:
        indice = self._obtener_indice(clave)
        actual = self.tabla[indice]
        anterior: NodoHash | None = None

        while actual is not None:
            if self._claves_iguales(actual.clave, clave):
                if anterior is None:
                    self.tabla[indice] = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente

                actual.siguiente = None
                self.cantidad -= 1
                return True

            anterior = actual
            actual = actual.siguiente
        return False

    def contiene(self, clave: object) -> bool:
        indice = self._obtener_indice(clave)
        actual = self.tabla[indice]

        while actual is not None:
            if self._claves_iguales(actual.clave, clave):
                return True
            actual = actual.siguiente
        return False

    def tamano(self) -> int:
        return self.cantidad

    def esta_vacio(self) -> bool:
        return self.cantidad == 0

    def obtener_elementos(self) -> list[tuple[object, Any]]:
        elementos: list[tuple[object, Any]] = []
        for primer_nodo in self.tabla:
            actual = primer_nodo
            while actual is not None:
                elementos.append((actual.clave, actual.valor))
                actual = actual.siguiente
        return elementos
