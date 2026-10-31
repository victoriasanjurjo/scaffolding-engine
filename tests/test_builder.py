"""Pruebas unitarias para el constructor físico de archivos (ScaffoldBuilder)."""

from pathlib import Path
import pytest

from src.scaffold.builder import ScaffoldBuilder
from src.scaffold.parser import TreeEntry


def test_builder_creates_dirs_and_files(tmp_path: Path):
    """Verifica que el builder cree directorios y archivos vacíos o con contenido."""
    builder = ScaffoldBuilder(target_dir=tmp_path)

    entries = [
        TreeEntry(path="src", is_dir=True),
        TreeEntry(path="src/core", is_dir=True),
        TreeEntry(path="src/core/__init__.py", is_dir=False),
        TreeEntry(path="README.md", is_dir=False),
    ]

    contents = {
        "README.md": "# Proyecto Generado\nDescripción del proyecto.\n",
    }

    report = builder.build(entries, contents, dry_run=False, force=False)

    assert (tmp_path / "src").is_dir()
    assert (tmp_path / "src" / "core").is_dir()
    assert (tmp_path / "src" / "core" / "__init__.py").is_file()
    assert (tmp_path / "README.md").is_file()
    assert "# Proyecto Generado" in (tmp_path / "README.md").read_text(encoding="utf-8")

    assert "src" in report.dirs_created
    assert "README.md" in report.files_written
    assert "src/core/__init__.py" in report.files_empty


def test_builder_dry_run_does_not_modify_disk(tmp_path: Path):
    """Comprueba que el modo dry-run no escriba ninguna carpeta ni archivo."""
    builder = ScaffoldBuilder(target_dir=tmp_path)

    entries = [
        TreeEntry(path="new_dir", is_dir=True),
        TreeEntry(path="new_dir/file.txt", is_dir=False),
    ]
    contents = {
        "new_dir/file.txt": "Contenido simulado",
    }

    report = builder.build(entries, contents, dry_run=True, force=False)

    assert report.is_dry_run is True
    assert not (tmp_path / "new_dir").exists()
    assert not (tmp_path / "new_dir" / "file.txt").exists()
    assert "new_dir" in report.dirs_created
    assert "new_dir/file.txt" in report.files_written


def test_builder_force_and_skip_logic(tmp_path: Path):
    """Valida la omisión de archivos existentes y la sobrescritura con force=True."""
    builder = ScaffoldBuilder(target_dir=tmp_path)

    # Crear archivo previo
    target_file = tmp_path / "config.ini"
    target_file.write_text("VERSION=1", encoding="utf-8")

    entries = [TreeEntry(path="config.ini", is_dir=False)]
    contents = {"config.ini": "VERSION=2"}

    # 1. Sin force -> omitir
    report_skip = builder.build(entries, contents, dry_run=False, force=False)
    assert "config.ini" in report_skip.files_skipped
    assert target_file.read_text(encoding="utf-8") == "VERSION=1"

    # 2. Con force -> sobrescribir
    report_force = builder.build(entries, contents, dry_run=False, force=True)
    assert "config.ini" in report_force.files_overwritten
    assert target_file.read_text(encoding="utf-8") == "VERSION=2"


def test_builder_prevents_path_traversal(tmp_path: Path):
    """Comprueba que se rechacen rutas maliciosas con '..' fuera del directorio base."""
    builder = ScaffoldBuilder(target_dir=tmp_path)

    with pytest.raises(ValueError, match="Violación de seguridad"):
        builder.validate_safe_path("../../etc/passwd")

    with pytest.raises(ValueError, match="Violación de seguridad"):
        builder.validate_safe_path("src/../../evil.sh")
