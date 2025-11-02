"""Python Project Deployment - A scaffolding tool for Python packages."""

__version__ = "0.1.0"

from python_project_deployment.models import ProjectConfig
from python_project_deployment.scaffolder import Scaffolder

__all__ = ["Scaffolder", "ProjectConfig", "__version__"]
