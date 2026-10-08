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
│   ├── main.py                   ← NetworkOS.ejecutar_menu()
│   ├── consola/                  ← menús de consola (MenuConsola)
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

