"""Python Project Deployment - A scaffolding tool for Python packages."""

__version__ = "0.1.0"

from python_project_deployment.config import ScaffolderSettings
from python_project_deployment.directory_structure import (
    DirectoryStructure,
    DocsStructure,
    GitHubStructure,
    PackageStructure,
    TestStructure,
)
from python_project_deployment.exceptions import (
    ConfigurationError,
    FileSystemError,
    PrerequisiteError,
    RollbackError,
    ScaffolderError,
    SecurityError,
    SubprocessError,
    ValidationError,
)
from python_project_deployment.models import ProjectConfig
from python_project_deployment.scaffolder import Scaffolder

__all__ = [
    # Core classes
    "Scaffolder",
    "ProjectConfig",
    "ScaffolderSettings",
    # Directory structures
    "DirectoryStructure",
    "PackageStructure",
    "TestStructure",
    "DocsStructure",
    "GitHubStructure",
    # Exceptions
    "ScaffolderError",
    "ValidationError",
    "SecurityError",
    "FileSystemError",
    "SubprocessError",
    "RollbackError",
    "ConfigurationError",
    "PrerequisiteError",
    # Version
    "__version__",
]
