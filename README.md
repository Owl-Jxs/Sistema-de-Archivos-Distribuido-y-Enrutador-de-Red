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
- **Registrar toda acción relevante** en un archivo CSV de auditoría por servidor (`servidores/<nombre>_<id>/auditoria.csv`), con fecha, hora y detalle de la transacción.

> El proyecto es de naturaleza **evolutiva**: cada semana se integrarán nuevas reglas de negocio publicadas por el equipo docente (*Sprints*), por lo que el código debe mantenerse **modular y ordenado** desde el inicio.

---

## 🗂️ Estructura del proyecto

```text
network-os/
├── src/
│   └── network_os/
│       ├── main.py                 ← punto de entrada, menú interactivo
│       ├── persistencia/
│       │   ├── persistencias_servidorCSV/
│       │   ├── persistencia_auditoria/
│       │   ├── persistencia_carpetas/
│       │   ├── persistencia_red/
│       │   └── persistencia_usuarios/
│       └── logic/
│           ├── controller/
│           │   ├── AuditoriaServidor/
│           │   ├── gestor_archivos/
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
│               ├── grafo_red/
│               ├── hash_table/
│               └── vertice_red/
├── tests/
│   ├── test_archivos.py
│   ├── test_auditoria.py
│   ├── test_gestor_archivos.py
│   ├── test_grafo_red.py
│   ├── test_hash_map.py
│   ├── test_paquete_datos.py
│   ├── test_persistencia_red_csv.py
│   ├── test_persistencia_usuarios_csv.py
│   └── test_servidor.py
├── datos/                           ← datos de ejemplo (archivos.csv)
├── logs/
├── .gitignore
└── README.md
```
