from getpass import getpass
#oculta los caracteres mientras escribes

def usuarios_locales(servidor):
    #permite registrar o eliminar usuarios del servidor
    while True:
        print("\n--- Usuarios locales ---")
        print("1. Registrar usuario")
        print("2. Eliminar usuario")
        print("0. Volver")

        opcion = input("Selecciona una opción: ").strip()

        if opcion not in ["0", "1", "2"]: 
            print("Opción inválida. Intenta de nuevo.")
            continue

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
            except ValueError as error:
                print(f"No se pudo registrar el usuario: {error}")

        elif opcion == "2":
            nombre = input("Nombre del usuario que deseas eliminar: ").strip()

            if not nombre:
                print("El nombre no puede estar vacío.")
                continue

            confirmacion = input(f"¿Eliminar al usuario '{nombre}'? (s/n): ").strip().lower()

            if confirmacion != "s":
                print("Eliminación cancelada.")
                continue

            try:
                servidor.eliminar_usuario(nombre)
                print(f"Se solicitó la eliminación del usuario '{nombre}'.")
            except (ValueError, KeyError) as error:
                print(f"No se pudo eliminar el usuario: {error}")

        elif opcion == "0":
            return