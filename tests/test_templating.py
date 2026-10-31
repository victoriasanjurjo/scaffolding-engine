"""Pruebas unitarias para la integración del motor de plantillas Jinja2 y YAML."""

from pathlib import Path
import pytest

from src.scaffold.builder import ScaffoldBuilder
from src.scaffold.parser import ScaffoldParser
from src.scaffold.templating import ScaffoldTemplateEngine, parse_cli_vars


def test_parse_cli_vars_types():
    """Valida la conversión automática de cadenas de consola a tipos primitivos."""
    cli_args = [
        "project_name=mi_sistema",
        "use_docker=true",
        "debug_mode=False",
        "port=8080",
        "ratio=3.14",
        "flag_empty",
    ]
    parsed = parse_cli_vars(cli_args)

    assert parsed["project_name"] == "mi_sistema"
    assert parsed["use_docker"] is True
    assert parsed["debug_mode"] is False
    assert parsed["port"] == 8080
    assert parsed["ratio"] == 3.14
    assert parsed["flag_empty"] is True


def test_extract_yaml_frontmatter_and_blocks():
    """Verifica la extracción de variables desde YAML frontmatter y bloques ```yaml."""
    md_with_frontmatter = """---
project_name: alpha_core
version: 2.0
use_db: true
---
# Documento
```yaml
db_port: 5432
```
"""
    context, cleaned = ScaffoldTemplateEngine.extract_yaml_context(md_with_frontmatter)

    assert context["project_name"] == "alpha_core"
    assert context["version"] == 2.0
    assert context["use_db"] is True
    assert context["db_port"] == 5432
    assert "---" not in cleaned


def test_cli_vars_override_markdown_vars():
    """Comprueba que las variables pasadas por CLI sobrescriban las del Markdown."""
    md = """---
app_name: original_name
author: Alice
---
"""
    cli_override = {"app_name": "custom_name"}
    parser = ScaffoldParser(md, extra_context=cli_override)

    assert parser.context["app_name"] == "custom_name"
    assert parser.context["author"] == "Alice"


def test_render_paths_and_content_with_variables():
    """Valida el reemplazo de {{ variable }} tanto en rutas como en bloques de código."""
    md = """---
pkg: auth_service
class_name: AuthManager
---
```tree
{{ pkg }}/
├── src/
│   └── {{ pkg }}_core.py
└── README.md
```

### `src/{{ pkg }}_core.py`
```python
class {{ class_name }}:
    \"\"\"Gestor de autenticación para {{ pkg }}.\"\"\"
    pass
```
"""
    parser = ScaffoldParser(md)
    entries, contents = parser.parse_all()

    entry_paths = [e.path for e in entries]
    assert "auth_service" in entry_paths
    assert "auth_service/src/auth_service_core.py" in entry_paths

    assert "src/auth_service_core.py" in contents
    assert "class AuthManager:" in contents["src/auth_service_core.py"]
    assert "Gestor de autenticación para auth_service." in contents["src/auth_service_core.py"]


def test_render_conditionals_in_content():
    """Verifica la evaluación de estructuras condicionales {% if %} en el código."""
    md = """---
enable_telemetry: true
enable_cache: false
---
### `config.py`
```python
TELEMETRY = {{ enable_telemetry }}
{% if enable_telemetry %}
def send_metric():
    pass
{% endif %}

{% if enable_cache %}
CACHE_ENABLED = True
{% else %}
CACHE_ENABLED = False
{% endif %}
```
"""
    parser = ScaffoldParser(md)
    _, contents = parser.parse_all()

    config_code = contents["config.py"]
    assert "TELEMETRY = True" in config_code
    assert "def send_metric():" in config_code
    assert "CACHE_ENABLED = False" in config_code
    assert "CACHE_ENABLED = True" not in config_code


def test_render_conditionals_in_tree_structure():
    """Verifica que condicionales Jinja2 en el bloque ```tree incluyan o excluyan ramas."""
    md = """---
include_docker: true
include_docs: false
---
```tree
app/
├── src/
│   └── main.py
{% if include_docker %}
├── Dockerfile
{% endif %}
{% if include_docs %}
├── docs/
│   └── index.md
{% endif %}
└── README.md
```
"""
    parser = ScaffoldParser(md)
    entries, _ = parser.parse_all()

    paths = [e.path for e in entries]
    assert "app/src/main.py" in paths
    assert "app/Dockerfile" in paths
    assert "app/docs" not in paths
    assert "app/docs/index.md" not in paths


def test_end_to_end_builder_with_jinja(tmp_path: Path):
    """Comprueba la creación física en disco de archivos con rutas y código renderizado."""
    md = """
```tree
{{ module_name }}/
└── {{ module_name }}.py
```

### `{{ module_name }}/{{ module_name }}.py`
```python
# Módulo generado para {{ module_name }}
{% for item in features %}
FEATURE_{{ item.upper() }} = True
{% endfor %}
```
"""
    context = {
        "module_name": "payments",
        "features": ["stripe", "paypal"],
    }

    parser = ScaffoldParser(md, extra_context=context)
    entries, contents = parser.parse_all()

    builder = ScaffoldBuilder(target_dir=tmp_path)
    report = builder.build(entries, contents)

    created_file = tmp_path / "payments" / "payments.py"
    assert created_file.is_file()

    code = created_file.read_text(encoding="utf-8")
    assert "# Módulo generado para payments" in code
    assert "FEATURE_STRIPE = True" in code
    assert "FEATURE_PAYPAL = True" in code
    assert "payments/payments.py" in report.files_written
