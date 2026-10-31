"""Módulo de renderizado de plantillas y extracción de variables con Jinja2 y YAML.

Permite extraer variables globales de frontmatter YAML y bloques ```yaml,
procesar variables inyectadas por CLI (--var clave=valor) y renderizar
dinámicamente rutas de archivo y contenidos de código.
"""

from typing import Any
import jinja2
import yaml


def parse_cli_value(val_str: str) -> Any:
    """Convierte cadenas de texto de argumentos CLI a tipos primitivos Python apropiados."""
    clean = val_str.strip()
    if clean.lower() == "true":
        return True
    if clean.lower() == "false":
        return False
    if clean.lower() in ("none", "null"):
        return None
    try:
        if clean.isdigit() or (clean.startswith("-") and clean[1:].isdigit()):
            return int(clean)
        return float(clean)
    except ValueError:
        return clean


def parse_cli_vars(var_list: list[str] | None) -> dict[str, Any]:
    """Parsea una lista de argumentos tipo ['clave=valor', 'puerto=8080'] en un diccionario."""
    variables: dict[str, Any] = {}
    if not var_list:
        return variables

    for item in var_list:
        if "=" not in item:
            variables[item.strip()] = True
        else:
            k, v = item.split("=", 1)
            variables[k.strip()] = parse_cli_value(v)
    return variables


class ScaffoldTemplateEngine:
    """Motor de renderizado de especificaciones basado en Jinja2."""

    def __init__(self, context: dict[str, Any] | None = None):
        self.context: dict[str, Any] = context or {}
        # Crear un entorno Jinja2 seguro con opciones estándar
        self.env = jinja2.Environment(
            autoescape=False,
            undefined=jinja2.ChainableUndefined,
        )

    @staticmethod
    def extract_yaml_context(markdown_content: str) -> tuple[dict[str, Any], str]:
        """Extrae variables de bloques frontmatter (---) o cercados ```yaml.
        
        Retorna el contexto extraído y el Markdown sin el bloque frontmatter inicial.
        """
        import re

        context: dict[str, Any] = {}
        cleaned_content = markdown_content

        # 1. Frontmatter al inicio del documento (--- ... ---)
        frontmatter_match = re.match(r"^---\s*\n([\s\S]*?)\n---\s*(?:\n|$)", markdown_content)
        if frontmatter_match:
            yaml_text = frontmatter_match.group(1)
            try:
                data = yaml.safe_load(yaml_text)
                if isinstance(data, dict):
                    context.update(data)
            except Exception:
                pass
            cleaned_content = markdown_content[frontmatter_match.end():]

        # 2. Bloques ```yaml o ```yml dentro del texto
        yaml_blocks = re.findall(r"```(?:yaml|yml)\n([\s\S]*?)```", cleaned_content)
        for block in yaml_blocks:
            try:
                data = yaml.safe_load(block)
                if isinstance(data, dict):
                    context.update(data)
            except Exception:
                pass

        return context, cleaned_content

    def render_string(self, template_str: str) -> str:
        """Renderiza una cadena de texto (ruta o contenido) con el contexto activo de Jinja2."""
        if not template_str or ("{{" not in template_str and "{%" not in template_str):
            return template_str

        template = self.env.from_string(template_str)
        return template.render(**self.context)

    def render_tree_entries(self, entries: list) -> list:
        """Renderiza las rutas de las entradas del árbol de directorios."""
        rendered = []
        for entry in entries:
            rendered_path = self.render_string(entry.path).strip()
            if rendered_path:
                from src.scaffold.parser import TreeEntry
                rendered.append(TreeEntry(path=rendered_path, is_dir=entry.is_dir))
        return rendered

    def render_file_contents(self, file_map: dict[str, str]) -> dict[str, str]:
        """Renderiza tanto las rutas (claves) como el contenido (valores) de los archivos."""
        rendered_map: dict[str, str] = {}
        for raw_path, content in file_map.items():
            rendered_path = self.render_string(raw_path).strip()
            if not rendered_path:
                continue
            rendered_content = self.render_string(content)
            rendered_map[rendered_path] = rendered_content
        return rendered_map
