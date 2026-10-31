"""md-scaffold: Motor local de scaffolding a partir de especificaciones Markdown con Jinja2.

Parsea estructuras en árbol ASCII, resuelve plantillas Jinja2 e inyecta
bloques de código cercados directamente en el sistema de archivos.
"""

__version__ = "1.1.0"
__author__ = "Antigravity Senior Architect"

from src.scaffold.builder import ScaffoldBuilder, ScaffoldReport
from src.scaffold.parser import ScaffoldParser, TreeEntry
from src.scaffold.templating import ScaffoldTemplateEngine, parse_cli_vars

__all__ = [
    "ScaffoldParser",
    "ScaffoldBuilder",
    "ScaffoldReport",
    "ScaffoldTemplateEngine",
    "TreeEntry",
    "parse_cli_vars",
    "__version__",
]
