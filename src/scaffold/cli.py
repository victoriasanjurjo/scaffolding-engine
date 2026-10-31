"""Interfaz de Línea de Comandos (CLI) para md-scaffold.

Procesa argumentos de consola, orquesta el parseo de Markdown y ejecuta
el constructor físico informando el estado y métricas de manera clara y profesional.
"""

import argparse
from pathlib import Path
import sys

from src.scaffold import __version__
from src.scaffold.builder import ScaffoldBuilder, ScaffoldReport
from src.scaffold.parser import ScaffoldParser


def build_argument_parser() -> argparse.ArgumentParser:
    """Configura las opciones y comandos del CLI."""
    parser = argparse.ArgumentParser(
        prog="scaffold",
        description="Generador local de estructuras de proyectos a partir de especificaciones Markdown.",
    )
    parser.add_argument(
        "markdown_file",
        type=str,
        help="Ruta al archivo Markdown (.md) que contiene la especificación.",
    )
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        default=".",
        help="Directorio destino donde se creará la estructura (por defecto: directorio actual).",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Simula la ejecución sin realizar escrituras ni modificaciones en disco.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Sobrescribe archivos preexistentes en lugar de omitirlos.",
    )
    parser.add_argument(
        "--strip-root",
        action="store_true",
        help="Si el árbol tiene una carpeta raíz englobadora (ej. mi-proyecto/), la descarta y crea el contenido directamente en el destino.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Muestra la versión instalada de md-scaffold.",
    )
    return parser


def print_report(report: ScaffoldReport, target_path: Path) -> None:
    """Imprime el resumen de operaciones ejecutadas en la terminal."""
    mode_tag = "[DRY-RUN] " if report.is_dry_run else ""

    print(f"\n{mode_tag}Destino: {target_path}")
    print("-" * 60)

    for d in report.dirs_created:
        print(f"  [DIR]       {mode_tag}{d}/")

    for f in report.files_written:
        print(f"  [INJECTED]  {mode_tag}{f}")

    for f in report.files_empty:
        print(f"  [TOUCH]     {mode_tag}{f}")

    for f in report.files_overwritten:
        print(f"  [OVERWRITE] {mode_tag}{f}")

    for f in report.files_skipped:
        print(f"  [SKIPPED]   {f} (ya existe; utiliza --force para sobrescribir)")

    print("-" * 60)
    print(
        f"{mode_tag}Resumen: {len(report.dirs_created)} carpetas, "
        f"{len(report.files_written)} archivos con código, "
        f"{len(report.files_empty)} archivos vacíos, "
        f"{len(report.files_skipped)} omitidos."
    )


def run_scaffold(args: argparse.Namespace) -> int:
    """Función central de ejecución del proceso de scaffolding."""
    md_path = Path(args.markdown_file)

    if not md_path.exists():
        sys.stderr.write(f"Error: El archivo especificado no existe: {md_path}\n")
        return 1

    if not md_path.is_file():
        sys.stderr.write(f"Error: La ruta proporcionada no es un archivo regular: {md_path}\n")
        return 1

    try:
        content = md_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = md_path.read_text(encoding="latin-1")
        except Exception as ex:
            sys.stderr.write(f"Error: No se pudo leer el archivo Markdown ({ex})\n")
            return 1
    except PermissionError:
        sys.stderr.write(f"Error: Permiso denegado al leer: {md_path}\n")
        return 1

    # 1. Parseo sintáctico
    parser = ScaffoldParser(content)
    tree_entries, file_contents = parser.parse_all(strip_root=args.strip_root)

    if not tree_entries and not file_contents:
        sys.stderr.write(
            f"Advertencia: No se encontraron bloques de árbol (```tree) ni archivos especificados en {md_path.name}.\n"
        )
        return 0

    # 2. Construcción física
    target_dir = Path(args.target).resolve()
    builder = ScaffoldBuilder(target_dir=target_dir)

    try:
        report = builder.build(
            tree_entries=tree_entries,
            file_contents=file_contents,
            dry_run=args.dry_run,
            force=args.force,
        )
    except ValueError as val_err:
        sys.stderr.write(f"Error de Seguridad: {val_err}\n")
        return 1
    except PermissionError as perm_err:
        sys.stderr.write(f"Error de Permisos: No se pudo escribir en el destino ({perm_err})\n")
        return 1
    except Exception as ex:
        sys.stderr.write(f"Error Inesperado: {ex}\n")
        return 1

    print_report(report, target_dir)
    return 0


def main(argv: list[str] = None) -> None:
    """Punto de entrada invocado desde consola."""
    parser = build_argument_parser()
    parsed_args = parser.parse_args(argv)
    exit_code = run_scaffold(parsed_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
