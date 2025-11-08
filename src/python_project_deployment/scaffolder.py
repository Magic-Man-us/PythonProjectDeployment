"""Core scaffolding logic for creating Python projects."""

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from python_project_deployment.config import ScaffolderSettings
from python_project_deployment.directory_structure import DirectoryStructure
from python_project_deployment.exceptions import PrerequisiteError, SecurityError
from python_project_deployment.logger import get_logger
from python_project_deployment.models import ProjectConfig
from python_project_deployment.rollback import RollbackManager
from python_project_deployment.security import set_secure_permissions, validate_path_traversal
from python_project_deployment.subprocess_runner import SubprocessRunner


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

    def __init__(
        self,
        config: ProjectConfig,
        settings: ScaffolderSettings | None = None,
    ) -> None:
        """Initialize scaffolder with project configuration.

        Args:
            config: Project configuration with all necessary settings
            settings: Optional scaffolder settings for timeouts, security, etc.
        """
        self.config = config
        self.settings = settings or ScaffolderSettings()
        self.logger = get_logger(__name__)
        self.subprocess_runner = SubprocessRunner()
        self.directory_structure = DirectoryStructure()
        self.template_dir = Path(__file__).parent / "templates"

        # Validate template directory
        if not self.template_dir.exists():
            raise PrerequisiteError(
                f"Template directory not found: {self.template_dir}",
                context={"template_dir": str(self.template_dir)},
            )

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(default=False),
        )

    def scaffold(self) -> Path:
        """Execute the full scaffolding process with rollback on failure.

        Returns:
            Path to the created project directory

        Raises:
            Various exceptions from operations, with automatic rollback
        """
        dest = self.config.destination_path
        self.logger.info(f"Starting scaffolding for {self.config.package_name} at {dest}")

        # Validate prerequisites before starting
        self._validate_prerequisites()

        # If dry-run mode, just show what would be done
        if self.settings.dry_run:
            self._print_dry_run_preview(dest)
            return dest

        # Use rollback manager for atomic operation
        with RollbackManager(dest) as rollback:
            # Create directory structure
            self._create_directory_structure(dest, rollback)

            # Render and write templates
            self._render_templates(dest)

            # Initialize git repository
            self._init_git(dest, rollback)

            # Setup virtual environment and install dependencies
            self._setup_environment(dest)

            # Run tests
            self._run_tests(dest)

            # Build documentation
            self._build_docs(dest)

        self.logger.info(f"Successfully scaffolded project at {dest}")
        return dest

    def _validate_prerequisites(self) -> None:
        """Validate that required tools are available.

        Raises:
            PrerequisiteError: If required tools are missing
        """
        self.logger.debug("Validating prerequisites")

        # Check for git
        git_path = shutil.which("git")
        if not git_path:
            raise PrerequisiteError(
                "git not found in PATH. Please install git to continue.",
                context={"required_tool": "git"},
            )

        self.logger.debug(f"Found git at {git_path}")

    def _create_directory_structure(self, dest: Path, rollback: RollbackManager) -> None:
        """Create the project directory structure with rollback support.

        Args:
            dest: Destination path for the project
            rollback: Rollback manager for cleanup on failure
        """
        self.logger.info("Creating directory structure")

        # Validate destination path
        try:
            validate_path_traversal(dest, self.config.target_dir)
        except SecurityError as e:
            raise SecurityError(
                f"Invalid destination path: {dest}",
                context={"dest": str(dest), "target_dir": str(self.config.target_dir)},
            ) from e

        # Main directory
        dest.mkdir(parents=True, exist_ok=False)
        rollback.register_directory_removal(dest)
        set_secure_permissions(dest, is_directory=True)

        # Use DirectoryStructure model to create all directories
        self.directory_structure.create_all(
            root=dest,
            package_name=self.config.package_name,
            set_permissions_fn=set_secure_permissions,
        )

        self.logger.debug("Directory structure created successfully")

    def _render_templates(self, dest: Path) -> None:
        """Render Jinja2 templates and write to destination.

        Args:
            dest: Destination path for the project
        """
        self.logger.info("Rendering templates")
        context = self.config.to_template_context()

        # Template mapping: (template_file, destination_path)
        pkg_path = dest / "src" / self.config.package_name
        template_mappings = [
            # Root configuration files
            ("pyproject.toml.j2", dest / "pyproject.toml"),
            ("README.md.j2", dest / "README.md"),
            ("CHANGELOG.md.j2", dest / "CHANGELOG.md"),
            ("CONTRIBUTING.md.j2", dest / "CONTRIBUTING.md"),
            ("SECURITY.md.j2", dest / "SECURITY.md"),
            (".gitignore.j2", dest / ".gitignore"),
            (".env.j2", dest / ".env"),
            ("LICENSE.j2", dest / "LICENSE"),
            ("Makefile.j2", dest / "Makefile"),
            ("pre-commit-config.yaml.j2", dest / ".pre-commit-config.yaml"),
            # CI/CD
            ("ci.yaml.j2", dest / ".github" / "workflows" / "ci.yaml"),
            ("publish.yaml.j2", dest / ".github" / "workflows" / "publish.yaml"),
            ("docs.yaml.j2", dest / ".github" / "workflows" / "docs.yaml"),
            ("dependabot.yml.j2", dest / ".github" / "dependabot.yml"),
            # Issue and PR templates
            ("bug_report.yml.j2", dest / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"),
            ("feature_request.yml.j2", dest / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"),
            ("issue_config.yml.j2", dest / ".github" / "ISSUE_TEMPLATE" / "config.yml"),
            ("pull_request_template.md.j2", dest / ".github" / "pull_request_template.md"),
            # Source package structure
            ("package_init.py.j2", pkg_path / "__init__.py"),
            ("main.py.j2", pkg_path / "main.py"),
            ("hello.py.j2", pkg_path / "hello.py"),
            ("py.typed.j2", pkg_path / "py.typed"),
            ("utils_init.py.j2", pkg_path / "utils" / "__init__.py"),
            ("logger_init.py.j2", pkg_path / "logger" / "__init__.py"),
            ("logger.py.j2", pkg_path / "logger" / "logger.py"),
            # Tests
            ("conftest.py.j2", dest / "tests" / "conftest.py"),
            ("test_hello.py.j2", dest / "tests" / "unit" / "test_hello.py"),
            # Scripts
            ("security_bandit_check.py.j2", dest / "scripts" / "security_bandit_check.py"),
            ("security_safety_check.py.j2", dest / "scripts" / "security_safety_check.py"),
            # Documentation
            ("conf.py.j2", dest / "docs" / "conf.py"),
            ("index.rst.j2", dest / "docs" / "index.rst"),
            ("quickstart.rst.j2", dest / "docs" / "quickstart.rst"),
            ("development.rst.j2", dest / "docs" / "development.rst"),
            ("security.rst.j2", dest / "docs" / "security.rst"),
        ]

        for template_name, output_path in template_mappings:
            template = self.jinja_env.get_template(template_name)
            rendered = template.render(**context)
            output_path.write_text(rendered, encoding="utf-8")
            set_secure_permissions(output_path, is_directory=False)

        self.logger.debug(f"Rendered {len(template_mappings)} templates")

    def _init_git(self, dest: Path, rollback: RollbackManager) -> None:
        """Initialize git repository and make initial commit.

        Args:
            dest: Project directory path
            rollback: Rollback manager for cleanup
        """
        self.logger.info("Initializing git repository")
        timeout = self.settings.get_timeout_for_operation("git")

        # Initialize git
        self.subprocess_runner.run_command(
            command=["git", "init", "-q"],
            cwd=dest,
            timeout=timeout,
        )
        rollback.register_git_cleanup(dest)

        # Add all files
        self.subprocess_runner.run_command(
            command=["git", "add", "."],
            cwd=dest,
            timeout=timeout,
        )

        # Initial commit
        self.subprocess_runner.run_command(
            command=["git", "commit", "-q", "-m", "chore: initial scaffold"],
            cwd=dest,
            timeout=timeout,
        )

        self.logger.debug("Git repository initialized")

    def _setup_environment(self, dest: Path) -> None:
        """Set up the virtual environment and install dependencies.

        Args:
            dest: Project directory path
        """
        self.logger.info("Setting up environment")
        uv_path = shutil.which("uv")
        timeout = self.settings.get_timeout_for_operation("install")

        if uv_path:
            self.logger.debug(f"Using uv at {uv_path}")
            # Create venv
            self.subprocess_runner.run_command(
                command=["uv", "venv"],
                cwd=dest,
                timeout=timeout,
            )

            # Sync dependencies
            self.subprocess_runner.run_command(
                command=["uv", "sync", "--all-extras"],
                cwd=dest,
                timeout=timeout,
            )

            # Install pre-commit
            self.subprocess_runner.run_command(
                command=["uv", "run", "pre-commit", "install"],
                cwd=dest,
                timeout=timeout,
            )

            # Run pre-commit
            self.subprocess_runner.run_command(
                command=["uv", "run", "pre-commit", "run", "--all-files"],
                cwd=dest,
                timeout=timeout,
                check=False,  # Pre-commit may fail on first run
            )
        else:
            self.logger.warning("uv not found, using pip instead")
            raise PrerequisiteError(
                "uv not found in PATH. Please install uv for optimal experience.",
                context={"recommended_tool": "uv"},
            )

        self.logger.debug("Environment setup complete")

    def _run_tests(self, dest: Path) -> None:
        """Run pytest with coverage.

        Args:
            dest: Project directory path
        """
        self.logger.info("Running tests")
        timeout = self.settings.get_timeout_for_operation("test")

        uv_path = shutil.which("uv")
        if uv_path:
            cmd = [
                "uv",
                "run",
                "pytest",
                f"--cov={self.config.package_name}",
                "--cov-report=term-missing",
            ]
        else:
            cmd = ["pytest", f"--cov={self.config.package_name}", "--cov-report=term-missing"]

        self.subprocess_runner.run_command(
            command=cmd,
            cwd=dest,
            timeout=timeout,
        )

        self.logger.debug("Tests completed successfully")

    def _build_docs(self, dest: Path) -> None:
        """Build Sphinx documentation.

        Args:
            dest: Project directory path
        """
        self.logger.info("Building documentation")
        timeout = self.settings.get_timeout_for_operation("docs")

        uv_path = shutil.which("uv")
        if uv_path:
            cmd = ["uv", "run", "sphinx-build", "-b", "html", "docs", "docs/_build/html"]
        else:
            cmd = ["sphinx-build", "-b", "html", "docs", "docs/_build/html"]

        self.subprocess_runner.run_command(
            command=cmd,
            cwd=dest,
            timeout=timeout,
        )

        self.logger.debug("Documentation built successfully")

    def _print_dry_run_preview(self, dest: Path) -> None:
        """Print a preview of what would be created in dry-run mode.

        Args:
            dest: Destination path for the project
        """
        self.logger.info("DRY RUN: Preview of scaffolding operations")

        # Get all directories that would be created
        all_dirs = self.directory_structure.get_all_directories(
            root=dest, package_name=self.config.package_name
        )

        # Template mappings to get file list
        pkg_path = dest / "src" / self.config.package_name
        files_to_create = [
            dest / "pyproject.toml",
            dest / "README.md",
            dest / "CHANGELOG.md",
            dest / "CONTRIBUTING.md",
            dest / "SECURITY.md",
            dest / ".gitignore",
            dest / ".env",
            dest / "LICENSE",
            dest / "Makefile",
            dest / ".pre-commit-config.yaml",
            dest / ".github" / "workflows" / "ci.yaml",
            dest / ".github" / "workflows" / "publish.yaml",
            dest / ".github" / "workflows" / "docs.yaml",
            dest / ".github" / "dependabot.yml",
            dest / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
            dest / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
            dest / ".github" / "ISSUE_TEMPLATE" / "config.yml",
            dest / ".github" / "pull_request_template.md",
            pkg_path / "__init__.py",
            pkg_path / "main.py",
            pkg_path / "hello.py",
            pkg_path / "py.typed",
            pkg_path / "utils" / "__init__.py",
            pkg_path / "logger" / "__init__.py",
            pkg_path / "logger" / "logger.py",
            dest / "tests" / "conftest.py",
            dest / "tests" / "unit" / "test_hello.py",
            dest / "scripts" / "security_bandit_check.py",
            dest / "scripts" / "security_safety_check.py",
            dest / "docs" / "conf.py",
            dest / "docs" / "index.rst",
            dest / "docs" / "quickstart.rst",
            dest / "docs" / "development.rst",
            dest / "docs" / "security.rst",
        ]

        # Print summary
        print(f"\n📁 Would create project at: {dest}")
        print(f"   Package name: {self.config.package_name}")
        print(f"   Author: {self.config.author_name} <{self.config.author_email}>")
        print(f"   License: {self.config.license_type}")
        print(
            f"   GitHub: https://github.com/{self.config.github_username}/{self.config.package_name}"
        )

        print(f"\n📂 Would create {len(all_dirs)} directories:")
        for directory in sorted(all_dirs)[:10]:  # Show first 10
            rel_path = directory.relative_to(dest.parent)
            print(f"   {rel_path}/")
        if len(all_dirs) > 10:
            print(f"   ... and {len(all_dirs) - 10} more directories")

        print(f"\n📝 Would create {len(files_to_create)} files:")
        for file_path in sorted(files_to_create)[:15]:  # Show first 15
            rel_path = file_path.relative_to(dest.parent)
            print(f"   {rel_path}")
        if len(files_to_create) > 15:
            print(f"   ... and {len(files_to_create) - 15} more files")

        print("\n🔧 Would execute:")
        print("   • git init && git add . && git commit")
        print("   • uv venv && uv sync --all-extras")
        print("   • pre-commit install && run --all-files")
        print("   • pytest with coverage")
        print("   • sphinx-build documentation")

        print("\n💡 To actually create the project, run without --dry-run")
