"""Secure subprocess execution with timeout enforcement.

This module provides secure subprocess execution with comprehensive timeout
handling, command validation, and structured result capture. All subprocess
operations should use this module to ensure consistent security and error handling.
"""

import subprocess
import time
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from python_project_deployment.exceptions import SecurityError, SubprocessError


class SubprocessResult(BaseModel):
    """Structured result from subprocess execution.

    Attributes:
        command: The command that was executed as a list of strings
        returncode: Exit code from the subprocess
        stdout: Standard output captured from the process
        stderr: Standard error captured from the process
        duration: Execution time in seconds
        timed_out: Whether the process exceeded the timeout
    """

    command: list[str] = Field(..., description="Command executed as list of strings")
    returncode: int = Field(..., description="Process exit code")
    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    duration: float = Field(..., ge=0, description="Execution duration in seconds")
    timed_out: bool = Field(default=False, description="Whether process timed out")

    @field_validator("command")
    @classmethod
    def validate_command_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure command list is not empty."""
        if not v:
            raise ValueError("Command list cannot be empty")
        return v

    def __str__(self) -> str:
        """Return human-readable representation."""
        status = "TIMEOUT" if self.timed_out else f"exit {self.returncode}"
        return (
            f"Command: {' '.join(self.command)}\nStatus: {status}\nDuration: {self.duration:.2f}s"
        )


class SubprocessRunner:
    """Secure subprocess execution manager with timeout enforcement.

    This class provides a safe interface for executing subprocess commands
    with timeout enforcement, command validation, and structured error handling.

    Example:
        >>> runner = SubprocessRunner()
        >>> result = runner.run_command(
        ...     command=["git", "init"],
        ...     cwd=Path("/path/to/project"),
        ...     timeout=30
        ... )
        >>> print(f"Exit code: {result.returncode}")
    """

    def __init__(self) -> None:
        """Initialize the subprocess runner."""
        pass

    def run_command(
        self,
        command: list[str],
        cwd: Path,
        timeout: int,
        capture_output: bool = True,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> SubprocessResult:
        """Execute command with security checks and timeout.

        Args:
            command: Command to execute as list of strings
            cwd: Working directory for command execution
            timeout: Maximum execution time in seconds
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit
            env: Optional environment variables (merged with os.environ)

        Returns:
            SubprocessResult with execution details

        Raises:
            SecurityError: If command validation fails
            SubprocessError: If command execution fails or times out
        """
        # Validate command before execution
        self.validate_command(command)

        # Validate working directory
        if not cwd.exists():
            raise SecurityError(
                f"Working directory does not exist: {cwd}",
                context={"cwd": str(cwd)},
            )
        if not cwd.is_dir():
            raise SecurityError(
                f"Working directory is not a directory: {cwd}",
                context={"cwd": str(cwd)},
            )

        # Validate timeout
        if timeout <= 0:
            raise SecurityError(
                f"Timeout must be positive: {timeout}",
                context={"timeout": timeout},
            )

        # Execute command with timeout
        start_time = time.time()
        timed_out = False
        stdout_str = ""
        stderr_str = ""
        returncode = 0

        try:
            result = subprocess.run(
                command,
                cwd=str(cwd),
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                check=False,  # We handle check manually
                env=env,
            )
            returncode = result.returncode
            stdout_str = result.stdout if capture_output else ""
            stderr_str = result.stderr if capture_output else ""

        except subprocess.TimeoutExpired as e:
            timed_out = True
            returncode = -1
            stdout_str = e.stdout.decode() if e.stdout else ""
            stderr_str = e.stderr.decode() if e.stderr else ""

        except Exception as e:
            # Unexpected error during execution
            duration = time.time() - start_time
            result_obj = SubprocessResult(
                command=command,
                returncode=-1,
                stdout="",
                stderr=str(e),
                duration=duration,
                timed_out=False,
            )
            raise SubprocessError(
                f"Unexpected error executing command: {e}",
                result=result_obj,
                context={"command": command, "cwd": str(cwd), "error_type": type(e).__name__},
            ) from e

        # Calculate duration
        duration = time.time() - start_time

        # Create result object
        result_obj = SubprocessResult(
            command=command,
            returncode=returncode,
            stdout=stdout_str,
            stderr=stderr_str,
            duration=duration,
            timed_out=timed_out,
        )

        # Handle timeout
        if timed_out:
            raise SubprocessError(
                f"Command timed out after {timeout}s: {' '.join(command)}",
                result=result_obj,
                context={"timeout": timeout, "duration": duration},
            )

        # Handle non-zero exit if check is enabled
        if check and returncode != 0:
            raise SubprocessError(
                f"Command failed with exit code {returncode}: {' '.join(command)}",
                result=result_obj,
                context={"returncode": returncode},
            )

        return result_obj

    def validate_command(self, command: list[str]) -> None:
        """Validate command before execution.

        This performs basic security validation to prevent common issues:
        - Empty commands
        - Shell metacharacters that could indicate injection
        - Suspicious patterns

        Args:
            command: Command to validate as list of strings

        Raises:
            SecurityError: If command validation fails
        """
        if not command:
            raise SecurityError(
                "Command list is empty",
                context={"command": command},
            )

        if not isinstance(command, list):
            raise SecurityError(
                "Command must be a list of strings",
                context={"command_type": type(command).__name__},
            )

        # Check each part is a string
        for i, part in enumerate(command):
            if not isinstance(part, str):
                raise SecurityError(
                    f"Command part {i} is not a string: {type(part).__name__}",
                    context={"command": command, "part_index": i},
                )

        # Check for empty strings
        if any(not part for part in command):
            raise SecurityError(
                "Command contains empty strings",
                context={"command": command},
            )

        # Basic check for suspicious patterns (shell metacharacters)
        # Note: Since we pass command as list to subprocess.run,
        # shell metacharacters won't be interpreted, but we check anyway
        # to catch potential issues early
        suspicious_chars = {";", "|", "&", "$", "`", "\n", "\r"}
        for i, part in enumerate(command):
            if any(char in part for char in suspicious_chars):
                raise SecurityError(
                    f"Command part {i} contains suspicious characters",
                    context={
                        "command": command,
                        "part_index": i,
                        "part": part,
                        "suspicious_chars": list(suspicious_chars),
                    },
                )


def run_command(
    command: list[str],
    cwd: Path,
    timeout: int,
    capture_output: bool = True,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> SubprocessResult:
    """Convenience function to run a command with default runner.

    This is a module-level convenience function that creates a SubprocessRunner
    and executes the command. For multiple commands, consider reusing a
    SubprocessRunner instance.

    Args:
        command: Command to execute as list of strings
        cwd: Working directory for command execution
        timeout: Maximum execution time in seconds
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise exception on non-zero exit
        env: Optional environment variables

    Returns:
        SubprocessResult with execution details

    Raises:
        SecurityError: If command validation fails
        SubprocessError: If command execution fails or times out
    """
    runner = SubprocessRunner()
    return runner.run_command(
        command=command,
        cwd=cwd,
        timeout=timeout,
        capture_output=capture_output,
        check=check,
        env=env,
    )
