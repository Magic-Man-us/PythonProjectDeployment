"""Transaction and rollback management for scaffolding operations.

This module provides rollback capability for scaffolding operations. When an error
occurs during scaffolding, registered rollback operations are executed in reverse
order (LIFO) to clean up partially created artifacts.
"""

import logging
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

from python_project_deployment.exceptions import RollbackError

logger = logging.getLogger(__name__)


class RollbackManager:
    """Manages rollback operations for failed scaffolding.

    This class provides transaction-like behavior for scaffolding operations.
    Operations can register rollback callbacks that will be executed in reverse
    order (LIFO) if scaffolding fails.

    Example:
        >>> with RollbackManager(Path("/path/to/project")) as rollback:
        ...     create_directory(some_dir)
        ...     rollback.register_directory_removal(some_dir)
        ...     # If an error occurs, some_dir will be removed

    Attributes:
        destination: The destination path for the scaffolding operation
        operations: List of rollback operations (callables) in LIFO order
        _in_rollback: Flag to prevent recursive rollback
    """

    def __init__(self, destination: Path) -> None:
        """Initialize the rollback manager.

        Args:
            destination: The destination path for scaffolding
        """
        self.destination = destination
        self.operations: list[Callable[[], None]] = []
        self._in_rollback = False

    def register_operation(self, rollback_fn: Callable[[], None]) -> None:
        """Register a rollback operation.

        The operation will be executed if rollback is triggered. Operations
        are executed in reverse order (LIFO) during rollback.

        Args:
            rollback_fn: Callable that performs the rollback operation.
                        Should not raise exceptions if already rolled back.
        """
        if not callable(rollback_fn):
            raise TypeError(f"Rollback operation must be callable, got {type(rollback_fn)}")
        self.operations.append(rollback_fn)
        logger.debug(f"Registered rollback operation: {rollback_fn.__name__}")

    def register_directory_removal(self, directory: Path) -> None:
        """Register a directory for removal on rollback.

        Args:
            directory: Directory to remove during rollback
        """

        def remove_dir() -> None:
            try:
                if directory.exists() and directory.is_dir():
                    shutil.rmtree(directory)
                    logger.info(f"Rollback: Removed directory {directory}")
            except Exception as e:
                logger.warning(f"Failed to remove directory {directory}: {e}")

        self.register_operation(remove_dir)

    def register_file_removal(self, file_path: Path) -> None:
        """Register a file for removal on rollback.

        Args:
            file_path: File to remove during rollback
        """

        def remove_file() -> None:
            try:
                if file_path.exists() and file_path.is_file():
                    file_path.unlink()
                    logger.info(f"Rollback: Removed file {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove file {file_path}: {e}")

        self.register_operation(remove_file)

    def register_git_cleanup(self, repo_path: Path) -> None:
        """Register git repository cleanup on rollback.

        Args:
            repo_path: Path to git repository to clean up
        """

        def cleanup_git() -> None:
            try:
                git_dir = repo_path / ".git"
                if git_dir.exists() and git_dir.is_dir():
                    shutil.rmtree(git_dir)
                    logger.info(f"Rollback: Removed .git directory from {repo_path}")
            except Exception as e:
                logger.warning(f"Failed to remove .git directory: {e}")

        self.register_operation(cleanup_git)

    def execute_rollback(self) -> None:
        """Execute all registered rollback operations in reverse order.

        Operations are executed in LIFO order (last registered, first executed).
        If a rollback operation fails, the error is logged and rollback continues
        with the remaining operations.

        Raises:
            RollbackError: If rollback is attempted while already in rollback
        """
        if self._in_rollback:
            raise RollbackError(
                "Recursive rollback detected",
                context={"destination": str(self.destination)},
            )

        if not self.operations:
            logger.debug("No rollback operations to execute")
            return

        self._in_rollback = True
        logger.info(f"Starting rollback of {len(self.operations)} operations")

        failures: list[dict[str, Any]] = []

        # Execute in reverse order (LIFO)
        for i, operation in enumerate(reversed(self.operations)):
            operation_index = len(self.operations) - 1 - i
            try:
                logger.debug(
                    f"Executing rollback operation {operation_index}: {operation.__name__}"
                )
                operation()
            except Exception as e:
                logger.error(f"Rollback operation {operation_index} failed: {e}")
                failures.append(
                    {
                        "index": operation_index,
                        "operation": operation.__name__,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                )
                # Continue with remaining rollback operations

        self._in_rollback = False

        if failures:
            logger.warning(f"Rollback completed with {len(failures)} failures")
            raise RollbackError(
                f"Rollback completed with {len(failures)} failed operations",
                context={
                    "destination": str(self.destination),
                    "total_operations": len(self.operations),
                    "failures": failures,
                },
            )
        else:
            logger.info("Rollback completed successfully")

    def clear_operations(self) -> None:
        """Clear all registered rollback operations.

        This should be called after successful completion of scaffolding
        to prevent rollback of successfully created artifacts.
        """
        count = len(self.operations)
        self.operations.clear()
        logger.debug(f"Cleared {count} rollback operations")

    def __enter__(self) -> "RollbackManager":
        """Enter context manager.

        Returns:
            Self for use in with statement
        """
        logger.debug(f"Entered rollback context for {self.destination}")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit context manager, executing rollback if an exception occurred.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            None (always propagates exceptions)
        """
        if exc_type is not None:
            logger.error(f"Exception occurred: {exc_type.__name__}: {exc_val}")
            logger.info("Executing rollback due to exception")
            try:
                self.execute_rollback()
            except RollbackError as e:
                # Log the rollback error but propagate the original exception
                logger.error(f"Rollback error: {e}")
        else:
            # Success - clear rollback operations
            logger.debug("Scaffolding completed successfully, clearing rollback operations")
            self.clear_operations()

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return (
            f"RollbackManager(destination={self.destination!r}, "
            f"operations={len(self.operations)}, "
            f"in_rollback={self._in_rollback})"
        )

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"RollbackManager with {len(self.operations)} operations for {self.destination}"
