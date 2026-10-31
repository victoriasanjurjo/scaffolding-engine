# md-scaffold

**md-scaffold** es un motor de scaffolding local y CLI en Python que lee archivos Markdown con especificaciones de proyectos y genera automáticamente la estructura física de carpetas y archivos en disco, inyectando código y renderizando plantillas con **Jinja2**.

---

## 🚀 Características Principales

- **Renderizado Dinámico con Jinja2:** Resuelve variables globales (`{{ project_name }}`) y estructuras lógicas/condicionales (`{% if ... %}`, `{% for ... %}`) tanto en las rutas del árbol como en el contenido de cada archivo.
- **Variables Globales en Markdown:** Permite declarar variables al inicio del archivo mediante **YAML frontmatter** (`---`) o bloques cercados ```` ```yaml ````.
- **Inyección de Variables por CLI:** Parsea banderas `--var clave=valor` (o `-V`), permitiendo parametrizar la generación desde la línea de comandos con conversión automática de tipos (`true`, `false`, enteros, flotantes).
- **Parseo de Árboles ASCII:** Reconoce diagramas en ```` ```tree ````, ```` ```text ```` o ```` ```ascii ```` con caracteres conectores (`├──`, `└──`, `│`), resolviendo la profundidad automáticamente y descartando comentarios explicativos (`#`).
- **Condicionales en el Árbol:** Soporta condicionales Jinja2 dentro del propio árbol para incluir o excluir carpetas/archivos de forma dinámica según las variables activas.
- **Creación de Archivos Vacíos:** Si una entrada en el árbol no cuenta con un bloque de código explícito, se genera como archivo vacío (`touch`), ideal para `__init__.py`, `.gitkeep`, etc.
- **Prevención de Path Traversal:** Valida rigurosamente cada ruta relativa para evitar que secuencias maliciosas (`../`) intenten escribir fuera del directorio destino.
- **Modo Simulación (`--dry-run`):** Inspecciona y audita en consola qué carpetas y archivos se crearían o modificarían sin alterar el disco.
- **Control de Sobrescritura (`--force`):** Por defecto preserva archivos existentes para evitar pérdida accidental de datos, ofreciendo sobrescritura forzada bajo demanda.
- **Desempaquetado Raíz (`--strip-root`):** Permite omitir la carpeta contenedora inicial (ej. `mi-proyecto/`) y generar el contenido directamente en la carpeta destino.

---

## 📋 Sintaxis Markdown y Plantillas Jinja2

### 1. Variables Globales (YAML Frontmatter o Bloques YAML)

```markdown
---
project_name: auth_api
author: Victoria
include_docker: true
port: 8000
---
```

O alternativamente mediante un bloque cercado:

````markdown
```yaml
project_name: auth_api
include_docker: true
```
````

### 2. Árbol de Directorios Dinámico con Condicionales

````markdown
```tree
{{ project_name }}/
├── src/
│   ├── __init__.py
│   └── app.py
{% if include_docker %}
├── Dockerfile
├── docker-compose.yml
{% endif %}
├── README.md
└── requirements.txt
```
````

### 3. Bloques de Contenido con Variables y Lógica Jinja2

````markdown
### `src/app.py`

```python
\"\"\"Servicio principal para {{ project_name }}.\"\"\"

PORT = {{ port }}

{% if include_docker %}
IS_CONTAINERIZED = True
{% else %}
IS_CONTAINERIZED = False
{% endif %}
```

### `Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
EXPOSE {{ port }}
CMD ["python", "src/app.py"]
```
````

---

## 🛠 Instalación y Requisitos

### Requisitos
- **Python 3.10** o superior.
- Dependencias: `jinja2`, `pyyaml`.

### Instalación local en modo editable

```powershell
# Clonar o ubicarse en el directorio
cd "d:\Proyectos\Nueva carpeta"

# Instalar en modo editable
pip install -e .
```

---

## 💻 Uso de la Línea de Comandos (CLI)

Una vez instalado, utiliza el comando `scaffold` o ejecútalo directamente vía Python:

```powershell
# 1. Simulación previa con Jinja2 (no escribe en disco)
scaffold proyecto.md --dry-run

# 2. Inyección de variables por CLI (sobrescriben las del Markdown)
scaffold proyecto.md --var project_name=mi_servicio --var include_docker=false

# 3. Generación en un directorio destino específico
scaffold proyecto.md --target ./salida/

# 4. Sobrescribir archivos preexistentes
scaffold proyecto.md --force

# 5. Descartar la carpeta raíz contenedora inicial
scaffold proyecto.md --strip-root --target .
```

### Comandos equivalentes vía módulo Python:

```powershell
# Ejecución vía módulo
python -m src.scaffold proyecto.md --dry-run --var env=production

# Ejecución vía script raíz
python main.py proyecto.md --dry-run
```

---

## 🧪 Ejecución de Pruebas Unitarias

El proyecto incluye 17 pruebas unitarias con **pytest**:

```powershell
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar la suite completa
pytest -v
```

---

## 📂 Estructura del Repositorio

```text
md-scaffold/
├── src/
│   └── scaffold/
│       ├── __init__.py       # Versión y exportaciones públicas
│       ├── __main__.py       # Soporte para python -m scaffold
│       ├── parser.py         # Analizador sintáctico de árboles ASCII y Markdown
│       ├── templating.py     # Motor Jinja2, extracción YAML y parsing de variables CLI
│       ├── builder.py        # Constructor físico en disco y prevención de Path Traversal
│       └── cli.py            # Interfaz de comandos con soporte --var y control de errores
├── tests/
│   ├── __init__.py
│   ├── test_parser.py        # Pruebas unitarias del parser sintáctico
│   ├── test_builder.py       # Pruebas del builder y validaciones de seguridad
│   └── test_templating.py    # Pruebas de Jinja2, variables YAML, CLI y condicionales
├── docs/
│   ├── architecture.md       # Diagrama de flujo y arquitectura técnica
│   └── decisions.md          # Registro de Decisiones de Arquitectura (ADR)
├── .gitignore                # Reglas de exclusión para Git
├── pyproject.toml            # Definición estándar de empaquetado pip con jinja2 y pyyaml
├── README.md                 # Documentación técnica completa
└── requirements.txt          # Manifiesto de dependencias instaladas
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la [Licencia MIT](LICENSE.txt).
