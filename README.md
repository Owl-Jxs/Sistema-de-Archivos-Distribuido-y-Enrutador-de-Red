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

`GrafoRed.enviar_paquete(origen, destino)` actualmente simula el recorrido y muestra
saltos y costo. El menú pide destino y contenido y prepara un `PaqueteDatos`, pero
informa que el contenido no se ha entregado. En `servidor/menu_servidor.py` queda
comentada la integración para cuando el grafo admita `PaqueteDatos` y devuelva
`ResultadoEnvio`. Los algoritmos y la entrega de contenido siguen en sus módulos.

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

