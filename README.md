# Python Project Deployment

A modern scaffolding tool for creating new Python packages with best practices built-in.

## Features

- 🚀 **Fast Setup**: Create fully-configured Python packages in seconds
- 📦 **uv Integration**: Modern dependency management with `uv`
- ✅ **Testing Ready**: Pre-configured `pytest` with coverage
- 📚 **Documentation**: Sphinx docs with `furo` theme
- 🔄 **CI/CD**: GitHub Actions workflow included
- 🎯 **Best Practices**: PEP 8 compliant, type hints, proper structure

## Installation

```bash
# Install with uv
uv pip install -e .

# Or with pip
pip install -e .
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
4. ✅ Sets up `uv` virtual environment
5. ✅ Installs dev dependencies
6. ✅ Runs initial tests
7. ✅ Builds documentation

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

## Development

```bash
# Clone the repository
git clone https://github.com/magicman/python-project-deployment.git
cd python-project-deployment

# Install in development mode
uv venv
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type check
mypy python_project_deployment
```

## Requirements

- Python 3.10+
- uv (recommended) or pip

## License

MIT License - see LICENSE file for details.
