"""Simple logging configuration for the scaffolder."""

import logging
import sys

from python_project_deployment.config import ScaffolderSettings


def configure_logging(settings: ScaffolderSettings | None = None) -> None:
    """Configure logging with optional file output.

    Args:
        settings: Optional settings for log level and file path
    """
    # Determine log level
    log_level = logging.INFO
    if settings:
        log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Basic format: time | level | name | message
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Add file handler if configured
    if settings and settings.log_file:
        try:
            file_handler = logging.FileHandler(settings.log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(log_format, date_format))
            logging.getLogger().addHandler(file_handler)
        except Exception as e:
            logging.warning(f"Failed to create file handler: {e}")

    # Quiet noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
