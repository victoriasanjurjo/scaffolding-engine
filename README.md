# md-scaffold

**md-scaffold** es un motor de scaffolding local y CLI en Python que lee archivos Markdown con especificaciones de proyectos y genera automáticamente la estructura física de carpetas y archivos en disco, inyectando el código correspondiente.

Construido utilizando **únicamente la biblioteca estándar de Python** (`pathlib`, `re`, `argparse`, `sys`, `typing`), garantizando ejecución inmediata, portable y sin dependencias pesadas de terceros.

---

## 🚀 Características Principales

- **Parseo de Árboles ASCII:** Reconoce bloques cercados etiquetados como ```` ```tree ````, ```` ```text ```` o ```` ```ascii ```` con caracteres de jerarquía (`├──`, `└──`, `│`). Resuelve la profundidad de anidación automáticamente y descarta comentarios descriptivos en línea (`#`).
- **Inyección Automática de Código:** Extrae bloques de código asociados a rutas de archivo bajo encabezados como `### \`ruta/al/archivo.ext\`` e inyecta su contenido exacto.
- **Creación de Archivos Vacíos:** Si una entrada en el árbol no cuenta con un bloque de código explícito, se genera como archivo vacío (`touch`), ideal para `__init__.py`, `.gitkeep`, etc.
- **Prevención de Path Traversal:** Valida rigurosamente cada ruta relativa para evitar que secuencias maliciosas (`../`) intenten escribir fuera del directorio destino.
- **Modo Simulación (`--dry-run`):** Inspecciona y audita en consola qué carpetas y archivos se crearían o modificarían sin alterar el disco.
- **Control de Sobrescritura (`--force`):** Por defecto preserva archivos existentes para evitar pérdida accidental de datos, ofreciendo sobrescritura forzada bajo demanda.
- **Desempaquetado Raíz (`--strip-root`):** Permite omitir la carpeta contenedora inicial (ej. `mi-proyecto/`) y generar el contenido directamente en la carpeta destino.

---

## 📋 Sintaxis Markdown Reconocida

### 1. Árbol de Directorios

Se define en un bloque cercado con ```` ```tree ````, ```` ```text ```` o similar. Las carpetas deben terminar con `/` y los comentarios se pueden añadir con `#`:

````markdown
```tree
mi-proyecto/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── config.py
│   └── main.py
├── tests/
│   └── test_engine.py
├── .gitignore
├── README.md
└── requirements.txt
```
````

### 2. Bloques de Contenido de Archivo

Se definen utilizando encabezados de nivel 2 a 4 con la ruta relativa del archivo entre acentos graves (o comillas), seguidos inmediatamente por el bloque de código:

````markdown
### `src/config.py`

```python
import os

DEBUG = os.getenv("DEBUG", "True") == "True"
APP_NAME = "EngineScaffold"
```

### `.gitignore`

```text
__pycache__/
*.pyc
.env
.venv/
dist/
build/
```
````

---

## 🛠 Instalación y Requisitos

### Requisitos
- **Python 3.10** o superior.
- Sin dependencias externas para ejecución en producción.

### Instalación local en modo editable

```powershell
# Clonar o ubicarse en el directorio
cd "d:\Proyectos\Nueva carpeta"

# Instalar en modo editable
pip install -e .
```

---

## 💻 Uso de la Línea de Comandos (CLI)

Una vez instalado, puedes utilizar el comando `scaffold` o ejecutarlo directamente mediante Python:

```powershell
# 1. Simulación previa (no escribe en disco)
scaffold proyecto.md --dry-run

# 2. Generación estándar en el directorio actual
scaffold proyecto.md

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
python -m src.scaffold proyecto.md --dry-run

# Ejecución vía script raíz
python main.py proyecto.md --dry-run
```

---

## 🧪 Ejecución de Pruebas Unitarias

El proyecto incluye una suite completa de pruebas unitarias implementadas con **pytest**:

```powershell
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar la suite completa de tests
pytest -v
```

### Cobertura de Pruebas
- **`tests/test_parser.py`:** Validación de extracción de bloques de árbol, resolución de jerarquías multinivel, descarte de comentarios en línea, opción `strip-root` y mapeo de contenidos de código.
- **`tests/test_builder.py`:** Creación física en carpetas temporales (`tmp_path`), validación de inalterabilidad en modo `--dry-run`, política de omisión y sobrescritura (`--force`), y detección de ataques de **Path Traversal**.

---

## 📂 Estructura del Repositorio

```text
md-scaffold/
├── src/
│   └── scaffold/
│       ├── __init__.py       # Versión y exportaciones públicas
│       ├── __main__.py       # Soporte para python -m scaffold
│       ├── parser.py         # Analizador sintáctico de árboles ASCII y código
│       ├── builder.py        # Constructor seguro en disco y reportes
│       └── cli.py            # Interfaz de comandos (argparse) y control de errores
├── tests/
│   ├── __init__.py
│   ├── test_parser.py        # Pruebas unitarias del parser
│   └── test_builder.py       # Pruebas unitarias del builder y seguridad
├── .gitignore                # Reglas de exclusión para Git
├── LICENSE.txt               # Licencia MIT
├── main.py                   # Acceso directo para ejecución raíz
├── pyproject.toml            # Definición estándar de empaquetado pip
├── proyecto.md               # Archivo de especificación de ejemplo
├── README.md                 # Documentación técnica completa
└── requirements.txt          # Dependencias de desarrollo (pytest)
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la [Licencia MIT](LICENSE.txt).
