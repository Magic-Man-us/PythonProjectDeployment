"""Core scaffolding logic for creating Python projects."""

import logging
import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from python_project_deployment.models import ProjectConfig


class Scaffolder:
    """Main scaffolder class for creating Python projects.

    This class handles the entire project scaffolding process:
    1. Creating directory structure
    2. Rendering templates
    3. Initializing git repository
    4. Setting up virtual environment
    5. Installing dependencies
    6. Running tests
    7. Building documentation
    """

    def __init__(self, config: ProjectConfig) -> None:
        """Initialize scaffolder with project configuration.

        Args:
            config: Project configuration with all necessary settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.template_dir = Path(__file__).parent / "templates"

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(default=False),
        )

    def scaffold(self) -> Path:
        """Execute the full scaffolding process.

        Returns:
            Path to the created project directory

        Raises:
            ValueError: If destination already exists
            RuntimeError: If any step in the scaffolding process fails
        """
        dest = self.config.destination_path

        # Create directory structure
        self._create_directory_structure(dest)

        # Render and write templates
        self._render_templates(dest)

        # Initialize git repository
        self._init_git(dest)

        # Setup virtual environment and install dependencies
        self._setup_environment(dest)

        # Run tests
        self._run_tests(dest)

        # Build documentation
        self._build_docs(dest)

        return dest

    def _create_directory_structure(self, dest: Path) -> None:
        """Create the project directory structure.

        Args:
            dest: Destination path for the project
        """
        # Main directories
        dest.mkdir(parents=True, exist_ok=False)
        (dest / self.config.package_name).mkdir()
        (dest / "tests").mkdir()
        (dest / "docs").mkdir()
        (dest / ".github" / "workflows").mkdir(parents=True)

    def _render_templates(self, dest: Path) -> None:
        """Render Jinja2 templates and write to destination.

        Args:
            dest: Destination path for the project
        """
        context = self.config.to_template_context()

        # Template mapping: (template_file, destination_path)
        template_mappings = [
            ("pyproject.toml.j2", dest / "pyproject.toml"),
            ("README.md.j2", dest / "README.md"),
            (".gitignore.j2", dest / ".gitignore"),
            ("LICENSE.j2", dest / "LICENSE"),
            ("ci.yaml.j2", dest / ".github" / "workflows" / "ci.yaml"),
            ("Makefile.j2", dest / "Makefile"),
            ("dependabot.yml.j2", dest / ".github" / "dependabot.yml"),
            ("package_init.py.j2", dest / self.config.package_name / "__init__.py"),
            ("hello.py.j2", dest / self.config.package_name / "hello.py"),
            ("test_hello.py.j2", dest / "tests" / "test_hello.py"),
            ("conf.py.j2", dest / "docs" / "conf.py"),
            ("index.rst.j2", dest / "docs" / "index.rst"),
            (".pre-commit-config.yaml.j2", dest / ".pre-commit-config.yaml"),
        ]

        for template_name, output_path in template_mappings:
            template = self.jinja_env.get_template(template_name)
            rendered = template.render(**context)
            output_path.write_text(rendered, encoding="utf-8")

    def _init_git(self, dest: Path) -> None:
        """Initialize git repository and make initial commit.

        Args:
            dest: Project directory path
        """
        git_path = shutil.which("git")
        if not git_path:
            raise RuntimeError("git not found in PATH; please install git")

        subprocess.run(
            [git_path, "init", "-q"],
            cwd=dest,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [git_path, "add", "."],
            cwd=dest,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [git_path, "commit", "-q", "-m", "chore: initial scaffold"],
            cwd=dest,
            check=True,
            capture_output=True,
        )

    def _setup_environment(self, dest: Path) -> None:
        """Set up the virtual environment and install dependencies.

        Args:
            dest: Project directory path
        """
        # Try to use `uv` if available; otherwise create a venv and install necessary tools
        uv_path = shutil.which("uv")
        venv_dir = dest / ".venv"

        if uv_path:
            # Use uv to create venv and run installs
            self.logger.info("Using uv binary: %s", uv_path)
            subprocess.run([uv_path, "venv"], cwd=dest, check=True, capture_output=True)
            # Use uv sync to install dev extras (preferred over direct pip usage)
            subprocess.run(
                [uv_path, "sync", "--all-extras"],
                cwd=dest,
                check=True,
                capture_output=True,
            )

            # Install and run pre-commit inside the uv-managed venv
            try:
                subprocess.run(
                    [uv_path, "run", "pre-commit", "install"],
                    cwd=dest,
                    check=True,
                    capture_output=True,
                )
                proc = subprocess.run(
                    [uv_path, "run", "pre-commit", "run", "--all-files"],
                    cwd=dest,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if proc.returncode != 0:
                    raise RuntimeError("pre-commit hooks failed:\n" + proc.stdout + proc.stderr)
            except Exception as exc:  # pragma: no cover - best-effort
                msg = "Failed to install/run pre-commit hooks using uv: " + str(exc)
                raise RuntimeError(msg) from exc
        else:
            # No uv: create a standard venv and install uv + pre-commit into it
            try:
                # Create venv
                subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

                pip_bin = venv_dir / "bin" / "pip"

                # Upgrade pip and install uv and pre-commit into the venv
                subprocess.run(
                    [str(pip_bin), "install", "--upgrade", "pip"],
                    check=True,
                )
                subprocess.run(
                    [str(pip_bin), "install", "uv", "pre-commit"],
                    check=True,
                )

                # Install package with dev dependencies using venv pip
                subprocess.run(
                    [str(pip_bin), "install", "-e", ".[dev]"],
                    cwd=dest,
                    check=True,
                )

                # Run pre-commit install and run using the venv's pre-commit binary
                precommit_bin = venv_dir / "bin" / "pre-commit"
                self.logger.info("Using venv pre-commit: %s", precommit_bin)
                subprocess.run(
                    [str(precommit_bin), "install"],
                    cwd=dest,
                    check=True,
                    capture_output=True,
                )
                proc = subprocess.run(
                    [str(precommit_bin), "run", "--all-files"],
                    cwd=dest,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if proc.returncode != 0:
                    raise RuntimeError("pre-commit hooks failed:\n" + proc.stdout + proc.stderr)
            except Exception as exc:  # pragma: no cover - best-effort
                msg = "Failed to create venv/install tools/run pre-commit: " + str(exc)
                raise RuntimeError(msg) from exc

    def _run_tests(self, dest: Path) -> None:
        """Run pytest with coverage.

        Args:
            dest: Project directory path
        """
        uv_path = shutil.which("uv")
        if uv_path:
            cmd = [
                uv_path,
                "run",
                "pytest",
                f"--cov={self.config.package_name}",
                "--cov-report=term-missing",
            ]
            self.logger.info("Running tests via uv: %s", uv_path)
        else:
            python_bin = dest / ".venv" / "bin" / "python"
            if python_bin.exists():
                cmd = [
                    str(python_bin),
                    "-m",
                    "pytest",
                    f"--cov={self.config.package_name}",
                    "--cov-report=term-missing",
                ]
                self.logger.info("Running tests via venv python: %s", python_bin)
            else:
                cmd = [
                    sys.executable,
                    "-m",
                    "pytest",
                    f"--cov={self.config.package_name}",
                    "--cov-report=term-missing",
                ]
                self.logger.info("Running tests via system python: %s", sys.executable)

        subprocess.run(cmd, cwd=dest, check=True)

    def _build_docs(self, dest: Path) -> None:
        """Build Sphinx documentation.

        Args:
            dest: Project directory path
        """
        uv_path = shutil.which("uv")
        if uv_path:
            cmd = [uv_path, "run", "sphinx-build", "-b", "html", "docs", "docs/_build/html"]
            self.logger.info("Building docs via uv: %s", uv_path)
        else:
            python_bin = dest / ".venv" / "bin" / "python"
            if python_bin.exists():
                cmd = [str(python_bin), "-m", "sphinx", "-b", "html", "docs", "docs/_build/html"]
                self.logger.info("Building docs via venv python: %s", python_bin)
            else:
                cmd = [sys.executable, "-m", "sphinx", "-b", "html", "docs", "docs/_build/html"]
                self.logger.info("Building docs via system python: %s", sys.executable)

        subprocess.run(cmd, cwd=dest, check=True, capture_output=True)
