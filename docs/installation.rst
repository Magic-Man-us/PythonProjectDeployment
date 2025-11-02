Installation
============

Requirements
------------

* Python 3.10+
* ``uv`` (recommended) or ``pip``

Install via pip
---------------

.. code-block:: bash

   uv add python-project-deployment

Install via uv
--------------

.. code-block:: bash

   uv uv add python-project-deployment

Development Installation
------------------------

Clone and install with development dependencies:

.. code-block:: bash

   git clone https://github.com/Magic-Man-us/PythonProjectDeployment
   cd PythonProjectDeployment
   make install

This will:

1. Check for ``uv`` (install if missing)
2. Sync all dependencies including dev/test/docs extras
3. Set up the project in editable mode
