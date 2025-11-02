"""Custom exception hierarchy for the scaffolder.

This module provides a comprehensive exception hierarchy for error handling
throughout the scaffolder application. All exceptions inherit from ScaffolderError
and preserve context information for debugging.
"""

from typing import Any


class ScaffolderError(Exception):
    """Base exception for all scaffolder errors.

    All custom exceptions in the scaffolder inherit from this base class.
    Includes context preservation for enhanced debugging and error reporting.

    Attributes:
        context: Dictionary containing contextual information about the error
    """

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Initialize the exception with a message and optional context.

        Args:
            message: Human-readable error message
            context: Optional dictionary with contextual information
        """
        super().__init__(message)
        self.context = context or {}

    def __str__(self) -> str:
        """Return string representation with context if available."""
        base_msg = super().__str__()
        if self.context:
            context_str = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
            return f"{base_msg} [Context: {context_str}]"
        return base_msg

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return f"{self.__class__.__name__}({super().__str__()!r}, context={self.context!r})"


class ValidationError(ScaffolderError):
    """Raised when validation fails.

    This exception is raised when input validation fails, such as invalid
    package names, paths, or configuration values.
    """

    pass


class SecurityError(ScaffolderError):
    """Raised when a security violation is detected.

    This exception is raised for security-related issues such as path traversal
    attempts, invalid binaries, or other security policy violations.
    """

    pass


class SubprocessError(ScaffolderError):
    """Raised when a subprocess execution fails.

    This exception preserves detailed information about the subprocess
    execution, including the command, exit code, output, and timing.

    Attributes:
        result: SubprocessResult object with execution details
    """

    def __init__(
        self,
        message: str,
        result: Any,  # SubprocessResult - avoiding circular import
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize with subprocess execution details.

        Args:
            message: Human-readable error message
            result: SubprocessResult object with execution details
            context: Optional dictionary with additional context
        """
        super().__init__(message, context)
        self.result = result

    def __str__(self) -> str:
        """Return string representation with subprocess details."""
        base_msg = super().__str__()
        if self.result:
            return (
                f"{base_msg}\n"
                f"Command: {' '.join(self.result.command)}\n"
                f"Exit code: {self.result.returncode}\n"
                f"Duration: {self.result.duration:.2f}s\n"
                f"Timed out: {self.result.timed_out}"
            )
        return base_msg


class FileSystemError(ScaffolderError):
    """Raised when a file system operation fails.

    This exception is raised for file system related errors such as
    permission issues, missing directories, or I/O failures.
    """

    pass


class RollbackError(ScaffolderError):
    """Raised when rollback operations fail.

    This exception is raised when an error occurs during the rollback
    process. The original error that triggered the rollback should be
    preserved in the context.
    """

    pass


class ConfigurationError(ScaffolderError):
    """Raised when configuration is invalid or missing.

    This exception is raised for configuration-related errors such as
    missing required settings, invalid timeout values, or malformed
    configuration files.
    """

    pass


class PrerequisiteError(ScaffolderError):
    """Raised when required prerequisites are not met.

    This exception is raised when required tools (git, uv, pip) are not
    available or when the system doesn't meet other prerequisites for
    scaffolding.
    """

    pass
