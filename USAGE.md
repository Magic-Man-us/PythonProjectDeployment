# Usage Guide - Python Project Deployment

This guide shows you how to use the Python Project Deployment tool to scaffold new Python packages.

## Installation

The tool is installed in editable mode and ready to use:

```bash
# Create or refresh a uv venv and install development extras
uv venv
uv sync --all-extras
```

## Quick Start

### Basic Usage

Create a new Python package with default settings:

```bash
scaffold-python my_awesome_package /path/to/projects
```

This creates a complete project at `/path/to/projects/my_awesome_package/` with:
- Full project structure
- Git repository (initialized)
- Virtual environment (via uv)
- Dependencies installed
- Tests passing
- Documentation built

### Custom Package

Specify custom metadata:

```bash
scaffold-python data_analyzer /home/user/projects \
  --author-name "Jane Doe" \
  --author-email "jane@example.com" \
  --description "A powerful data analysis toolkit" \
  --license "Apache-2.0"
```

### Verbose Mode

## Installation

The tool is installed in editable mode and ready to use (uv-first):

```bash
# Create or refresh a uv venv
uv venv

# Install dev extras (sync will install extras listed in pyproject)
uv sync --all-extras
```
See detailed progress:

```bash
scaffold-python my_package /tmp -v
```

## What Gets Created

The tool creates a complete Python package with this structure:

```
my_package/
├── .github/
│   └── workflows/
│       └── ci.yaml          # GitHub Actions CI/CD
├── docs/
│   ├── conf.py              # Sphinx configuration
│   └── index.rst            # Documentation index
├── tests/
│   └── test_hello.py        # Example tests
├── my_package/
│   ├── __init__.py          # Package init
│   └── hello.py             # Example module
├── .gitignore               # Python .gitignore
├── .venv/                   # Virtual environment
├── LICENSE                  # MIT License
├── README.md                # Project README
└── pyproject.toml           # Modern Python packaging
```

## Post-Creation Workflow

After creating your package:

```bash
# Navigate to the project
  ### Post-Creation Workflow

  After creating your package follow this uv-first workflow:

```bash
# Navigate to the project
cd /path/to/your/my_package

# Use uv for any command (preferred)
uv run python -c "import my_package; print(my_package.hello())"

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=my_package

# View coverage report (HTML)
xdg-open htmlcov/index.html || true

# Build documentation (Sphinx)
uv run sphinx-build -b html docs docs/_build/html
xdg-open docs/_build/html/index.html || true

# Format code
uv run ruff format .

# Type checking
uv run mypy my_package

# Linting
uv run ruff check my_package

# Run pre-commit hooks
uv run pre-commit install
uv run pre-commit run --all-files
```
Our CI is uv-first and now uses a single canonical workflow: `.github/workflows/ci.yml`. It sets up `uv`, installs Python versions, syncs dependencies, and runs linters, mypy, pre-commit, tests and security scans.
```

## Features Included

### ✅ Testing
- pytest configured with coverage
- Example tests included
- Coverage reports (terminal + HTML)

### 📚 Documentation
- Sphinx with Furo theme
- Auto-generated API docs
- Example documentation structure

### 🔧 Development Tools
- Black formatter
- isort import sorting
- mypy type checking
- ruff linting

### 🚀 CI/CD
- GitHub Actions workflow
- Multi-Python version testing (3.10, 3.11, 3.12)
- Automated linting and type checking
- Test coverage reporting

### 📦 Modern Packaging
- pyproject.toml (PEP 621)
- hatchling build backend
- uv for dependency management
- Development extras included

## Examples

### Create a Data Science Package

```bash
scaffold-python ml_toolkit ~/projects \
  --author-name "Data Team" \
  --author-email "data@company.com" \
  --description "Machine learning utilities and tools"
```

### Create an API Client

```bash
scaffold-python api_client ~/work \
  --author-name "API Team" \
  --description "REST API client library" \
  --license "MIT"
```

### Create a CLI Tool

```bash
scaffold-python my_cli_tool ~/tools \
  --author-name "DevOps Team" \
  --description "Command-line automation tool"
```

## Validation

The tool validates inputs:

### Package Name Rules
- ✅ Valid: `my_package`, `data_processor`, `api_v2`, `_internal`
- ❌ Invalid: `123pkg` (starts with number), `my-package` (has hyphen), `my.package` (has dot)

### Target Directory Rules
- ✅ Must be an absolute path: `/home/user/projects`
- ❌ Relative paths not allowed: `./projects`, `~/projects`

### Destination Checking
- Tool checks if destination already exists
- Fails gracefully if package folder already exists

## Troubleshooting

### Command not found

If `scaffold-python` is not found:

```bash
# Reinstall in editable mode
uv sync --all-extras

# Or run directly
uv run python -m python_project_deployment.cli --help
```

### Import errors

If you see import errors after creation:

```bash
cd your_new_package
source .venv/bin/activate
  uv sync --all-extras
```

### Git not initialized

If git commands fail, ensure git is installed:

```bash
git --version
```

## Development of the Scaffolder

To develop or modify the scaffolder itself:

```bash
# Clone/navigate to the scaffolder directory
cd $(pwd)  # run this from the repository root

# Install in dev mode
uv venv
uv sync --all-extras

# Run tests
pytest tests/ -v

# Make changes to templates in python_project_deployment/templates/

# Test your changes by creating a test package
scaffold-python test_pkg /tmp
```

## Templates

Templates are in `python_project_deployment/templates/` using Jinja2:

- `pyproject.toml.j2` - Project metadata and dependencies
- `README.md.j2` - Project README
- `.gitignore.j2` - Python .gitignore
- `LICENSE.j2` - MIT License
- `ci.yaml.j2` - GitHub Actions CI
- `package_init.py.j2` - Package __init__.py
- `hello.py.j2` - Example module
- `test_hello.py.j2` - Example tests
- `conf.py.j2` - Sphinx configuration
- `index.rst.j2` - Documentation index

Variables available in templates:
- `{{ PKG }}` - Package name
- `{{ AUTHOR_NAME }}` - Author name
- `{{ AUTHOR_EMAIL }}` - Author email
- `{{ DESCRIPTION }}` - Package description
- `{{ LICENSE }}` - License type

## License

MIT License - See LICENSE file for details.
