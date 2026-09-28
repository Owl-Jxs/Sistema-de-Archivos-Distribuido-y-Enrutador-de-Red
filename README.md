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
- **Registrar toda acción relevante** en un archivo CSV de auditoría (`network_audit_log.csv`), con fecha, hora y detalle de la transacción.

> El proyecto es de naturaleza **evolutiva**: cada semana se integrarán nuevas reglas de negocio publicadas por el equipo docente (*Sprints*), por lo que el código debe mantenerse **modular y ordenado** desde el inicio.

---

## 🗂️ Estructura del proyecto

```text
network-os/
├── src/
│   └── network_os/
│       ├── main.py                 ← punto de entrada, menú interactivo
│       └── logic/
│           ├── controller/
│           │   ├── auditoria_servidor.py
│           │   └── gestor_archivos.py
│           ├── model/
│           │   ├── nodo_hash/
│           │   │   └── nodo_hash.py
│           │   └── registro_auditoria/
│           │       └── registro_auditoria.py
│           └── structure/
│               ├── carpeta/
│               │   └── carpeta.py
│               ├── hash_table/
│               │   └── hash_map.py
│               └── persistencia_auditoria/
│                   └── persistencia_auditoria_csv.py
├── tests/
│   ├── test_auditoria.py
│   ├── test_gestor_archivos.py
│   └── test_hash_map.py
├── logs/                           ← aquí se genera network_audit_log.csv
├── .gitignore
└── README.md
```
