from network_os.logic.structure.archivo.archivo import Archivo
from network_os.logic.structure.carpeta.carpeta import Carpeta

def main():
    carpeta = Carpeta(1, "Documentos")

    archivo = Archivo(
        1,
        "tarea.txt",
        "Este es el contenido de prueba."
    )

    carpeta.agregar_archivo(archivo)

    print("Carpeta:", carpeta.nombre_carpeta)
    print("Direccion:", carpeta.direccion_carpeta)

    print("\nArchivos de la carpeta:")

    for archivo in carpeta.listar_archivos():
        print(
            f"ID: {archivo.id} | "
            f"Nombre: {archivo.nombre} | "
            f"Contenido: {archivo.contenido}"
        )


if __name__ == "__main__":
    main()