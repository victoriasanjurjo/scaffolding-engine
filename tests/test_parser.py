"""Pruebas unitarias para el analizador sintáctico (ScaffoldParser)."""

import pytest

from src.scaffold.parser import ScaffoldParser, TreeEntry


def test_extract_tree_blocks():
    """Valida la extracción de bloques de árbol con etiquetas tree, text y genéricas."""
    content = """
# Proyecto de Prueba

```tree
mi-app/
├── src/
│   └── app.py
└── README.md
```

Otro texto informativo.
"""
    parser = ScaffoldParser(content)
    blocks = parser.extract_tree_blocks()
    assert len(blocks) == 1
    assert "mi-app/" in blocks[0]
    assert "├── src/" in blocks[0]


def test_parse_tree_lines_hierarchy():
    """Comprueba la resolución de jerarquías y profundidades en árbol ASCII."""
    tree_text = """
mi-app/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── engine.py
│   └── main.py
├── tests/
│   └── test_engine.py
├── .gitignore
└── README.md
"""
    parser = ScaffoldParser(tree_text)
    entries = parser.parse_tree_lines(tree_text, strip_root=False)

    paths = [e.path for e in entries]
    assert "mi-app" in paths
    assert "mi-app/src" in paths
    assert "mi-app/src/core" in paths
    assert "mi-app/src/core/__init__.py" in paths
    assert "mi-app/src/core/engine.py" in paths
    assert "mi-app/src/main.py" in paths
    assert "mi-app/tests/test_engine.py" in paths
    assert "mi-app/.gitignore" in paths
    assert "mi-app/README.md" in paths

    # Validar tipos (directorios vs archivos)
    entry_dict = {e.path: e.is_dir for e in entries}
    assert entry_dict["mi-app"] is True
    assert entry_dict["mi-app/src"] is True
    assert entry_dict["mi-app/src/core"] is True
    assert entry_dict["mi-app/src/main.py"] is False
    assert entry_dict["mi-app/README.md"] is False


def test_parse_tree_with_comments():
    """Verifica que los comentarios inline con '#' se ignoren limpiamente."""
    tree_text = """
proyecto/
├── docs/       # Documentación técnica y bitácora
├── src/        # Código fuente principal
│   └── cli.py  # Punto de entrada CLI
└── README.md   # Guía de inicio rápido
"""
    parser = ScaffoldParser(tree_text)
    entries = parser.parse_tree_lines(tree_text, strip_root=True)

    paths = [e.path for e in entries]
    assert "docs" in paths
    assert "src" in paths
    assert "src/cli.py" in paths
    assert "README.md" in paths

    # Asegurarse de que el comentario no forme parte del nombre
    for p in paths:
        assert "#" not in p


def test_parse_tree_strip_root():
    """Valida la opción de descartar la carpeta contenedora inicial."""
    tree_text = """
root-folder/
├── config/
│   └── settings.json
└── index.js
"""
    parser = ScaffoldParser(tree_text)
    entries = parser.parse_tree_lines(tree_text, strip_root=True)

    paths = [e.path for e in entries]
    assert "root-folder" not in paths
    assert "config" in paths
    assert "config/settings.json" in paths
    assert "index.js" in paths


def test_parse_file_contents():
    """Comprueba la extracción de bloques de código asociados a rutas de archivo."""
    content = """
### `src/config.py`

```python
import os

DEBUG = True
APP_NAME = "TestApp"
```

### `requirements.txt`

```text
pytest>=8.0
```
"""
    parser = ScaffoldParser(content)
    file_map = parser.parse_file_contents()

    assert "src/config.py" in file_map
    assert "requirements.txt" in file_map
    assert 'APP_NAME = "TestApp"' in file_map["src/config.py"]
    assert "pytest>=8.0" in file_map["requirements.txt"]


def test_parse_all_integration():
    """Prueba la orquestación completa con árbol y archivos."""
    md = """
# Test Full

```tree
demo/
├── src/
│   └── main.py
└── config.env
```

### `src/main.py`
```python
print("Hola Mundo")
```
"""
    parser = ScaffoldParser(md)
    entries, contents = parser.parse_all(strip_root=False)

    assert len(entries) >= 3
    assert "src/main.py" in contents
    assert 'print("Hola Mundo")' in contents["src/main.py"]
