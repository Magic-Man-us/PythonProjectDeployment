# Python Project Deployment

[![CI](https://github.com/Magic-Man-us/PythonProjectDeployment/actions/workflows/ci.yml/badge.svg)](https://github.com/Magic-Man-us/PythonProjectDeployment/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/python-project-deployment.svg)](https://pypi.org/project/python-project-deployment)
[![Python Versions](https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13%20|%203.14-blue)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern scaffolding tool for creating new Python packages with best practices built-in.

## Features

-  **Fast Setup**: Create fully-configured Python packages in seconds
-  **uv Integration**: Modern dependency & venv management using `uv`
-  **Testing Ready**: Pre-configured `pytest` with coverage
-  **Documentation**: Sphinx docs included
-  **CI/CD**: uv-first GitHub Actions workflow (single canonical `ci.yml`)
-  **Best Practices**: PEP 8 compliant, type hints, pre-commit hooks, type checking

## Installation

```bash
# Install (uv-first)
uv venv
uv sync --all-extras
```

## Usage

### CLI Command

```bash
scaffold-python my_awesome_package /path/to/parent/directory
```

### What Gets Created

```
my_awesome_package/
├── .github/
│   └── workflows/
│       └── ci.yaml
├── docs/
│   ├── conf.py
│   └── index.rst
├── tests/
│   └── test_hello.py
├── my_awesome_package/
│   ├── __init__.py
│   └── hello.py
├── .gitignore
├── LICENSE
├── Makefile
├── README.md
├── pyproject.toml
└── requirements-dev.txt
```

### Post-Creation Steps

The tool automatically:
1. ✅ Validates inputs
2. ✅ Creates project structure
3. ✅ Initializes git repository
4. ✅ Sets up `uv` virtual environment (preferred)
5. ✅ Installs dev dependencies
6. ✅ Runs initial tests
7. ✅ Installs and runs `pre-commit` hooks
8. ✅ Builds documentation

## Example

```bash
# Create a new package
scaffold-python data_processor /home/user/projects

# Navigate to the new package
cd /home/user/projects/data_processor

# Activate the environment
source .venv/bin/activate

# Run tests
pytest

# Build docs
sphinx-build -b html docs docs/_build/html
```

# Development

Local development is uv-first. Use the provided Makefile for convenience or run uv directly.

Using the Makefile (recommended):

```bash
# Create or refresh a uv venv and install dev deps
make install

# Run the test suite
make test

# Run linters and type checks
make lint
make type

# Apply formatting (Black/isort)
make format

# Run pre-commit hooks locally
make precommit
```

Direct uv commands:

```bash
# Create a venv and install dev extras
uv venv
uv sync --all-extras

# Run tests
uv run pytest

# Run linters
uv run ruff check .
uv run mypy python_project_deployment

# Run pre-commit
uv run pre-commit install
uv run pre-commit run --all-files
```

## Requirements

- Python 3.11+ (recommended)
- uv (strongly recommended) — the scaffolder / CI are uv-first

If `uv` is not available, the tool will try to fall back to `pip`, but behaviour and reproducibility are better with `uv`.

## License

MIT License - see LICENSE file for details.
