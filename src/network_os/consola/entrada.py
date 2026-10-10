def leer_opcion(validas: list[str], mensaje: str = "Opcion: ") -> str:
    """Pide una opcion hasta que pertenezca a los valores permitidos."""
    while True:
        entrada = input(mensaje).strip()
        if entrada in validas:
            return entrada
        print(f"Opcion invalida: '{entrada}'. Intente de nuevo.")


def pausar() -> None:
    input("\nPresione Enter para continuar...")
