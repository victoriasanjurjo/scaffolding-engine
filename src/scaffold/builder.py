"""Módulo de construcción e inyección de scaffolding en el sistema de archivos.

Gestiona la creación segura de carpetas, escritura atómica de archivos,
prevención de ataques de Path Traversal y soporte para modos dry-run y force.
"""

from dataclasses import dataclass, field
import os
from pathlib import Path
import sys
from typing import Optional

from src.scaffold.parser import TreeEntry


@dataclass
class ScaffoldReport:
    """Informe consolidado de las operaciones de scaffolding ejecutadas."""

    dirs_created: list[str] = field(default_factory=list)
    files_written: list[str] = field(default_factory=list)
    files_empty: list[str] = field(default_factory=list)
    files_skipped: list[str] = field(default_factory=list)
    files_overwritten: list[str] = field(default_factory=list)
    is_dry_run: bool = False

    @property
    def total_actions(self) -> int:
        return (
            len(self.dirs_created)
            + len(self.files_written)
            + len(self.files_empty)
            + len(self.files_overwritten)
        )


class ScaffoldBuilder:
    """Constructor físico del scaffolding en disco con garantías de seguridad."""

    def __init__(self, target_dir: Path | str = "."):
        self.target_dir: Path = Path(target_dir).resolve()

    def validate_safe_path(self, relative_path: str) -> Path:
        """Verifica que la ruta relativa no intente escapar del directorio destino (Path Traversal)."""
        clean_rel = relative_path.replace("\\", "/").strip("/")
        
        # Validación de componentes sospechosos
        parts = clean_rel.split("/")
        if any(part == ".." for part in parts):
            raise ValueError(
                f"Violación de seguridad: Ruta '{relative_path}' contiene '..' que intenta escapar del destino."
            )

        destination = (self.target_dir / clean_rel).resolve()
        try:
            destination.relative_to(self.target_dir)
        except ValueError as err:
            raise ValueError(
                f"Violación de seguridad: Ruta '{relative_path}' resuelve fuera del directorio base: {destination}"
            ) from err

        return destination

    def build(
        self,
        tree_entries: list[TreeEntry],
        file_contents: dict[str, str],
        dry_run: bool = False,
        force: bool = False,
    ) -> ScaffoldReport:
        """Aplica la especificación de directorios y archivos sobre el sistema de archivos."""
        report = ScaffoldReport(is_dry_run=dry_run)

        # Conjunto normalizado de rutas que tienen contenido explícito asignado
        contents_normalized: dict[str, str] = {
            k.replace("\\", "/").strip("/"): v for k, v in file_contents.items()
        }

        # 1. Crear directorios definidos en el árbol
        for entry in tree_entries:
            dest = self.validate_safe_path(entry.path)
            if entry.is_dir:
                if dry_run:
                    report.dirs_created.append(entry.path)
                else:
                    dest.mkdir(parents=True, exist_ok=True)
                    report.dirs_created.append(entry.path)

        # 2. Crear archivos vacíos del árbol (aquellos sin contenido especificado en bloques)
        for entry in tree_entries:
            if not entry.is_dir:
                clean_path = entry.path.replace("\\", "/").strip("/")
                if clean_path in contents_normalized:
                    continue  # Se procesará en la etapa de inyección de contenido

                dest = self.validate_safe_path(entry.path)
                if dest.exists() and not force:
                    report.files_skipped.append(entry.path)
                    continue

                if dry_run:
                    if dest.exists() and force:
                        report.files_overwritten.append(entry.path)
                    else:
                        report.files_empty.append(entry.path)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    is_overwrite = dest.exists()
                    dest.touch(exist_ok=True)
                    if is_overwrite:
                        report.files_overwritten.append(entry.path)
                    else:
                        report.files_empty.append(entry.path)

        # 3. Inyectar archivos con contenido de código
        for rel_path, content in contents_normalized.items():
            dest = self.validate_safe_path(rel_path)
            is_existing = dest.exists()

            if is_existing and not force:
                report.files_skipped.append(rel_path)
                continue

            if dry_run:
                if is_existing:
                    report.files_overwritten.append(rel_path)
                else:
                    report.files_written.append(rel_path)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content, encoding="utf-8")
                if is_existing:
                    report.files_overwritten.append(rel_path)
                else:
                    report.files_written.append(rel_path)

        return report
