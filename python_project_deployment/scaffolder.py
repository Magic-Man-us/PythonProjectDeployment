"""Core scaffolding logic for creating Python projects."""

import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

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
        self.template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
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
            ("package_init.py.j2", dest / self.config.package_name / "__init__.py"),
            ("hello.py.j2", dest / self.config.package_name / "hello.py"),
            ("test_hello.py.j2", dest / "tests" / "test_hello.py"),
            ("conf.py.j2", dest / "docs" / "conf.py"),
            ("index.rst.j2", dest / "docs" / "index.rst"),
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
        subprocess.run(
            ["git", "init", "-q"],
            cwd=dest,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "add", "."],
            cwd=dest,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "chore: initial scaffold"],
            cwd=dest,
            check=True,
            capture_output=True,
        )

    def _setup_environment(self, dest: Path) -> None:
        """Setup virtual environment and install dependencies.
        
        Args:
            dest: Project directory path
        """
        # Create virtual environment
        subprocess.run(
            ["uv", "venv"],
            cwd=dest,
            check=True,
            capture_output=True,
        )

        # Install package with dev dependencies
        subprocess.run(
            ["uv", "pip", "install", "-e", ".[dev]"],
            cwd=dest,
            check=True,
            capture_output=True,
        )

    def _run_tests(self, dest: Path) -> None:
        """Run pytest with coverage.
        
        Args:
            dest: Project directory path
        """
        subprocess.run(
            [
                "uv",
                "run",
                "pytest",
                f"--cov={self.config.package_name}",
                "--cov-report=term-missing",
            ],
            cwd=dest,
            check=True,
        )

    def _build_docs(self, dest: Path) -> None:
        """Build Sphinx documentation.
        
        Args:
            dest: Project directory path
        """
        subprocess.run(
            [
                "uv",
                "run",
                "sphinx-build",
                "-b",
                "html",
                "docs",
                "docs/_build/html",
            ],
            cwd=dest,
            check=True,
            capture_output=True,
        )
