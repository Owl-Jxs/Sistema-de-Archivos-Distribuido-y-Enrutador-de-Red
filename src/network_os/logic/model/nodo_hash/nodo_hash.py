from __future__ import annotations

from typing import Any


class NodoHash:
    """Nodo de una cubeta de la tabla hash."""

    def __init__(self, clave: object, valor: Any) -> None:
        self.clave = clave
        self.valor = valor
        self.siguiente: NodoHash | None = None
