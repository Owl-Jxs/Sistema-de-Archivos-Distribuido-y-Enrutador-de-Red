import sys
from pathlib import Path

# Permite ejecutar el proyecto sin instalarlo: python run.py
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from network_os.main import NetworkOS

if __name__ == "__main__":
    NetworkOS.ejecutar_menu()
