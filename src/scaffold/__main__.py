"""Punto de ejecución cuando se invoca el módulo como script (python -m scaffold)."""

import sys
from pathlib import Path

# Garantizar que el directorio raíz y src estén en sys.path
CURRENT_FILE = Path(__file__).resolve()
SRC_DIR = CURRENT_FILE.parent.parent
ROOT_DIR = SRC_DIR.parent

for p in (str(ROOT_DIR), str(SRC_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from src.scaffold.cli import main

if __name__ == "__main__":
    main()
