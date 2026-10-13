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

### Bitácora Erving Sequeira

## 1. Definición de Arquitectura y Estructura Inicial
> **Modelo utilizado:** Claude Sonnet 5.5

* **Prompt:**  
  > "Estoy empezando este proyecto en Python de NetworkOS, necesito saber cuál sería una buena arquitectura y estructura para las carpetas, aparte necesito un `.gitignore` bien hecho y quiero que el `README` resuma lo que decía el enunciado, para guiar al grupo."

* **Respuesta de la IA:**  
  Propuso una estructura `src/network_os/` con carpetas por tema (`arbol`, `auditoria`, `grafo`, `hash_table`), `test/` en la raíz, un `.gitignore` para Python y un borrador del `README`.

* **Adaptación en NetworkOS:**  
  Ajustamos la propuesta para aplicar un patrón **MVC**:
  * Inicialmente establecimos las carpetas `logic/` (con `controller`, `model` y `estructure`) y `persistencia/`.
  * La carpeta `consola/` apareció a la par de estas cuando se implementaron los menús de interacción.
  * La carpeta `test/` se mantuvo en la raíz al nivel de `src/`.

---

## 2. Diseño del Módulo de Auditoría y Trazabilidad Global
> **Modelo utilizado:** Claude Sonnet 5.5

* **Prompt:**  
  > "Estoy por trabajar en el módulo de auditoría, la idea sería el registro de cada servidor para anotar su fecha y hora, categoría, acción, resultado, detalle, como dividirlo bien para la base."

* **Respuesta de la IA:**  
  Propuso crear una clase `RegistroAuditoria` como estructura inmutable (`frozen`) para evitar alteraciones, un gestor `PersistenciaAuditoria` para manejar archivos CSV por cada servidor, y una fachada llamada `AuditoriaServidor` conectada al futuro modelo de `Servidor`. Además, generó automáticamente la estructura inicial para `test_auditoria`.

* **Adaptación en NetworkOS:**  
  Ampliamos el alcance inicial al darnos cuenta de que la red poseía un **GrafoRed** completo que también requería trazabilidad:
  * Renombramos `AuditoriaServidor` a simplemente `Auditoria` para soportar tanto eventos individuales de servidores como eventos globales de red (reconstrucción, adición/eliminación de nodos, guardado de red).
  * Añadimos un sexto campo para registrar explícitamente el origen del evento (servidor o red).
  * Modificamos la estrategia de persistencia: además de los registros por servidor, incorporamos un archivo global `network_audit_log.txt` para centralizar la auditoría de toda la red.

---

## 3. Implementación Base del Grafo de Red y Persistencia CSV
> **Modelo utilizado:** Claude Sonnet 5.5

* **Prompt:**  
  > "Estoy listo para continuar con el GrafoRed que ya teníamos previsto para auditoría, aunque solo dejaré el mínimo para que mis compañeros creen la lógica, guardar y cargar, ya mi compañera creó el vértice red entonces ayúdame a crear la lógica de esto, junto a una PersistenciaRedCSV que me de la red de conexiones para ver el tipo, nombre, id, direccion base, origen, destino y latencia_ms."

* **Respuesta de la IA:**  
  Generó una estructura base aprovechando el vértice de red previamente creado por el equipo, implementando la lógica inicial del grafo junto con un módulo `PersistenciaRedCSV` capaz de serializar y deserializar las conexiones contemplando sus atributos (tipo, nombre, id, dirección base, origen, destino y latencia en ms).

* **Adaptación en NetworkOS:**  
  Como equipo validamos que esta propuesta cumplía perfectamente con el objetivo de servir como cimiento sólido y estandarizado, permitiendo que el resto de compañeros se integraran fácilmente a desarrollar las funcionalidades avanzadas y lógicas restantes sobre el grafo.

---

## 4. Refactorización Integral, Corrección de Bugs y Robustez (Modo Plan/Build)
> **Modelo utilizado:** OpenCode Mimo 2.6

* **Prompt (Agente de código):**  
  > "Quiero que busques errores en el código, primero vamos en modo plan para luego pasar a build, te digo como tal las cosas que quiero arreglar de una vez: las contraseñas con tilde no son lo mismo al autenticar, como 'mónica' y 'monica'; quiero que el guardar en CSV tenga escritura atómica (archivo temporal y reemplazar solo si salió bien) junto a rollback por si el guardado falla y deshace en memoria; el grafo hay que arreglarlo ya que las conexiones no son bidireccionales, solo de A -> B; para el árbol necesitamos la búsqueda recursiva y poder imprimirlo con indentación; aparte estoy dependiendo de usar tzdata para zona horaria."

* **Respuesta de la IA (Agente de código):**  
  * Encontró un bug crítico en la tabla hash (degradación a $O(n)$ por mezcla de bits ausente en strings) y propuso un mixer universal.
  * Solucionó la autenticación con tildes mediante comparación segura en UTF-8 con `hmac.compare_digest`.
  * Diseñó la escritura atómica en CSV con rollback en memoria y corrigió el grafo (conexiones bidireccionales, borrado, validación de latencias con `math.isfinite` para Dijkstra).
  * Añadió búsqueda recursiva e impresión con indentación en el árbol, configuró `pyproject.toml` para pruebas sin `PYTHONPATH`, y reemplazó `tzdata` por zona horaria nativa UTC-6 (Costa Rica).

* **Adaptación en NetworkOS:**  
  * Validamos e integramos todas las correcciones, elevando drásticamente la robustez y seguridad del sistema reflejada en la estructura de clases final.

---

## 5. Estructuración y Modularización de la Consola
> **Modelo utilizado:** Claude Sonnet 5.5

* **Prompt:**  
  > "Esta vez me toca que el proyecto se pueda ejecutar ya, quiero que me ayudes a decidir la estructura para el menu_consola, decidí crear la carpeta consola/ ya y dentro menu_consola, de momento quedara monolítico ya que quiero dejar más o menos varios docstrings por menú y que los menús de momento devuelvan un print que diga que esto falta, pero dejar hecho el iniciar sesión, pedimos un servidor pero si no hay pues toca meter un método en Servidor para saber si no hay usuarios y así pedir uno al inicio, bueno, para cuando haya servers creados por los otros menú."

* **Respuesta de la IA:**  
  * Propuso un menú monolítico base con opciones de red, servidor y auditoría, utilidades de entrada (`leer_opcion`, `pausar`), validación de usuarios vacíos (`usuarios_vacios`) y un archivo raíz `run.py` para depuración en VS Code.

* **Adaptación en NetworkOS:**  
  * El equipo evolucionó este planteamiento inicial dividiendo la interfaz en clases separadas organizadas en subdirectorios especializados (`consola/principal/`, `consola/red/` y `consola/servidor/`) para mantener la cohesión modular que se aprecia en el diagrama final.

---

## 6. Limpieza de Código Muerto, Parcheo de Auditoría y Manejo de Excepciones
> **Modelo utilizado:** OpenCode Mimo 2.6

* **Prompt (Agente de código):**  
  > "Sabes hay una lógica de portapapeles, cortar, copiar y pegar que ningún menú usa pero estaba planeada por mi compañero por si hacíamos interfaz gráfica me dijo, esto quedó como consola y es código y test que pues realmente no se usa, corta eso como tal ya de por si cumplimos con el enunciado sin ese añadido, pasa en persistencia auditoria csv que si el archivo era viejo, podía ser por haberlo probado antes y que quedaran registros de header 5 pues al escribir se pega un sexto valor DESCONOCIDO al final de cada fila nueva, entonces que eso ya no inspeccione el header y no separe el campo faltante, saca esos test pero no toques CAMPOS, busca si encuentras algo que necesite atención."

* **Respuesta de la IA (Agente de código):**  
  * Validó que los nombres de usuario exijan al menos una letra para evitar que nombres puramente numéricos rompieran la autenticación.
  * Eliminó 316 líneas de código muerto y tests asociados al portapapeles no utilizado.
  * Simplificó `persistencia_auditoria_csv.py` trabajando con campos estables sin inspección dinámica de encabezados obsoletos.

* **Adaptación en NetworkOS:**  
  * Implementamos manejo manual de excepciones en consola (`except FileNotFoundError:`) para inicializar una red vacía si el archivo CSV no existe o está corrupto, asegurando un arranque limpio y tolerante a fallos.
