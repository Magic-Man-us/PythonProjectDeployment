"""Logger module for the scaffolder.

Provides centralized logging configuration and utilities.
"""

from python_project_deployment.logger.logger import (
    configure_logging,
    get_logger,
)

__all__ = ["configure_logging", "get_logger"]
