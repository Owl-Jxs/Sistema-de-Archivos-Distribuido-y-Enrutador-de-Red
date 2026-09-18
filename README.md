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
- **Registrar toda acción relevante** en un log de auditoría (`network_audit_log.txt`), con fecha, hora y detalle de la transacción.

> El proyecto es de naturaleza **evolutiva**: cada semana se integrarán nuevas reglas de negocio publicadas por el equipo docente (*Sprints*), por lo que el código debe mantenerse **modular y ordenado** desde el inicio.

---

## 🗂️ Estructura del proyecto

```text
network-os/
├── src/
│   └── network_os/
│       ├── __init__.py
│       ├── main.py                 ← punto de entrada, menú interactivo
│       ├── arbol/                  ← sistema de directorios (árbol)
│       │   └── __init__.py
│       ├── hash_table/             ← autenticación (tabla hash propia)
│       │   └── __init__.py
│       ├── grafo/                  ← topología y enrutamiento de red
│       │   └── __init__.py
│       └── auditoria/              ← logging de transacciones
│           └── __init__.py
├── tests/                          ← pruebas sueltas por módulo
├── logs/                           ← aquí se genera network_audit_log.txt
├── .gitignore
└── README.md