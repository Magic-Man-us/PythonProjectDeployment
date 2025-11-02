"""Configuration management using Pydantic Settings.

This module provides environment-based configuration for the scaffolder
using pydantic-settings BaseSettings. Configuration can be loaded from:
1. Environment variables (SCAFFOLD_ prefix)
2. .env files
3. CLI arguments (highest precedence)

Configuration precedence: CLI args > Environment variables > .env file > defaults
"""

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from python_project_deployment.exceptions import ConfigurationError


class SecurityLevel(str, Enum):
    """Security check severity levels for validation."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ScaffolderSettings(BaseSettings):
    """Application settings with environment variable support.

    All settings can be configured via:
    - Environment variables with SCAFFOLD_ prefix (e.g., SCAFFOLD_TIMEOUT_GIT)
    - .env file in the current directory
    - Programmatic configuration

    Attributes:
        timeout_git: Timeout in seconds for git operations (1-300)
        timeout_install: Timeout in seconds for package installation (60-3600)
        timeout_test: Timeout in seconds for test execution (30-1800)
        timeout_docs: Timeout in seconds for documentation build (30-900)
        security_fail_level: Security check severity level that triggers failure
        validate_binaries: Whether to validate binary executables
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file for persistent logging
    """

    model_config = SettingsConfigDict(
        env_prefix="SCAFFOLD_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    # Timeout configurations
    timeout_git: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Timeout for git operations in seconds",
    )
    timeout_install: int = Field(
        default=600,
        ge=60,
        le=3600,
        description="Timeout for package installation in seconds",
    )
    timeout_test: int = Field(
        default=300,
        ge=30,
        le=1800,
        description="Timeout for test execution in seconds",
    )
    timeout_docs: int = Field(
        default=180,
        ge=30,
        le=900,
        description="Timeout for documentation build in seconds",
    )

    # Security settings
    validate_binaries: bool = Field(
        default=True,
        description="Whether to validate binary executables before use",
    )

    # Execution settings
    dry_run: bool = Field(
        default=False,
        description="Preview changes without making them (dry-run mode)",
    )

    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_file: Path | None = Field(
        default=None,
        description="Optional path to log file",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ConfigurationError(
                f"Invalid log level: {v}",
                context={"valid_levels": list(valid_levels), "provided": v},
            )
        return v_upper

    @field_validator("log_file", mode="after")
    @classmethod
    def validate_log_file_writable(cls, v: Path | None) -> Path | None:
        """Validate that log file directory is writable if specified."""
        if v is not None:
            parent = v.parent
            if not parent.exists():
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    raise ConfigurationError(
                        f"Cannot create log file directory: {parent}",
                        context={"path": str(parent), "error": str(e)},
                    ) from e
            if not parent.is_dir():
                raise ConfigurationError(
                    f"Log file parent is not a directory: {parent}",
                    context={"path": str(parent)},
                )
        return v

    def get_timeout_for_operation(self, operation: str) -> int:
        """Get timeout for a specific operation.

        Args:
            operation: Operation name (git, install, test, docs)

        Returns:
            Timeout in seconds

        Raises:
            ConfigurationError: If operation is not recognized
        """
        timeout_map = {
            "git": self.timeout_git,
            "install": self.timeout_install,
            "test": self.timeout_test,
            "docs": self.timeout_docs,
        }
        timeout = timeout_map.get(operation)
        if timeout is None:
            raise ConfigurationError(
                f"Unknown operation: {operation}",
                context={"operation": operation, "valid_operations": list(timeout_map.keys())},
            )
        return timeout


def load_settings(env_file: Path | None = None) -> ScaffolderSettings:
    """Load settings from environment and optional .env file.

    Args:
        env_file: Optional path to .env file. If None, looks for .env in current directory

    Returns:
        Loaded ScaffolderSettings instance

    Raises:
        ConfigurationError: If configuration is invalid
    """
    try:
        if env_file is not None:
            # Load dotenv file manually, then create settings
            # override=False means existing environment variables take precedence
            from dotenv import load_dotenv

            load_dotenv(env_file, override=False)
        # Create settings - will use environment variables (including those loaded from .env)
        return ScaffolderSettings()
    except Exception as e:
        raise ConfigurationError(
            f"Failed to load settings: {e}",
            context={"env_file": str(env_file) if env_file else None},
        ) from e


def merge_cli_with_settings(
    cli_args: dict[str, Any], settings: ScaffolderSettings
) -> dict[str, Any]:
    """Merge CLI arguments with settings, with CLI taking precedence.

    This function implements the configuration precedence:
    CLI args > Environment variables > .env file > defaults

    Args:
        cli_args: Dictionary of CLI arguments (only non-None values)
        settings: Loaded ScaffolderSettings

    Returns:
        Merged configuration dictionary

    Note:
        Only CLI arguments that are explicitly provided (not None) will
        override the settings values.
    """
    # Start with settings as base
    config = settings.model_dump()

    # Override with CLI args (only if explicitly provided)
    for key, value in cli_args.items():
        if value is not None:
            config[key] = value

    return config
