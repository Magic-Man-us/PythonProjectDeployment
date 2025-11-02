"""Tests for rollback manager module."""

from unittest.mock import patch

import pytest
from python_project_deployment.exceptions import RollbackError
from python_project_deployment.rollback import RollbackManager


class TestRollbackManager:
    """Tests for RollbackManager class."""

    @pytest.fixture
    def temp_dest(self, tmp_path):
        """Create a temporary destination path."""
        return tmp_path / "test_project"

    @pytest.fixture
    def manager(self, temp_dest):
        """Create a rollback manager instance."""
        return RollbackManager(temp_dest)

    def test_initialization(self, manager, temp_dest):
        """Test that manager can be initialized."""
        assert manager.destination == temp_dest
        assert manager.operations == []
        assert not manager._in_rollback

    def test_register_operation(self, manager):
        """Test registering a rollback operation."""
        called = []

        def mock_operation():
            called.append(True)

        manager.register_operation(mock_operation)
        assert len(manager.operations) == 1

        # Execute the operation
        manager.operations[0]()
        assert called == [True]

    def test_register_operation_not_callable(self, manager):
        """Test that non-callable operation raises TypeError."""
        with pytest.raises(TypeError, match="must be callable"):
            manager.register_operation("not callable")  # type: ignore

    def test_register_multiple_operations(self, manager):
        """Test registering multiple operations."""
        called = []

        def op1():
            called.append(1)

        def op2():
            called.append(2)

        def op3():
            called.append(3)

        manager.register_operation(op1)
        manager.register_operation(op2)
        manager.register_operation(op3)

        assert len(manager.operations) == 3

    def test_register_directory_removal(self, manager, tmp_path):
        """Test registering directory removal."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        assert test_dir.exists()

        manager.register_directory_removal(test_dir)
        assert len(manager.operations) == 1

        # Execute rollback
        manager.execute_rollback()
        assert not test_dir.exists()

    def test_register_directory_removal_already_removed(self, manager, tmp_path):
        """Test directory removal when directory doesn't exist."""
        test_dir = tmp_path / "nonexistent"

        manager.register_directory_removal(test_dir)
        # Should not raise even if directory doesn't exist
        manager.execute_rollback()

    def test_register_file_removal(self, manager, tmp_path):
        """Test registering file removal."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()

        manager.register_file_removal(test_file)
        assert len(manager.operations) == 1

        # Execute rollback
        manager.execute_rollback()
        assert not test_file.exists()

    def test_register_file_removal_already_removed(self, manager, tmp_path):
        """Test file removal when file doesn't exist."""
        test_file = tmp_path / "nonexistent.txt"

        manager.register_file_removal(test_file)
        # Should not raise even if file doesn't exist
        manager.execute_rollback()

    def test_register_git_cleanup(self, manager, tmp_path):
        """Test registering git cleanup."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("test")

        assert git_dir.exists()

        manager.register_git_cleanup(repo_path)
        manager.execute_rollback()

        assert not git_dir.exists()
        assert repo_path.exists()  # Repo directory should remain

    def test_execute_rollback_lifo_order(self, manager):
        """Test that rollback operations execute in LIFO order."""
        execution_order = []

        def op1():
            execution_order.append(1)

        def op2():
            execution_order.append(2)

        def op3():
            execution_order.append(3)

        manager.register_operation(op1)
        manager.register_operation(op2)
        manager.register_operation(op3)

        manager.execute_rollback()

        # Should execute in reverse order: 3, 2, 1
        assert execution_order == [3, 2, 1]

    def test_execute_rollback_no_operations(self, manager):
        """Test rollback with no operations registered."""
        # Should not raise
        manager.execute_rollback()

    def test_execute_rollback_with_failure(self, manager):
        """Test rollback when one operation fails."""
        execution_order = []

        def op1():
            execution_order.append(1)

        def op2():
            execution_order.append(2)
            raise RuntimeError("Operation 2 failed")

        def op3():
            execution_order.append(3)

        manager.register_operation(op1)
        manager.register_operation(op2)
        manager.register_operation(op3)

        with pytest.raises(RollbackError) as exc_info:
            manager.execute_rollback()

        # All operations should execute despite failure
        assert execution_order == [3, 2, 1]
        assert "1 failed operations" in str(exc_info.value)
        assert exc_info.value.context["total_operations"] == 3
        assert len(exc_info.value.context["failures"]) == 1

    def test_execute_rollback_multiple_failures(self, manager):
        """Test rollback with multiple failing operations."""
        execution_order = []

        def op1():
            execution_order.append(1)
            raise RuntimeError("Operation 1 failed")

        def op2():
            execution_order.append(2)

        def op3():
            execution_order.append(3)
            raise ValueError("Operation 3 failed")

        manager.register_operation(op1)
        manager.register_operation(op2)
        manager.register_operation(op3)

        with pytest.raises(RollbackError) as exc_info:
            manager.execute_rollback()

        assert execution_order == [3, 2, 1]
        assert "2 failed operations" in str(exc_info.value)
        assert len(exc_info.value.context["failures"]) == 2

    def test_execute_rollback_recursive_prevention(self, manager):
        """Test that recursive rollback is prevented."""

        def recursive_op():
            manager.execute_rollback()

        manager.register_operation(recursive_op)

        with pytest.raises(RollbackError, match="Recursive rollback detected"):
            manager.execute_rollback()

    def test_clear_operations(self, manager):
        """Test clearing rollback operations."""

        def mock_op():
            pass

        manager.register_operation(mock_op)
        manager.register_operation(mock_op)
        manager.register_operation(mock_op)

        assert len(manager.operations) == 3

        manager.clear_operations()
        assert len(manager.operations) == 0

    def test_context_manager_success(self, manager, tmp_path):
        """Test context manager when no exception occurs."""
        test_file = tmp_path / "test.txt"

        with manager as m:
            assert m is manager
            test_file.write_text("content")
            m.register_file_removal(test_file)

        # File should still exist (rollback not triggered)
        assert test_file.exists()
        assert len(manager.operations) == 0  # Operations cleared

    def test_context_manager_with_exception(self, manager, tmp_path):
        """Test context manager when exception occurs."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        with pytest.raises(ValueError):
            with manager:
                manager.register_file_removal(test_file)
                raise ValueError("Test exception")

        # Rollback should have been executed
        assert not test_file.exists()

    def test_context_manager_rollback_error_logged(self, manager, tmp_path):
        """Test that rollback errors are logged but original exception propagates."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        def failing_rollback():
            raise RuntimeError("Rollback failed")

        with pytest.raises(ValueError) as exc_info:
            with manager:
                manager.register_operation(failing_rollback)
                raise ValueError("Original exception")

        # Original exception should be raised
        assert "Original exception" in str(exc_info.value)

    def test_context_manager_integration(self, manager, tmp_path):
        """Test complete context manager flow with multiple operations."""
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        file1 = tmp_path / "file1.txt"

        dir1.mkdir()
        dir2.mkdir()
        file1.write_text("content")

        with pytest.raises(RuntimeError):
            with manager:
                manager.register_directory_removal(dir1)
                manager.register_directory_removal(dir2)
                manager.register_file_removal(file1)
                raise RuntimeError("Simulate failure")

        # All should be rolled back
        assert not dir1.exists()
        assert not dir2.exists()
        assert not file1.exists()

    def test_str_representation(self, manager):
        """Test string representation."""

        def mock_op():
            pass

        manager.register_operation(mock_op)
        manager.register_operation(mock_op)

        str_repr = str(manager)
        assert "2 operations" in str_repr
        assert str(manager.destination) in str_repr

    def test_repr_representation(self, manager):
        """Test repr representation."""

        def mock_op():
            pass

        manager.register_operation(mock_op)

        repr_str = repr(manager)
        assert "RollbackManager" in repr_str
        assert "operations=1" in repr_str
        assert "in_rollback=False" in repr_str

    def test_mixed_rollback_operations(self, manager, tmp_path):
        """Test mix of different rollback operations."""
        # Create test artifacts
        test_dir = tmp_path / "test_dir"
        test_file = tmp_path / "test.txt"
        repo_dir = tmp_path / "repo"
        git_dir = repo_dir / ".git"

        test_dir.mkdir()
        test_file.write_text("content")
        repo_dir.mkdir()
        git_dir.mkdir()

        # Register removals
        manager.register_directory_removal(test_dir)
        manager.register_file_removal(test_file)
        manager.register_git_cleanup(repo_dir)

        # Execute rollback
        manager.execute_rollback()

        # Verify all were removed
        assert not test_dir.exists()
        assert not test_file.exists()
        assert not git_dir.exists()
        assert repo_dir.exists()

    def test_rollback_partial_completion(self, manager, tmp_path):
        """Test rollback with some operations already completed."""
        # Create only some of the artifacts
        test_file = tmp_path / "exists.txt"
        test_file.write_text("content")
        nonexistent_file = tmp_path / "nonexistent.txt"

        manager.register_file_removal(nonexistent_file)  # Doesn't exist
        manager.register_file_removal(test_file)  # Exists

        # Should not raise even though first file doesn't exist
        manager.execute_rollback()

        assert not test_file.exists()

    @patch("python_project_deployment.rollback.logger")
    def test_logging_during_rollback(self, mock_logger, manager):
        """Test that appropriate logging occurs during rollback."""

        def mock_op():
            pass

        manager.register_operation(mock_op)
        manager.execute_rollback()

        # Verify logging calls
        mock_logger.info.assert_called()
        mock_logger.debug.assert_called()

    @patch("python_project_deployment.rollback.logger")
    def test_logging_on_failure(self, mock_logger, manager):
        """Test logging when rollback operation fails."""

        def failing_op():
            raise RuntimeError("Test failure")

        manager.register_operation(failing_op)

        with pytest.raises(RollbackError):
            manager.execute_rollback()

        mock_logger.error.assert_called()
        mock_logger.warning.assert_called()
