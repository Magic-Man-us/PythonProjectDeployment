SHELL := /bin/bash
.PHONY: help install sync test quick-test test-cov lint type format check security docs docs-watch docs-clean docs-rebuild precommit clean

help:
	@echo "=== Quick Commands (Recommended for Development) ==="
	@echo "  make quick-test    # run tests FAST (no coverage, no strict checks)"
	@echo "  make install       # install uv (if missing) and sync dependencies"
	@echo "  make format        # auto-format code with ruff"
	@echo ""
	@echo "=== Quality Checks (Optional) ==="
	@echo "  make test-cov      # run tests with coverage reporting"
	@echo "  make lint          # check code style with ruff"
	@echo "  make type          # type check with mypy"
	@echo "  make security      # run security scans (bandit)"
	@echo "  make check         # run ALL quality checks"
	@echo ""
	@echo "=== Other Commands ==="
	@echo "  make sync          # sync dependencies with uv"
	@echo "  make docs          # build Sphinx documentation"
	@echo "  make docs-watch    # build docs with auto-reload"
	@echo "  make precommit     # install pre-commit hooks (OPTIONAL)"
	@echo "  make clean         # remove build artifacts"

install:
	@command -v uv >/dev/null 2>&1 || \
	  { echo "uv not found. Please install uv. Example:"; \
	    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv sync --all-extras

sync:
	uv sync --all-extras

test: quick-test
	@echo "Tip: Use 'make quick-test' for faster testing without coverage"

quick-test:
	@echo " Running tests (fast mode, no coverage)..."
	uv run pytest -v

test-cov:
	@echo " Running tests with coverage reporting..."
	uv run pytest --cov --cov-report=term --cov-report=html

lock:
	uv lock

lint:
	uv run ruff check .

type:
	uv run mypy src/python_project_deployment

check:
	@echo " Running all quality checks..."
	@echo ""
	@echo " [1/4] Formatting check..."
	@uv run ruff format --check . || echo "Format issues found - run 'make format' to fix"
	@echo ""
	@echo " [2/4] Linting..."
	@uv run ruff check . || echo "Lint issues found"
	@echo ""
	@echo " [3/4] Type checking..."
	@uv run mypy src/python_project_deployment || echo "Type issues found"
	@echo ""
	@echo " [4/4] Running tests..."
	@uv run pytest -v || echo "Test failures found"
	@echo ""
	@echo " Quality check complete!"

security:
	@echo " Running security scans..."
	@uv run bandit -r src/python_project_deployment/ || echo "Security issues found"

format:
	@echo " Auto-formatting code..."
	uv run ruff format .
	@echo " Format complete!"

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
