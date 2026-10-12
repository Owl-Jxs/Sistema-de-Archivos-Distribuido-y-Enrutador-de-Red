# Network OS - Simulador de Sistema Operativo de Red

**Proyecto de Investigación Aplicada #2** · **EIF207 - Estructuras de Datos**
Universidad Nacional, Sección Regional Central Occidente

## ¿Qué hace?

Simula una red descentralizada de servidores interconectados. Cuando esté
terminado:

- Cada servidor administra su **sistema de archivos** como un árbol de carpetas
  y archivos, con búsqueda recursiva y borrado en cascada.
- Cada servidor **autentica usuarios en tiempo O(1)** con una tabla hash
  construida desde cero (función de dispersión propia y manejo de colisiones).
- Los servidores se **enrutan paquetes** por un grafo ponderado: Dijkstra para
  la ruta más corta y BFS/DFS para detectar red aislada o fragmentada.
- **Toda acción queda auditada**: cada servidor escribe su propio log y la red
  escribe `network_audit_log.txt` (fecha, origen, acción, resultado, detalle).
- La interacción ocurre por **menús de consola**.

El código está separado en `logic` (reglas de negocio), `persistencia` (CSV) y `consola`
(menús).

## Estructura

```text
network-os/
├── run.py                        ← punto de entrada (python run.py)
├── pyproject.toml                ← configura pytest para buscar en src/
├── src/network_os/
│   ├── main.py                   ← main(): inicialización y menú principal
│   ├── consola/                  ← menús separados por responsabilidad
│   │   ├── principal/
│   │   │   └── menu_consola.py   ← MenuConsola: principal, sesión y auditoría general
│   │   ├── entrada.py            ← lectura de opciones y pausas
│   │   ├── red/menu_red.py       ← MenuRed: administración y diagnóstico de la red
│   │   └── servidor/
│   │       ├── menu_servidor.py  ← MenuServidor: archivos, usuarios, envío y auditoría local
│   │       ├── menu_archivos.py  ← MenuArchivos: operaciones del repositorio
│   │       └── usuarios_locales.py ← gestión de usuarios existente
│   ├── logic/
│   │   ├── controller/           ← auditoria · gestor_archivos · grafo_red · servidor
│   │   ├── model/                ← archivo · conexion · paquete_datos · registros
│   │   └── structure/            ← carpeta · hash_table · vertice_red
│   └── persistencia/             ← CSV: red · servidores · usuarios · árbol · auditoría
└── tests/                        ← pruebas unitarias
```

## ▶️ Cómo ejecutar el programa (VS Code)

1. Abrir la carpeta del proyecto en VS Code.
2. Terminal integrada con <kbd>Ctrl</kbd> + <kbd>`</kbd> y:

```bash
python run.py
```

También funciona el botón ▶ de VS Code con `run.py` abierto.
Alternativa sin launcher:

```bash
set PYTHONPATH=src && python -m network_os.main   # Windows cmd
$env:PYTHONPATH="src"; python -m network_os.main  # PowerShell
```

## Menús y envío de paquetes

Los submenús usan bucles y la opción `0` vuelve al menú que los abrió. Las
contraseñas se leen con `getpass`. El primer usuario de un servidor vacío se
crea durante el acceso, conservando el flujo actual.

La opción `3` del menú principal consulta la auditoría de la red en
`network_audit_log.txt`. La opción `4` del menú del servidor permite consultar
sus registros locales en `servidores/<nombre>_<id>/auditoria.csv`, mediante
`Servidor.consultar_auditoria()`. Cada consulta lee exclusivamente su archivo
y no agrega eventos ni combina los registros de otros servidores.

El menú de archivos lista el contenido directo, navega, crea carpetas y archivos,
busca archivos desde la raíz, imprime el árbol y confirma los borrados en cascada.
Las creaciones y eliminaciones se guardan mediante `Servidor.guardar_estado()`;
la auditoría permanece en los módulos lógicos.

Al crear una conexión, el menú pide los servidores de origen y destino.
`GrafoRed.agregar_conexion()` asigna una latencia aleatoria entera entre 1 y
100 ms, compartida por ambos sentidos y conservada en CSV. La lógica también
admite una latencia explícita para las pruebas y la carga de datos.

El Ping General utiliza BFS para determinar los servidores alcanzables y
Dijkstra para conservar la información de latencias mínimas. El menú informa
si todos están comunicados o si la red está fragmentada, y distingue los
servidores aislados de los que pertenecen a otro componente conectado.
Una autoconexión no cuenta como comunicación con otros servidores.

El menú pide destino y contenido y llama a
`Servidor.enviar_paquete(grafo, paquete)`. El grafo recibe un `PaqueteDatos`,
calcula una sola vez la ruta mínima y solicita la recepción al destino. Devuelve
un `ResultadoEnvio` con `entregado`, `ruta`, `latencia_total_ms` y `mensaje`;
solo confirma la entrega cuando el contenido se recibió y guardó en CSV.
Sin ruta devuelve `entregado=False`, una ruta vacía y latencia infinita.
Los servidores inexistentes y los argumentos inválidos producen errores.

El envío de consola admite texto, que se guarda como `mensaje_<fecha>.txt`
en la carpeta actual del receptor, con un sufijo si el nombre ya existe.
La lógica también admite archivos y subcarpetas: se importan copias independientes
con IDs propios del destino. Un nombre duplicado se rechaza sin sobrescribir.
Si falla el guardado, se retira la copia y se conserva el CSV anterior.
La persistencia existente guarda los contenidos como texto, también para estos
envíos; no serializa objetos Python arbitrarios con su tipo original.

El origen registra su solicitud y el destino su recepción en sus logs locales;
la red registra únicamente el envío, su recorrido, costo y resultado, sin copiar
registros locales ni guardar el contenido del paquete. Se trata de una transferencia
dentro del simulador, sin sockets ni comunicación entre equipos físicos.

## 🧪 Cómo ejecutar los tests

Requisito: Python 3.10 o superior.

```bash
pip install pytest
python -m pytest tests
```

El `pyproject.toml` le indica a pytest que busque los módulos en `src/`, así
que no hace falta configurar nada más.

Alternativa sin pytest (librería estándar):

```bash
set PYTHONPATH=src
python -m unittest discover -s tests
```

## Promps usados durante el desarrollo:

## Isabella Cubillo Paniagua

1. Archivos y persistencia de carpetas:
Ayúdame a revisar cómo implementar el guardado y la carga de carpetas para que la estructura de archivos pueda persistirse y recuperarse correctamente. Explícame cómo manejar los datos almacenados y cómo evitar problemas al reconstruir la estructura desde los archivos de persistencia.

2. Grafo de red

Actualizar latencia:
Ayúdame a implementar una función para actualizar la latencia de una conexión entre dos servidores del grafo de red. Considera cómo identificar los servidores, validar la nueva latencia y mantener actualizada la conexión existente.

Enviar paquetes:
Explícame cómo implementar el envío de un paquete de datos entre servidores representados en un grafo de red. Considera cómo identificar el servidor de origen y el destino, comprobar si existe una ruta y manejar los casos en los que el destino no sea alcanzable.

Identificar servidores aislados:
Ayúdame a determinar cómo identificar los servidores aislados de un grafo de red. Explícame cómo recorrer la estructura y distinguir un servidor sin conexiones de uno que sí forma parte de la red.

Eliminar servidores:
Ayúdame a revisar la lógica para eliminar un servidor de un grafo de red. Considera cómo retirar el vértice correspondiente y sus conexiones para evitar que queden referencias a un servidor que ya no existe.

3. Menú de red y auditoría

Menú de red:
Ayúdame a organizar el menú de administración de la red para que el usuario pueda acceder de forma clara a las operaciones disponibles, como administrar servidores y conexiones, actualizar latencias y consultar información de conectividad. Procura mantener el menú coherente con los métodos existentes en el proyecto.

Menú de auditoría:
Ayúdame a estructurar un menú de auditoría que permita consultar los registros de operaciones del sistema. Considera opciones para visualizar los registros disponibles y los más recientes, utilizando las funciones de auditoría que ya existen en el proyecto.

