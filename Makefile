SHELL := /bin/bash
.PHONY: help install sync test lint type format docs docs-watch docs-clean docs-rebuild precommit clean

help:
	@echo "Available targets:"
	@echo "  make install       # install uv (if missing) and sync dependencies"
	@echo "  make sync          # uv sync --all-extras"
	@echo "  make test          # run tests with coverage"
	@echo "  make lint          # run ruff"
	@echo "  make type          # run mypy"
	@echo "  make format        # format with ruff"
	@echo "  make docs          # build Sphinx docs"
	@echo "  make docs-watch    # build docs with auto-reload on changes"
	@echo "  make docs-clean    # remove built docs"
	@echo "  make docs-rebuild  # clean + rebuild docs"
	@echo "  make precommit     # install pre-commit hooks"
	@echo "  make clean         # remove build artifacts"

install:
	@command -v uv >/dev/null 2>&1 || \
	  { echo "uv not found. Please install uv. Example:"; \
	    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv sync --all-extras

sync:
	uv sync --all-extras

test:
	uv run pytest --cov

lock:
	uv lock

lint:
	uv run ruff check .

type:
	uv run mypy python_project_deployment

format:
	uv run ruff format .

docs:
	@echo " Building Sphinx documentation..."
	@uv run sphinx-build -b html docs docs/_build
	@echo " Documentation built at docs/_build/index.html"

docs-watch:
	@command -v sphinx-autobuild >/dev/null 2>&1 || \
	  { echo "sphinx-autobuild not found. Installing..."; uv add sphinx-autobuild; }
	@echo " Starting live documentation server..."
	uv run sphinx-autobuild docs docs/_build --open-browser

docs-clean:
	@echo " Cleaning documentation build artifacts..."
	rm -rf docs/_build docs/_autosummary
	@echo " Clean complete"

docs-rebuild: docs-clean docs
	@echo " Documentation rebuilt successfully"

precommit:
	uv run pre-commit install

clean:
	rm -rf .venv build dist htmlcov coverage.xml coverage.json docs/_build
