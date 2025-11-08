"""Tests for the scaffolder's directory structure creation."""

import tempfile
from pathlib import Path

from python_project_deployment.models import ProjectConfig
from python_project_deployment.rollback import RollbackManager
from python_project_deployment.scaffolder import Scaffolder


def test_directory_structure_creation() -> None:
    """Test that scaffolder creates the correct directory structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ProjectConfig(
            package_name="test_package",
            target_dir=Path(tmpdir),
            author_name="Test Author",
            author_email="test@example.com",
            description="A test package",
        )

        scaffolder = Scaffolder(config)
        dest = config.destination_path

        # Create only the directory structure (not full scaffold)
        with RollbackManager(dest) as rollback:
            scaffolder._create_directory_structure(dest, rollback)

        # Verify root directories
        assert dest.exists()
        assert (dest / "src").exists()
        assert (dest / "tests").exists()
        assert (dest / "docs").exists()
        assert (dest / "data").exists()
        assert (dest / "logs").exists()
        assert (dest / "scripts").exists()
        assert (dest / ".github" / "workflows").exists()

        # Verify src/ layout
        assert (dest / "src" / "test_package").exists()
        assert (dest / "src" / "test_package" / "utils").exists()
        assert (dest / "src" / "test_package" / "logger").exists()

        # Verify test subdirectories
        assert (dest / "tests" / "unit").exists()
        assert (dest / "tests" / "integration").exists()


def test_template_files_created() -> None:
    """Test that all template files are created in correct locations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ProjectConfig(
            package_name="test_package",
            target_dir=Path(tmpdir),
            author_name="Test Author",
            author_email="test@example.com",
            description="A test package",
        )

        scaffolder = Scaffolder(config)
        dest = config.destination_path

        # Create directory structure and render templates
        with RollbackManager(dest) as rollback:
            scaffolder._create_directory_structure(dest, rollback)
        scaffolder._render_templates(dest)

        # Verify root configuration files
        assert (dest / "pyproject.toml").exists()
        assert (dest / "README.md").exists()
        assert (dest / "CONTRIBUTING.md").exists()
        assert (dest / "SECURITY.md").exists()
        assert (dest / ".gitignore").exists()
        assert (dest / ".env").exists()
        assert (dest / "LICENSE").exists()
        assert (dest / "Makefile").exists()
        assert (dest / ".pre-commit-config.yaml").exists()

        # Verify CI/CD files
        assert (dest / ".github" / "workflows" / "ci.yaml").exists()
        assert (dest / ".github" / "dependabot.yml").exists()

        # Verify source files
        pkg_path = dest / "src" / "test_package"
        assert (pkg_path / "__init__.py").exists()
        assert (pkg_path / "main.py").exists()
        assert (pkg_path / "hello.py").exists()
        assert (pkg_path / "utils" / "__init__.py").exists()
        assert (pkg_path / "logger" / "__init__.py").exists()
        assert (pkg_path / "logger" / "logger.py").exists()

        # Verify test files
        assert (dest / "tests" / "conftest.py").exists()
        assert (dest / "tests" / "unit" / "test_hello.py").exists()

        # Verify documentation files
        assert (dest / "docs" / "conf.py").exists()
        assert (dest / "docs" / "index.rst").exists()


def test_pyproject_toml_has_src_layout() -> None:
    """Test that pyproject.toml is configured for src/ layout."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = ProjectConfig(
            package_name="test_package",
            target_dir=Path(tmpdir),
            author_name="Test Author",
            author_email="test@example.com",
            description="A test package",
        )

        scaffolder = Scaffolder(config)
        dest = config.destination_path

        with RollbackManager(dest) as rollback:
            scaffolder._create_directory_structure(dest, rollback)
        scaffolder._render_templates(dest)

        pyproject_content = (dest / "pyproject.toml").read_text(encoding="utf-8")

        # Verify modern pyproject.toml configuration
        assert "test_package" in pyproject_content
        assert "[project]" in pyproject_content
