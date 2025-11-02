Usage Guide
===========

Basic Usage
-----------

Run the interactive CLI:

.. code-block:: bash

   scaffold-python my_package /path/to/parent/directory

The tool will prompt you for:

* Package name (must be valid Python identifier)
* Target directory (absolute path)
* Author name
* Author email
* Project description
* License type (MIT, Apache-2.0, GPL-3.0, BSD-3-Clause)

What Gets Created
-----------------

The scaffolder generates a complete project structure:

.. code-block:: text

   your-package/
   ├── .github/
   │   └── workflows/
   │       └── ci.yml           # GitHub Actions CI/CD
   ├── .gitignore               # Python-specific gitignore
   ├── pyproject.toml           # Modern Python project config
   ├── README.md                # Project documentation
   ├── LICENSE                  # Your chosen license
   ├── Makefile                 # Development shortcuts
   ├── your_package/
   │   ├── __init__.py
   │   └── hello.py             # Entry point template
   └── tests/
       ├── __init__.py
       └── test_hello.py        # Example test

Development Workflow
--------------------

After scaffolding, use the included Makefile:

.. code-block:: bash

   make install    # Install dependencies
   make test       # Run tests with coverage
   make lint       # Check code with Ruff
   make type       # Type check with mypy
   make format     # Auto-format code
   make docs       # Build Sphinx docs

Command Line Options
--------------------

.. code-block:: bash

   scaffold-python --help

Options:

* ``--author-name`` - Author name for package metadata (default: "Your Name")
* ``--author-email`` - Author email (default: "your.email@example.com")
* ``--description`` - Short package description (default: "A new Python package")
* ``--license`` - License type (default: "MIT")
* ``--verbose`` / ``-v`` - Enable verbose output

Programmatic Usage
------------------

Use as a library:

.. code-block:: python

   from pathlib import Path
   from python_project_deployment.models import ProjectConfig
   from python_project_deployment.scaffolder import Scaffolder

   config = ProjectConfig(
       package_name="my_package",
       target_dir=Path("/absolute/path/to/parent"),
       author_name="Your Name",
       author_email="you@example.com",
       description="My awesome package",
       license_type="MIT"
   )

   scaffolder = Scaffolder(config)
   project_path = scaffolder.scaffold()
   print(f"Project created at: {project_path}")
