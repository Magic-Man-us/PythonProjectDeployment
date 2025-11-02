"""Tests for custom exception hierarchy."""

import pytest
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


class TestExceptionHierarchy:
    """Test exception inheritance and hierarchy."""

    def test_all_exceptions_inherit_from_scaffolder_error(self):
        """Verify all custom exceptions inherit from ScaffolderError."""
        exception_classes = [
            ValidationError,
            SecurityError,
            SubprocessError,
            FileSystemError,
            RollbackError,
            ConfigurationError,
            PrerequisiteError,
        ]
        for exc_class in exception_classes:
            assert issubclass(exc_class, ScaffolderError)
            assert issubclass(exc_class, Exception)

    def test_scaffolder_error_is_exception(self):
        """Verify ScaffolderError inherits from Exception."""
        assert issubclass(ScaffolderError, Exception)


class TestScaffolderError:
    """Test base ScaffolderError functionality."""

    def test_basic_error_creation(self):
        """Test creating error with just a message."""
        error = ScaffolderError("Test error")
        assert str(error) == "Test error"
        assert error.context == {}

    def test_error_with_context(self):
        """Test creating error with context dictionary."""
        context = {"package": "test_pkg", "path": "/tmp/test"}
        error = ScaffolderError("Test error", context=context)
        assert error.context == context
        assert "package='test_pkg'" in str(error)
        assert "path='/tmp/test'" in str(error)

    def test_error_context_in_string_representation(self):
        """Test that context appears in string representation."""
        error = ScaffolderError("Error occurred", context={"key": "value"})
        error_str = str(error)
        assert "Error occurred" in error_str
        assert "Context:" in error_str
        assert "key='value'" in error_str

    def test_error_repr(self):
        """Test __repr__ method for debugging."""
        error = ScaffolderError("Test", context={"a": 1})
        repr_str = repr(error)
        assert "ScaffolderError" in repr_str
        assert "'Test'" in repr_str
        assert "context=" in repr_str

    def test_error_without_context_no_context_in_str(self):
        """Test that errors without context don't show context in string."""
        error = ScaffolderError("Simple error")
        error_str = str(error)
        assert error_str == "Simple error"
        assert "Context:" not in error_str


class TestValidationError:
    """Test ValidationError functionality."""

    def test_validation_error_creation(self):
        """Test creating validation error."""
        error = ValidationError("Invalid package name")
        assert isinstance(error, ScaffolderError)
        assert "Invalid package name" in str(error)

    def test_validation_error_with_context(self):
        """Test validation error with field context."""
        context = {"field": "package_name", "value": "invalid-name"}
        error = ValidationError("Invalid value", context=context)
        assert error.context["field"] == "package_name"


class TestSecurityError:
    """Test SecurityError functionality."""

    def test_security_error_creation(self):
        """Test creating security error."""
        error = SecurityError("Path traversal detected")
        assert isinstance(error, ScaffolderError)
        assert "Path traversal" in str(error)

    def test_security_error_with_context(self):
        """Test security error with attack details."""
        context = {"path": "../etc/passwd", "base": "/tmp/project"}
        error = SecurityError("Security violation", context=context)
        assert "../etc/passwd" in str(error)


class TestSubprocessError:
    """Test SubprocessError functionality."""

    def test_subprocess_error_creation(self):
        """Test creating subprocess error with result."""

        # Create a mock result object
        class MockResult:
            command = ["git", "clone", "repo"]
            returncode = 128
            stdout = "Cloning..."
            stderr = "fatal: repository not found"
            duration = 2.5
            timed_out = False

        result = MockResult()
        error = SubprocessError("Git clone failed", result=result)
        assert isinstance(error, ScaffolderError)
        assert error.result == result

    def test_subprocess_error_string_includes_details(self):
        """Test that subprocess error string includes execution details."""

        class MockResult:
            command = ["ls", "-la"]
            returncode = 1
            stdout = ""
            stderr = "No such file"
            duration = 0.1
            timed_out = False

        result = MockResult()
        error = SubprocessError("Command failed", result=result)
        error_str = str(error)
        assert "Command failed" in error_str
        assert "ls -la" in error_str
        assert "Exit code: 1" in error_str
        assert "Duration: 0.10s" in error_str
        assert "Timed out: False" in error_str

    def test_subprocess_error_with_timeout(self):
        """Test subprocess error when command times out."""

        class MockResult:
            command = ["sleep", "1000"]
            returncode = -1
            stdout = ""
            stderr = ""
            duration = 30.0
            timed_out = True

        result = MockResult()
        error = SubprocessError("Command timed out", result=result)
        assert "Timed out: True" in str(error)
        assert error.result.timed_out is True

    def test_subprocess_error_with_context(self):
        """Test subprocess error with additional context."""

        class MockResult:
            command = ["git", "push"]
            returncode = 1
            stdout = ""
            stderr = "Permission denied"
            duration = 1.0
            timed_out = False

        result = MockResult()
        context = {"branch": "main", "remote": "origin"}
        error = SubprocessError("Push failed", result=result, context=context)
        assert error.context["branch"] == "main"


class TestFileSystemError:
    """Test FileSystemError functionality."""

    def test_filesystem_error_creation(self):
        """Test creating filesystem error."""
        error = FileSystemError("Permission denied")
        assert isinstance(error, ScaffolderError)
        assert "Permission denied" in str(error)

    def test_filesystem_error_with_context(self):
        """Test filesystem error with path context."""
        context = {"path": "/root/restricted", "operation": "write"}
        error = FileSystemError("Access denied", context=context)
        assert "restricted" in str(error)


class TestRollbackError:
    """Test RollbackError functionality."""

    def test_rollback_error_creation(self):
        """Test creating rollback error."""
        error = RollbackError("Failed to rollback changes")
        assert isinstance(error, ScaffolderError)
        assert "rollback" in str(error)

    def test_rollback_error_with_original_error_context(self):
        """Test rollback error preserving original error context."""
        original_context = {"original_error": "Git clone failed"}
        context = {"rollback_step": "remove_directory", **original_context}
        error = RollbackError("Rollback failed", context=context)
        assert error.context["original_error"] == "Git clone failed"
        assert error.context["rollback_step"] == "remove_directory"


class TestConfigurationError:
    """Test ConfigurationError functionality."""

    def test_configuration_error_creation(self):
        """Test creating configuration error."""
        error = ConfigurationError("Invalid timeout value")
        assert isinstance(error, ScaffolderError)
        assert "timeout" in str(error)

    def test_configuration_error_with_context(self):
        """Test configuration error with setting details."""
        context = {"setting": "timeout_git", "value": -1, "min": 1}
        error = ConfigurationError("Invalid configuration", context=context)
        assert "timeout_git" in str(error)


class TestPrerequisiteError:
    """Test PrerequisiteError functionality."""

    def test_prerequisite_error_creation(self):
        """Test creating prerequisite error."""
        error = PrerequisiteError("git not found")
        assert isinstance(error, ScaffolderError)
        assert "git" in str(error)

    def test_prerequisite_error_with_context(self):
        """Test prerequisite error with missing tool context."""
        context = {"tool": "git", "required_version": "2.0+"}
        error = PrerequisiteError("Missing tool", context=context)
        assert "git" in str(error)


class TestExceptionRaising:
    """Test that exceptions can be raised and caught properly."""

    def test_raise_and_catch_scaffolder_error(self):
        """Test raising and catching base ScaffolderError."""
        with pytest.raises(ScaffolderError) as exc_info:
            raise ScaffolderError("Test error", context={"test": True})
        assert "Test error" in str(exc_info.value)
        assert exc_info.value.context["test"] is True

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        with pytest.raises(ValidationError):
            raise ValidationError("Validation failed")

    def test_catch_as_base_exception(self):
        """Test that specific exceptions can be caught as base type."""
        with pytest.raises(ScaffolderError):
            raise SecurityError("Security issue")

    def test_multiple_exception_types(self):
        """Test handling multiple exception types."""
        exceptions_to_test = [
            (ValidationError, "Validation failed"),
            (SecurityError, "Security issue"),
            (SubprocessError, "Subprocess failed", None),
            (FileSystemError, "Filesystem error"),
            (RollbackError, "Rollback failed"),
            (ConfigurationError, "Config error"),
            (PrerequisiteError, "Prerequisite missing"),
        ]

        for exc_data in exceptions_to_test:
            exc_class = exc_data[0]
            message = exc_data[1]
            if len(exc_data) > 2 and exc_class == SubprocessError:
                # SubprocessError requires a result parameter
                class MockResult:
                    command = ["test"]
                    returncode = 1
                    stdout = ""
                    stderr = ""
                    duration = 0.0
                    timed_out = False

                with pytest.raises(exc_class):
                    raise exc_class(message, result=MockResult())
            else:
                with pytest.raises(exc_class):
                    raise exc_class(message)
