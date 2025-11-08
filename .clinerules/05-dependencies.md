# Dependency Management

## Package Manager
ONLY USE UV for dependency management. DO NOT USE pip or conda.

## Standard Package Requirements

### Core Data & Validation
- `pydantic` - ALL data validation, serialization, JSON encoding/decoding, data models
- `pydantic_settings` - Configuration and environment management
- `pydantic_ai` - AI-related data models and validation

### Testing
- `pytest` - Test framework
- `pytest-mock` - Mocking support

### Standard Library Usage
- `asyncio` - Asynchronous programming
- `logging` - Application logging
- `datetime.datetime` - Date/time operations
- `typing` - Type hints and annotations
- `pathlib` - Filesystem paths
- `contextlib` - Context managers
- `collections` - Specialized containers
- `functools` - Higher-order functions
- `itertools` - Iterator building blocks

### Additional Tools
- `sphinx` - Documentation generation
- `uv` - Dependency management (ONLY)
- `click` - CLI development
- `sqlalchemy` - Database interactions

## UV Workflow

Use Makefile targets for common tasks:
- `make install` - Install dependencies
- `make update` - Update dependencies
- `make docs` - Build Sphinx documentation
- `make precommit` - Install pre-commit hooks
- `make clean` - Remove build artifacts
- `make lock` - Create the uv.lock file

If no Makefile exists, create one with these commands following the existing structure and conventions.
