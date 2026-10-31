"""Módulo de parseo sintáctico para especificaciones Markdown.

Extrae jerarquías de directorios a partir de diagramas de árbol ASCII y mapea
el contenido exacto de los archivos definidos en bloques de código cercados.
"""

from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class TreeEntry:
    """Representa una entrada extraída del árbol de directorios."""

    path: str
    is_dir: bool


class ScaffoldParser:
    """Analizador léxico y sintáctico de especificaciones Markdown para scaffolding."""

    def __init__(self, content: str):
        # Normalizar saltos de línea a formato Unix (\n) para consistencia en regex
        self.raw_content: str = content.replace("\r\n", "\n")

    def extract_tree_blocks(self) -> list[str]:
        """Localiza y extrae bloques de código etiquetados como tree, text, ascii o sin etiqueta."""
        patterns = [
            r"```(?:tree|text|ascii)\n([\s\S]*?)```",
            r"```\n([\s\S]*?)```",
        ]
        blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, self.raw_content, flags=re.MULTILINE)
            for match in matches:
                # Comprobar si el bloque contiene caracteres típicos de árbol ASCII
                if any(char in match for char in ("├──", "└──", "│", "+--", "\\--")):
                    blocks.append(match)
        return blocks

    def parse_tree_lines(self, tree_text: str, strip_root: bool = False) -> list[TreeEntry]:
        """Procesa un texto de árbol ASCII y construye las rutas relativas normalizadas.
        
        Soporta comentarios en línea (iniciados con #) y calcula la profundidad
        para resolver anidamientos sin depender de una cantidad fija de espacios.
        """
        raw_lines = [line.rstrip() for line in tree_text.strip().splitlines() if line.strip()]
        if not raw_lines:
            return []

        parsed_items: list[dict] = []
        stack: list[tuple[int, str]] = []  # Tuplas de (profundidad, nombre_carpeta)

        for line in raw_lines:
            # 1. Ignorar comentarios en línea que explican la función del archivo/carpeta
            clean_line = re.split(r"\s+#", line, maxsplit=1)[0].rstrip()
            if not clean_line:
                continue

            # 2. Localizar el nombre del nodo eliminando conectores de árbol
            # Coincide con caracteres alfanuméricos, guiones, puntos y barra final opcional
            match = re.search(r"([a-zA-Z0-9_\-\.\/]+/?)$", clean_line)
            if not match:
                continue

            entry_name = match.group(1).strip()
            if not entry_name or entry_name in (".", ".."):
                continue

            # La profundidad se calcula por el índice donde comienza el nombre en la línea
            depth = clean_line.find(entry_name)

            # Desapilar directorios con mayor o igual profundidad
            while stack and stack[-1][0] >= depth:
                stack.pop()

            parent_path = "/".join(item[1] for item in stack)
            is_explicit_dir = entry_name.endswith("/")
            clean_name = entry_name.rstrip("/")

            relative_path = f"{parent_path}/{clean_name}".strip("/") if parent_path else clean_name

            parsed_items.append({
                "path": relative_path,
                "clean_name": clean_name,
                "depth": depth,
                "is_explicit_dir": is_explicit_dir,
            })

            # Si es carpeta explícita, se apila para sus hijos
            if is_explicit_dir:
                stack.append((depth, clean_name))

        if not parsed_items:
            return []

        # Determinar si un elemento sin / es carpeta si el siguiente elemento es un hijo
        results: list[TreeEntry] = []
        total = len(parsed_items)

        # Detectar si hay una única carpeta raíz englobadora (ej. "mi-proyecto")
        first_item = parsed_items[0]
        has_single_root = total > 1 and first_item["depth"] == 0 and (
            first_item["is_explicit_dir"] or not ("." in first_item["clean_name"])
        )
        root_prefix = f"{first_item['clean_name']}/" if (has_single_root and strip_root) else ""

        for idx, item in enumerate(parsed_items):
            is_dir = item["is_explicit_dir"]
            # Si no tiene barra explícita pero el siguiente elemento tiene mayor profundidad, es directorio
            if not is_dir and idx + 1 < total:
                if parsed_items[idx + 1]["depth"] > item["depth"]:
                    is_dir = True

            path_str = item["path"]
            if strip_root and has_single_root:
                if path_str == first_item["clean_name"]:
                    # Omitir la carpeta raíz contenedora
                    continue
                if path_str.startswith(root_prefix):
                    path_str = path_str[len(root_prefix):]

            results.append(TreeEntry(path=path_str, is_dir=is_dir))

        return results

    def parse_file_contents(self) -> dict[str, str]:
        """Detecta bloques de contenido asociados a rutas de archivo.
        
        Patrón reconocido:
        ### `ruta/al/archivo.ext`
        ```lenguaje
        contenido
        ```
        """
        pattern = r"#{2,4}\s+[`\"']?([^`\"'\n\r]+?)[`\"']?\s*\n+```[^\n]*\n([\s\S]*?)```"
        matches = re.findall(pattern, self.raw_content)
        file_map: dict[str, str] = {}

        for raw_path, content in matches:
            clean_path = raw_path.strip().replace("\\", "/").strip("/")
            file_map[clean_path] = content

        return file_map

    def parse_all(self, strip_root: bool = False) -> tuple[list[TreeEntry], dict[str, str]]:
        """Ejecuta el parseo integral del árbol de directorios y contenidos de archivos."""
        tree_blocks = self.extract_tree_blocks()
        all_entries: list[TreeEntry] = []

        for block in tree_blocks:
            entries = self.parse_tree_lines(block, strip_root=strip_root)
            all_entries.extend(entries)

        file_contents = self.parse_file_contents()
        return all_entries, file_contents
