"""md-scaffold: Motor local de scaffolding a partir de especificaciones Markdown.

Parsea estructuras en árbol ASCII e inyecta bloques de código cercados
directamente en el sistema de archivos de forma segura y portable.
"""

__version__ = "1.0.0"
__author__ = "Antigravity Senior Architect"

from src.scaffold.builder import ScaffoldBuilder
from src.scaffold.parser import ScaffoldParser

__all__ = ["ScaffoldParser", "ScaffoldBuilder", "__version__"]
