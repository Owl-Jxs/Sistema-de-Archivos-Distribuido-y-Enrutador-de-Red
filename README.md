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

### Isabella Cubillo Paniagua

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


### Bitácora Arleth Varela González
Le pedí ayuda a la IA en varias ocasiones principalmente para poder implementar la lógica en Python ya que nunca había trabajado un proyecto en este lenguaje de programación y también para que me pudiera explicar definiciones que no conocía, en los archivos que realicé puse algunos comentarios de explicación.

1. Estructura de HashMap
Prompt: Ayúdame a implementar la tabla hash en el archivo hashMap con base en el UML. 
Para obtener una propuesta de tabla hash y cómo podría hacer para las operaciones de insertar, buscar y eliminar elementos.

2. Persistencia de usuarios
Prompt: Podrías decirme cómo puedo implementar la persistencia de los usuarios donde guarde los usuarios y pueda cargarlos en un HashMap.
Sirvió para proponer cómo conservar los usuarios en un archivo CSV y reconstruir la tabla hash al cargar los datos. Se aclaró que los objetos guardados como datos JSON pueden recuperarse como diccionarios.

3. Menú del servidor y usuarios locales
Prompt: Ayúdame a implementar la lógica para el menú del servidor y del submenú de usuarios locales, para poder definir opciones de navegación para administrar archivos, usuarios y envío de paquetes. 
Me recomendó verificar si el usuario existe antes de registrarlo o eliminarlo.

5. Aclaraciones sobre imports en Python
Prompt: Explícame para qué sirve from getpass import getpass. 
Me sirvió para comprender cómo se oculta una contraseña durante su captura. También me ayudó a implementar un getpass para que la contraseña no se muestre al escribirla.



### Bitacora de Daniel

 El uso que le di a la AI Tuvo distintos enfoques:
  - Crear Tests de las partes del sistema para validar un correcto funcionamiento del mismo.
  - A partir de estos tests o de prompts especificos,  se buscaban posibles errores, de encontrarlos se clasificaban en dos tipos (Si era logica o sintaxis el mismo aagente se encargaba de corregirlo y  me informaba posteriorimente, en el caso de errores de diseno o estructura del proyecto el azgente se   encargaba de informarmelo para ser yo el que tome la decision de que debia de hacer para corregirlo).
  - Automatizar creacion de codigo repetitivo o ya con conocimientos sobre el mismo para agilizar el progreso del proyecto.
  - Implenentar codigo correcto en python, ya que no conocia el lenguaje pero si tenia claro lo que debia lograr


#### Partes em el proyecto de AI:
1. Pruebas del sistema
Utilicé la IA para crear y actualizar pruebas en la carpeta tests conforme avanzaban las funcionalidades del proyecto. Estas verificaban casos normales, entradas inválidas y situaciones como servidores desconectados o carpetas anidadas.
No hay como tal un prompt que ejecute esto. Los prompts estaban estaban en las solicitudes de implementación, por ejemplo: “Ejecuta las pruebas existentes y comprueba los casos indicados”.

2. Auditoría de servidores y red
Me di cuenta que las auditorias estaban mal disenadadss y dejaban fuera procesos de la red, despues de esto analice como se debian redisenar y Solicité adaptar la auditoría para registrar las operaciones del grafo. Para posteriormente separar los registros de cada servidor de los movimientos de la red.
Prompt utilizado: “En auditoria en este momento el diseno contempla solo los procesos de todos los servidores en una sola dentro de la red, pero cada servidor debe manejar su auditoria y la red una propia. Haz una clase genérica Auditoria, con instancias y archivos independientes para cada servidor y para la red.
este cambia en el código para que la descentralice y que ahora cada servidor tenga su auditoría y en el grafo haya una auditoría aparte”.

3. Organización de los menús de consola
Utilicé la IA para revisar los menús y organizarlos en clases y carpetas según su responsabilidad, tomando el UML como referencia.
Prompt utilizado: “Necesito que revises lo que ya está y corrijas errores de logica y  sintaxis dentro de las clases que funcionan como las interfaces de consola, además separa la estructura actual en diferentes clases respetando las funciones dentro de ellas como están ahora, esto para dejar una clase de vista para cada parte (la red, el servidor y el gestor de archivos)”.

4. Envío de paquetes
Solicité completar la integración de envío que había quedado comentada en el menú del servidor mientras esperaba que una companera terminara  metodos faltantes para esta funcionalidada
Prompt utilizado: “Revisa el flujo que hay para enviar un paquete entre servidores, empezando por el menu del servidor. Revisa todo el flujo buscando errores o partes faltantes o mal conectadas, de haberlas completa las partes faltantes ”.
Nota: La IA ayudó a conectar PaqueteDatos, el enrutamiento de GrafoRed, la recepción en Servidor y ResultadoEnvio. Se mantuvieron las estructuras existentes y se verificó que la entrega se confirmara después de guardar el contenido en el destino.

5. Diagnóstico de red y latencias simuladas
Después de comparar el proyecto con el enunciado, solicité ajustar el Ping General y generar automáticamente las latencias de las conexiones.
Prompt utilizado: “Revisa el Ping General y ajústalo para utilizar BFS, indicando si todos los servidores están comunicados y distinguiendo los servidores aislados de los componentes desconectados. Además, al crear una conexión, genera una latencia aleatoria dentro de un rango razonable sin pedir los milisegundos al usuario'
