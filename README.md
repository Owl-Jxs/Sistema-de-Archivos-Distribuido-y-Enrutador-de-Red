# Network OS - Simulador de Sistema Operativo de Red

**Proyecto de Investigación Aplicada #2**  
**EIF207 - Estructuras de Datos**  
Universidad Nacional, Sección Regional Central Occidente

---

## 📌 Objetivo del proyecto

Construir el núcleo lógico de un **Network OS**: una simulación de red descentralizada donde múltiples servidores están interconectados.

Cada servidor debe:

- **Administrar su propio sistema de archivos interno** mediante un árbol (jerarquía de carpetas y archivos, con búsqueda recursiva y eliminación en cascada).
- **Autenticar usuarios en tiempo constante `O(1)`** mediante una tabla hash construida desde cero (función de dispersión propia y manejo de colisiones).
- **Enrutar paquetes de datos entre servidores** usando un grafo ponderado, aplicando **Dijkstra** para encontrar la ruta más corta y **BFS/DFS** para diagnosticar si la red está completamente conectada o si hay servidores aislados.
- **Registrar toda acción relevante** en un archivo CSV de auditoría por servidor (`servidores/<nombre>_<id>/auditoria.csv`) y las operaciones generales de la red en `network_audit_log.txt`, con fecha, hora, origen, acción, resultado y detalle.

> El proyecto es de naturaleza **evolutiva**: cada semana se integrarán nuevas reglas de negocio publicadas por el equipo docente (*Sprints*), por lo que el código debe mantenerse **modular y ordenado** desde el inicio.

---

## 🗂️ Estructura del proyecto

```text
network-os/
├── src/
│   └── network_os/
│       ├── main.py                 ← reservado para el controlador de la vista
│       ├── persistencia/
│       │   ├── persistencias_servidorCSV/
│       │   ├── persistencia_auditoria/
│       │   ├── persistencia_carpetas/
│       │   ├── persistencia_red/
│       │   └── persistencia_usuarios/
│       └── logic/
│           ├── controller/
│           │   ├── auditoria/
│           │   ├── gestor_archivos/
│           │   ├── grafo_red/
│           │   └── servidor/
│           ├── model/
│           │   ├── archivo/
│           │   ├── conexion/
│           │   ├── nodo_hash/
│           │   ├── paquete_datos/
│           │   ├── registro_auditoria/
│           │   └── resultado_envio/
│           └── structure/
│               ├── carpeta/
│               ├── hash_table/
│               └── vertice_red/
├── tests/
│   ├── test_archivos.py
│   ├── test_auditoria.py
│   ├── test_auditoria_descentralizada.py
│   ├── test_gestor_archivos.py
│   ├── test_grafo_red.py
│   ├── test_hash_map.py
│   ├── test_paquete_datos.py
│   ├── test_persistencia_arbol_csv.py
│   ├── test_persistencia_red_csv.py
│   ├── test_persistencia_usuarios_csv.py
│   └── test_servidor.py
├── .gitignore
└── README.md
```

---

## Auditoría descentralizada

`Auditoria` se reutiliza como clase, pero sus instancias y archivos son independientes. Cada `Servidor` crea su auditoría local al construirse, también cuando se carga desde el CSV de la red. `GrafoRed` recibe únicamente la auditoría general por constructor y no consulta ni combina los registros locales.

La futura interfaz puede construir el grafo así; `main.py` permanece reservado para la vista:

```python
from network_os.logic.controller.auditoria.auditoria import Auditoria
from network_os.logic.controller.grafo_red.grafoRed import GrafoRed
from network_os.persistencia.persistencia_auditoria.persistencia_auditoria_csv import PersistenciaAuditoriaCSV

auditoria_red = Auditoria("RED", PersistenciaAuditoriaCSV())
grafo = GrafoRed(auditoria=auditoria_red)
registros_red = grafo.consultar_auditoria()
```

La persistencia usa append. Los CSV locales antiguos se conservan y siguen siendo consultables; sus filas sin origen se muestran como `DESCONOCIDO`. Para consultar un servidor se usa `servidor.consultar_auditoria()`. Las operaciones de archivos y carpetas deben llamarse mediante `Servidor` para que queden auditadas.

Las altas de servidores, altas y bajas de conexiones, rutas, ping y guardado/carga de la red registran su resultado una sola vez. Una ruta calculada no registra una entrega. El grafo actual todavía no implementa eliminar servidores, modificar latencias ni enviar paquetes; esta modificación no agrega esas operaciones.

## ▶️ Cómo ejecutar los tests

Requisito: Python 3.10 o superior.

```bash
pip install pytest
py -m pytest tests
```

El `pyproject.toml` de la raíz le indica a pytest que busque los módulos en `src/`, así que no hace falta configurar nada más.

Alternativa sin pytest (usa la librería estándar):

```bash
set PYTHONPATH=src        # macOS/Linux: export PYTHONPATH=src
py -m unittest discover -s tests
```
