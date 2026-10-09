from network_os.consola import usuarios_locales


def menu_servidor(menu_consola):

    while menu_consola.servidor_actual is not None:
        print("\n--- Menú del servidor ---")
        print("1. Archivos y carpetas")
        print("2. Usuarios locales")
        print("3. Enviar paquete")
        print("0. Cerrar sesión")

        opcion = menu_consola.leer_opcion(["0", "1", "2", "3"])

        if opcion == "1":
            menu_consola.menu_archivos()
        elif opcion == "2":
            menu_usuarios(menu_consola)
        elif opcion == "3":
            menu_consola.enviar_paquete()
        elif opcion == "0":
            menu_consola.servidor_actual = None
            print("Sesión cerrada.")
            return


def menu_usuarios(menu_consola):
    #abre el submenú de usuarios locales del servidor activo
    if menu_consola.servidor_actual is None:
        print("No hay una sesión activa.")
        return

    usuarios_locales(menu_consola.servidor_actual)