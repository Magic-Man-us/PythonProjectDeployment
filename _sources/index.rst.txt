Python Project Deployment Documentation
========================================

A modern scaffolding tool for creating new Python packages with best practices built-in.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api

Installation
============

Install using uv (preferred):

.. code-block:: bash

   uv venv
   uv sync --all-extras

Quick Start
===========

Create a new Python package:

.. code-block:: bash

   scaffold-python my_awesome_package /path/to/parent/directory

API Reference
=============

.. automodule:: python_project_deployment
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: python_project_deployment.cli
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: python_project_deployment.models
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: python_project_deployment.scaffolder
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
