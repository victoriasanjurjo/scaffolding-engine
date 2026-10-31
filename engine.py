"""Wrapper de compatibilidad para engine.py delegando en md-scaffold."""

import sys
from pathlib import Path

# Asegurar que src esté en el path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.scaffold.cli import main

if __name__ == "__main__":
    # Si se pasan argumentos con la sintaxis antigua (python engine.py file.md [target]),
    # adaptarlos limpiamente a los flags del CLI moderno
    argv = sys.argv[1:]
    if len(argv) == 2 and not argv[1].startswith("-"):
        argv = [argv[0], "--target", argv[1]]
    main(argv)