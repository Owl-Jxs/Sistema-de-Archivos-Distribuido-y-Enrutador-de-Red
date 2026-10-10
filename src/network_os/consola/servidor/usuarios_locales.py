from getpass import getpass

from ..entrada import leer_opcion

def usuarios_locales(servidor):
    #permite registrar o eliminar usuarios del servidor
    while True:
        print("\n--- Usuarios locales ---")
        print("1. Registrar usuario")
        print("2. Eliminar usuario")
        print("0. Volver")

        opcion = leer_opcion(["0", "1", "2"], "Selecciona una opción: ")

        if opcion == "1": 
            nombre = input("Nombre del nuevo usuario: ").strip()

            if not nombre:
                print("El nombre no puede estar vacío.")
                continue

            contrasena = getpass("Contraseña: ")

            if not contrasena:
                print("La contraseña no puede estar vacía.")
                continue

            try:
                servidor.agregar_usuario(nombre, contrasena)
                print(f"Usuario '{nombre}' registrado.")
            except (ValueError, TypeError, OSError) as error:
                print(f"No se pudo registrar el usuario: {error}")

        elif opcion == "2":
            nombre = input("Nombre del usuario que deseas eliminar: ").strip()

            if not nombre:
                print("El nombre no puede estar vacío.")
                continue

            confirmacion = leer_opcion(
                ["s", "S", "n", "N"], f"¿Eliminar al usuario '{nombre}'? (s/n): ",
            ).lower()

            if confirmacion != "s":
                print("Eliminación cancelada.")
                continue

            try:
                if servidor.eliminar_usuario(nombre):
                    print(f"Usuario '{nombre}' eliminado.")
                else:
                    print(f"El usuario '{nombre}' no existe.")
            except (ValueError, TypeError, KeyError, OSError) as error:
                print(f"No se pudo eliminar el usuario: {error}")

        elif opcion == "0":
            return
