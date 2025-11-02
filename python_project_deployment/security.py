"""Security utilities for the scaffolder.

This module provides security-related utilities including path traversal
validation, template value sanitization, binary validation, and secure
file permission setting.
"""

import os
import shutil
import stat
from pathlib import Path

from python_project_deployment.exceptions import SecurityError


def validate_path_traversal(path: Path, base_path: Path) -> Path:
    """Ensure path doesn't escape base directory.

    This function validates that the resolved path is within the base directory,
    preventing path traversal attacks using "..", symlinks, or absolute paths.

    Args:
        path: Path to validate (can be relative or absolute)
        base_path: Base directory that path must remain within

    Returns:
        Resolved absolute path that is confirmed to be within base_path

    Raises:
        SecurityError: If path attempts to escape base_path
    """
    # Initialize variables for exception handling
    resolved_base: Path
    resolved_path: Path

    try:
        # Resolve both paths to absolute, canonical paths
        # This resolves symlinks and removes ".." components
        resolved_base = base_path.resolve()
        resolved_path = (base_path / path).resolve()

        # Check if resolved_path is relative to resolved_base
        # This will raise ValueError if resolved_path is not relative to resolved_base
        resolved_path.relative_to(resolved_base)

        return resolved_path
    except ValueError as e:
        raise SecurityError(
            f"Path traversal attempt detected: {path}",
            context={
                "attempted_path": str(path),
                "base_path": str(base_path),
                "resolved_base": str(resolved_base),
                "resolved_path": str(resolved_path),
            },
        ) from e
    except Exception as e:
        raise SecurityError(
            f"Failed to validate path: {path}",
            context={"path": str(path), "base_path": str(base_path), "error": str(e)},
        ) from e


def sanitize_template_value(value: str, max_length: int = 1000) -> str:
    """Sanitize values before template rendering.

    This function removes potentially dangerous characters and enforces
    length limits to prevent template injection attacks and excessive
    memory usage.

    Args:
        value: String value to sanitize
        max_length: Maximum allowed length (default: 1000)

    Returns:
        Sanitized string value

    Raises:
        SecurityError: If value exceeds max_length or contains null bytes
    """
    if not isinstance(value, str):
        raise SecurityError(
            f"Template value must be string, got {type(value).__name__}",
            context={"value_type": type(value).__name__},
        )

    # Check for null bytes (potential injection)
    if "\x00" in value:
        raise SecurityError(
            "Null bytes not allowed in template values",
            context={"value_preview": value[:50]},
        )

    # Enforce length limit
    if len(value) > max_length:
        raise SecurityError(
            f"Template value exceeds maximum length of {max_length}",
            context={"length": len(value), "max_length": max_length, "preview": value[:50]},
        )

    # Remove any control characters except common whitespace
    # Keep: tab (\t), newline (\n), carriage return (\r)
    sanitized = "".join(char for char in value if char >= " " or char in "\t\n\r")

    return sanitized


def validate_binary(binary_path: Path, expected_name: str) -> bool:
    """Verify binary is what it claims to be.

    This function checks if a binary exists and its basename matches
    the expected name, helping prevent execution of malicious binaries.

    Args:
        binary_path: Path to the binary to validate
        expected_name: Expected basename of the binary (e.g., "git", "python")

    Returns:
        True if binary is valid

    Raises:
        SecurityError: If binary is not found or doesn't match expected name
    """
    if not binary_path.exists():
        raise SecurityError(
            f"Binary not found: {expected_name}",
            context={"expected": expected_name, "path": str(binary_path)},
        )

    if not binary_path.is_file():
        raise SecurityError(
            f"Binary path is not a file: {expected_name}",
            context={"expected": expected_name, "path": str(binary_path)},
        )

    # Check if executable
    if not os.access(binary_path, os.X_OK):
        raise SecurityError(
            f"Binary is not executable: {expected_name}",
            context={"expected": expected_name, "path": str(binary_path)},
        )

    # Verify basename matches expected name
    actual_name = binary_path.name
    if actual_name != expected_name:
        raise SecurityError(
            f"Binary name mismatch: expected '{expected_name}', got '{actual_name}'",
            context={"expected": expected_name, "actual": actual_name, "path": str(binary_path)},
        )

    return True


def find_binary(binary_name: str) -> Path:
    """Find and validate a binary in the system PATH.

    Args:
        binary_name: Name of the binary to find (e.g., "git", "python")

    Returns:
        Path to the validated binary

    Raises:
        SecurityError: If binary is not found or validation fails
    """
    binary_path = shutil.which(binary_name)
    if binary_path is None:
        raise SecurityError(
            f"Binary not found in PATH: {binary_name}",
            context={"binary_name": binary_name},
        )

    binary_path_obj = Path(binary_path)
    validate_binary(binary_path_obj, binary_name)
    return binary_path_obj


def set_secure_permissions(path: Path, is_directory: bool = False) -> None:
    """Set secure file or directory permissions.

    This function sets appropriate permissions to prevent unauthorized
    access while allowing necessary operations.

    Permissions:
    - Directories: 0o755 (rwxr-xr-x) - Owner: read/write/execute, Others: read/execute
    - Files: 0o644 (rw-r--r--) - Owner: read/write, Others: read-only

    Args:
        path: Path to the file or directory
        is_directory: Whether the path is a directory

    Raises:
        SecurityError: If unable to set permissions
    """
    try:
        if is_directory:
            # Directory: owner can read/write/execute, others can read/execute
            mode = (
                stat.S_IRUSR
                | stat.S_IWUSR
                | stat.S_IXUSR
                | stat.S_IRGRP
                | stat.S_IXGRP
                | stat.S_IROTH
                | stat.S_IXOTH
            )
        else:
            # File: owner can read/write, others can read
            mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH

        os.chmod(path, mode)
    except OSError as e:
        raise SecurityError(
            f"Failed to set secure permissions on {path}",
            context={
                "path": str(path),
                "is_directory": is_directory,
                "error": str(e),
            },
        ) from e


def validate_filename(filename: str) -> str:
    """Validate and sanitize a filename.

    This function ensures filenames are safe and don't contain
    potentially dangerous characters or patterns.

    Args:
        filename: Filename to validate

    Returns:
        Validated filename

    Raises:
        SecurityError: If filename is invalid or contains dangerous patterns
    """
    if not filename:
        raise SecurityError("Filename cannot be empty")

    # Check for null bytes
    if "\x00" in filename:
        raise SecurityError(
            "Null bytes not allowed in filenames",
            context={"filename": filename},
        )

    # Check for path separators
    if "/" in filename or "\\" in filename:
        raise SecurityError(
            "Path separators not allowed in filenames",
            context={"filename": filename},
        )

    # Check for special names
    dangerous_names = {".", "..", "~"}
    if filename in dangerous_names:
        raise SecurityError(
            f"Dangerous filename: {filename}",
            context={"filename": filename},
        )

    # Check length
    if len(filename) > 255:
        raise SecurityError(
            "Filename too long (max 255 characters)",
            context={"filename": filename[:50], "length": len(filename)},
        )

    return filename
