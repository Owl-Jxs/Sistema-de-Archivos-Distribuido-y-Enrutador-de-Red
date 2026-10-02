from network_os.logic.persistence.persistencia_arbol_csv import (
    PersistenciaArbolCSV,
)
from network_os.logic.structure.archivo.archivo import Archivo
from network_os.logic.structure.carpeta.carpeta import Carpeta


# 1. Crear el árbol

raiz = Carpeta(
    id=0,
    nombre_carpeta="Documentos",
)

universidad = Carpeta(
    id=1,
    nombre_carpeta="Universidad",
)

proyectos = Carpeta(
    id=2,
    nombre_carpeta="Proyectos",
)

raiz.agregar_subcarpeta(universidad)
universidad.agregar_subcarpeta(proyectos)


# 2. Crear archivos

archivo1 = Archivo(
    id=10,
    nombre="tarea.txt",
    contenido="Este es el contenido de la tarea.",
)

archivo2 = Archivo(
    id=11,
    nombre="notas.txt",
    contenido="Notas de estructuras de datos.",
)

archivo3 = Archivo(
    id=12,
    nombre="proyecto.txt",
    contenido="Sistema de archivos distribuido.",
)



# 3. Agregar archivos a sus carpetas

raiz.agregar_archivo(archivo1)
universidad.agregar_archivo(archivo2)
proyectos.agregar_archivo(archivo3)


# 4. Guardar

persistencia = PersistenciaArbolCSV(
    "datos/archivos.csv"
)

persistencia.guardar(raiz)

print("Árbol guardado correctamente.")
print()

# 5. Cargar

raiz_cargada = persistencia.cargar()

print("Árbol cargado correctamente.")
print()


# Verificar que se recuperó la carpeta raíz.
assert raiz_cargada.id == 0
assert raiz_cargada.nombre_carpeta == "Documentos"

# Verificar el archivo que está en la raíz.
archivo_raiz = raiz_cargada.buscar_archivo_por_id(10)

assert archivo_raiz is not None
assert archivo_raiz.nombre == "tarea.txt"
assert archivo_raiz.contenido == "Este es el contenido de la tarea."

# Verificar la subcarpeta Universidad.
universidad = raiz_cargada.buscar_subcarpeta_por_nombre("Universidad")

assert universidad is not None
assert universidad.id == 1

# Verificar el archivo dentro de Universidad.
notas = universidad.buscar_archivo_por_id(11)

assert notas is not None
assert notas.nombre == "notas.txt"
assert notas.contenido == "Notas de estructuras de datos."

# Verificar la subcarpeta Proyectos.
proyectos = universidad.buscar_subcarpeta_por_nombre("Proyectos")

assert proyectos is not None
assert proyectos.id == 2

# Verificar el archivo dentro de Proyectos.
proyecto = proyectos.buscar_archivo_por_id(12)

assert proyecto is not None
assert proyecto.nombre == "proyecto.txt"
assert proyecto.contenido == "Sistema de archivos distribuido."

# Verificar que las fechas también se recuperaron.
assert archivo_raiz.ultima_modificacion is not None
assert notas.ultima_modificacion is not None
assert proyecto.ultima_modificacion is not None

print("¡Todas las pruebas de persistencia pasaron correctamente!")


# 6. Mostrar árbol cargado

def mostrar_carpeta(carpeta: Carpeta, nivel: int = 0) -> None:
    espacios = "    " * nivel

    print(
        f"{espacios}Carpeta: "
        f"{carpeta.nombre_carpeta}"
    )

    print(
        f"{espacios}Direccion: "
        f"{carpeta.direccion_carpeta}"
    )

    for archivo in carpeta.listar_archivos():
        print(
            f"{espacios}    Archivo: "
            f"{archivo.nombre}"
        )

        print(
            f"{espacios}    ID: "
            f"{archivo.id}"
        )

        print(
            f"{espacios}    Contenido: "
            f"{archivo.contenido}"
        )

    print()

    for subcarpeta in carpeta.listar_contenido():
        mostrar_carpeta(
            subcarpeta,
            nivel + 1,
        )


mostrar_carpeta(raiz_cargada)