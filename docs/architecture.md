# Arquitectura Técnica - md-scaffold

Este documento describe la arquitectura modular, el modelo de datos interno y el flujo de ejecución de **md-scaffold**.

---

## 1. Diagrama de Arquitectura y Flujo

```mermaid
graph TD
    A[Archivo Markdown (.md)] --> B[ScaffoldParser]
    B -->|extract_tree_blocks()| C[Bloques Árbol ASCII]
    B -->|parse_tree_lines()| D[List of TreeEntry]
    B -->|parse_file_contents()| E[Map of File Contents]
    D --> F[ScaffoldBuilder]
    E --> F
    F -->|validate_safe_path()| G{Path Traversal?}
    G -->|No| H[File System Operations]
    G -->|Sí| I[ValueError: Security Error]
    H -->|dry_run=True| J[ScaffoldReport: Simulación]
    H -->|dry_run=False| K[Creación en Disco: Dirs, Files, Touches]
    K --> L[Consola CLI: Reporte Formateado]
    J --> L
```

---

## 2. Componentes y Módulos

### 2.1 `src/scaffold/parser.py`
- **`TreeEntry`:** Modelo de datos inmutable (`path: str`, `is_dir: bool`).
- **`ScaffoldParser`:**
  - Extrae bloques cercados con identificadores `tree`, `text`, `ascii` o sin lenguaje.
  - Normaliza caracteres de retorno de carro (`\r\n` a `\n`).
  - Procesa jerarquías basadas en profundidad y caracteres conectores (`├──`, `└──`, `│`).
  - Remueve comentarios explicativos en línea iniciados con `#`.
  - Mapea encabezados `### `ruta/al/archivo`` con sus bloques de código correspondientes.

### 2.2 `src/scaffold/builder.py`
- **`ScaffoldBuilder`:**
  - `validate_safe_path()`: Valida que ninguna ruta intente escapar de `target_dir` mediante secuencias `..`.
  - Crea carpetas intermedias (`parents=True, exist_ok=True`).
  - Inyecta código en archivos definidos.
  - Genera archivos vacíos para entradas del árbol sin bloque asociado.
  - Administra banderas `--dry-run` y `--force`.
- **`ScaffoldReport`:** Estructura que acumula métricas de directorios y archivos creados, escritos, vacíos, omitidos y sobrescritos.

### 2.3 `src/scaffold/cli.py`
- Configuración de argumentos mediante `argparse`.
- Captura limpia de excepciones (`FileNotFoundError`, `PermissionError`, `ValueError`) evitando tracebacks no controlados.
- Formateo de salida visual claro en consola.
