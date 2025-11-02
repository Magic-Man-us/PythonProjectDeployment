Python Project Deployment
==========================

**Automated Python project scaffolding with best practices built-in.**

A modern scaffolding tool that creates production-ready Python projects with comprehensive
testing, linting, type checking, CI/CD, and documentation infrastructure.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api

Features
--------

* 🚀 **Modern Python packaging** with ``pyproject.toml`` and ``uv``
* 🔍 **Pre-configured linting** (Ruff), type checking (mypy), testing (pytest)
* 📦 **Multiple license options** (MIT, Apache-2.0, GPL-3.0, BSD-3-Clause)
* 🔄 **GitHub Actions CI/CD** workflows included
* 📚 **Sphinx documentation** with auto-generated API docs
* 🎯 **Pre-commit hooks** for code quality enforcement

Quick Start
-----------

Install and create a new project:

.. code-block:: bash

   # Install
   pip install python-project-deployment

   # Create a new project
   scaffold-python my_package /path/to/parent/directory

The scaffolder creates a complete project structure with:

* Package source code with entry point
* Comprehensive test suite with pytest
* Pre-configured Makefile for common tasks
* GitHub Actions workflows for CI/CD
* Sphinx documentation with auto-generated API docs
* Pre-commit hooks for code quality

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
