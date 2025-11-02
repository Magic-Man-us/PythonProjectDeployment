"""Command-line interface for Python project scaffolding."""

import sys
from pathlib import Path

import click
from pydantic import ValidationError

from python_project_deployment.models import ProjectConfig
from python_project_deployment.scaffolder import Scaffolder


@click.command()
@click.argument("package_name")
@click.argument("target_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--author-name",
    default="Your Name",
    help="Author name for package metadata",
)
@click.option(
    "--author-email",
    default="your.email@example.com",
    help="Author email for package metadata",
)
@click.option(
    "--description",
    default="A new Python package",
    help="Short description of the package",
)
@click.option(
    "--license",
    "license_type",
    default="MIT",
    help="License type (MIT, Apache-2.0, GPL-3.0, etc.)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def main(
    package_name: str,
    target_dir: str,
    author_name: str,
    author_email: str,
    description: str,
    license_type: str,
    verbose: bool,
) -> None:
    """Scaffold a new Python package with best practices.
    
    PACKAGE_NAME: Valid Python package identifier (e.g., my_awesome_pkg)
    TARGET_DIR: Absolute path to parent directory for the project
    
    Example:
        scaffold-python my_package /home/user/projects
    """
    click.echo("🚀 Python Project Scaffolder")
    click.echo("=" * 50)

    # Convert target_dir to absolute path
    target_path = Path(target_dir).resolve()

    try:
        # Create configuration
        config = ProjectConfig(
            package_name=package_name,
            target_dir=target_path,
            author_name=author_name,
            author_email=author_email,
            description=description,
            license_type=license_type,
        )

        if verbose:
            click.echo("\n📋 Configuration:")
            click.echo(f"  Package Name: {config.package_name}")
            click.echo(f"  Target Directory: {config.target_dir}")
            click.echo(f"  Destination: {config.destination_path}")
            click.echo(f"  Author: {config.author_name} <{config.author_email}>")
            click.echo(f"  Description: {config.description}")
            click.echo(f"  License: {config.license_type}")

        # Create scaffolder and execute
        scaffolder = Scaffolder(config)

        click.echo("\n📁 Creating project structure...")
        if verbose:
            click.echo("  Creating directories...")

        click.echo("📝 Rendering templates...")

        click.echo("🔧 Initializing git repository...")

        click.echo("🐍 Setting up virtual environment...")

        click.echo("📦 Installing dependencies...")

        click.echo("✅ Running tests...")

        click.echo("📚 Building documentation...")

        # Run the scaffold process
        result_path = scaffolder.scaffold()

        # Success message
        click.echo("\n" + "=" * 50)
        click.secho("✨ Scaffold complete!", fg="green", bold=True)
        click.echo(f"\n📍 Project created at: {result_path}")

        click.echo("\n📖 Next steps:")
        click.echo(f"  1. cd {result_path}")
        click.echo("  2. source .venv/bin/activate  # (or use uv run)")
        click.echo(f"  3. uv run python -c \"import {package_name}; print({package_name}.hello())\"")

        click.echo("\n🔍 Available commands:")
        click.echo("  • Run tests: pytest")
        click.echo("  • View coverage: open htmlcov/index.html")
        click.echo("  • Build docs: sphinx-build -b html docs docs/_build/html")
        click.echo("  • Format code: black . && isort .")
        click.echo(f"  • Type check: mypy {package_name}")

    except ValidationError as e:
        click.secho("\n❌ Validation Error:", fg="red", bold=True)
        for error in e.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            msg = error["msg"]
            click.echo(f"  • {field}: {msg}")
        sys.exit(1)

    except FileExistsError as e:
        click.secho(f"\n❌ Error: {e}", fg="red", bold=True)
        click.echo("  The destination directory already exists.")
        click.echo("  Please choose a different package name or target directory.")
        sys.exit(1)

    except Exception as e:
        click.secho(f"\n❌ Unexpected Error: {e}", fg="red", bold=True)
        if verbose:
            import traceback
            click.echo("\n" + traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
