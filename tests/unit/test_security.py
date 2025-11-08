"""Tests for security utilities."""

import stat
import tempfile
from pathlib import Path

import pytest

from python_project_deployment.exceptions import SecurityError
from python_project_deployment.security import (
    find_binary,
    sanitize_template_value,
    set_secure_permissions,
    validate_binary,
    validate_filename,
    validate_path_traversal,
)


class TestValidatePathTraversal:
    """Test path traversal validation."""

    def test_valid_path_within_base(self):
        """Test that valid paths within base are accepted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            subdir = base / "subdir"
            subdir.mkdir()

            result = validate_path_traversal(Path("subdir"), base)
            assert result == subdir.resolve()

    def test_reject_parent_directory_traversal(self):
        """Test that .. paths are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "project"
            base.mkdir()

            with pytest.raises(SecurityError) as exc_info:
                validate_path_traversal(Path(".."), base)
            assert "Path traversal attempt detected" in str(exc_info.value)

    def test_reject_absolute_path_escape(self):
        """Test that absolute paths outside base are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "project"
            base.mkdir()

            with pytest.raises(SecurityError):
                validate_path_traversal(Path("/etc/passwd"), base)

    def test_reject_symlink_escape(self):
        """Test that symlinks pointing outside base are rejected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "project"
            base.mkdir()

            # Create a symlink pointing outside
            link = base / "escape"
            target = Path(tmpdir) / "outside"
            target.mkdir()

            try:
                link.symlink_to(target)

                with pytest.raises(SecurityError):
                    validate_path_traversal(link, base)
            except OSError:
                # Skip test if symlinking not supported
                pytest.skip("Symlinks not supported on this platform")

    def test_nested_path_within_base(self):
        """Test that nested paths within base are accepted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            nested = base / "a" / "b" / "c"
            nested.mkdir(parents=True)

            result = validate_path_traversal(Path("a/b/c"), base)
            assert result == nested.resolve()


class TestSanitizeTemplateValue:
    """Test template value sanitization."""

    def test_valid_string_unchanged(self):
        """Test that valid strings pass through unchanged."""
        value = "valid_package_name"
        assert sanitize_template_value(value) == value

    def test_remove_control_characters(self):
        """Test that control characters are removed."""
        value = "test\x01\x02\x03value"
        result = sanitize_template_value(value)
        assert result == "testvalue"

    def test_preserve_whitespace(self):
        """Test that tabs, newlines, and spaces are preserved."""
        value = "test\ttab\nnewline\rreturn space"
        result = sanitize_template_value(value)
        assert "\t" in result
        assert "\n" in result
        assert "\r" in result
        assert " " in result

    def test_reject_null_bytes(self):
        """Test that null bytes raise SecurityError."""
        value = "test\x00null"
        with pytest.raises(SecurityError) as exc_info:
            sanitize_template_value(value)
        assert "Null bytes not allowed" in str(exc_info.value)

    def test_reject_excessive_length(self):
        """Test that values exceeding max_length raise SecurityError."""
        value = "a" * 1001
        with pytest.raises(SecurityError) as exc_info:
            sanitize_template_value(value)
        assert "exceeds maximum length" in str(exc_info.value)

    def test_custom_max_length(self):
        """Test custom max_length parameter."""
        value = "a" * 50
        # Should pass with default length
        sanitize_template_value(value)

        # Should fail with custom short length
        with pytest.raises(SecurityError):
            sanitize_template_value(value, max_length=10)

    def test_reject_non_string_type(self):
        """Test that non-string values raise SecurityError."""
        with pytest.raises(SecurityError) as exc_info:
            sanitize_template_value(123)  # type: ignore
        assert "must be string" in str(exc_info.value)


class TestValidateBinary:
    """Test binary validation."""

    def test_valid_binary(self):
        """Test that valid binaries pass validation."""
        # Use a system binary that should exist
        python_path = Path("/usr/bin/python3")
        if python_path.exists():
            result = validate_binary(python_path, "python3")
            assert result is True
        else:
            pytest.skip("python3 not found at /usr/bin/python3")

    def test_reject_nonexistent_binary(self):
        """Test that nonexistent binaries raise SecurityError."""
        fake_path = Path("/nonexistent/binary")
        with pytest.raises(SecurityError) as exc_info:
            validate_binary(fake_path, "binary")
        assert "Binary not found" in str(exc_info.value)

    def test_reject_directory_as_binary(self):
        """Test that directories raise SecurityError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)
            with pytest.raises(SecurityError) as exc_info:
                validate_binary(dir_path, "test")
            assert "not a file" in str(exc_info.value)

    def test_reject_non_executable(self):
        """Test that non-executable files raise SecurityError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test"
            file_path.touch()
            # Make it non-executable
            file_path.chmod(0o644)

            with pytest.raises(SecurityError) as exc_info:
                validate_binary(file_path, "test")
            assert "not executable" in str(exc_info.value)

    def test_reject_name_mismatch(self):
        """Test that name mismatches raise SecurityError."""
        # Use ls as example - it exists and is executable
        ls_path = Path("/bin/ls")
        if ls_path.exists():
            with pytest.raises(SecurityError) as exc_info:
                validate_binary(ls_path, "wrong_name")
            assert "name mismatch" in str(exc_info.value)
        else:
            pytest.skip("/bin/ls not found")


class TestFindBinary:
    """Test finding binaries in PATH."""

    def test_find_existing_binary(self):
        """Test finding an existing binary."""
        # Python should always be available
        try:
            result = find_binary("python3")
            assert result.exists()
            assert result.is_file()
            assert result.name == "python3"
        except SecurityError:
            pytest.skip("python3 not found in PATH")

    def test_reject_nonexistent_binary(self):
        """Test that nonexistent binaries raise SecurityError."""
        with pytest.raises(SecurityError) as exc_info:
            find_binary("nonexistent_binary_12345")
        assert "not found in PATH" in str(exc_info.value)


class TestSetSecurePermissions:
    """Test setting secure file permissions."""

    def test_set_file_permissions(self):
        """Test setting permissions on a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            file_path.touch()

            set_secure_permissions(file_path, is_directory=False)

            # Check permissions: 0o644 (rw-r--r--)
            mode = file_path.stat().st_mode
            assert mode & stat.S_IRUSR  # Owner read
            assert mode & stat.S_IWUSR  # Owner write
            assert not (mode & stat.S_IXUSR)  # Owner no execute
            assert mode & stat.S_IRGRP  # Group read
            assert not (mode & stat.S_IWGRP)  # Group no write
            assert mode & stat.S_IROTH  # Other read
            assert not (mode & stat.S_IWOTH)  # Other no write

    def test_set_directory_permissions(self):
        """Test setting permissions on a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "testdir"
            dir_path.mkdir()

            set_secure_permissions(dir_path, is_directory=True)

            # Check permissions: 0o755 (rwxr-xr-x)
            mode = dir_path.stat().st_mode
            assert mode & stat.S_IRUSR  # Owner read
            assert mode & stat.S_IWUSR  # Owner write
            assert mode & stat.S_IXUSR  # Owner execute
            assert mode & stat.S_IRGRP  # Group read
            assert not (mode & stat.S_IWGRP)  # Group no write
            assert mode & stat.S_IXGRP  # Group execute
            assert mode & stat.S_IROTH  # Other read
            assert not (mode & stat.S_IWOTH)  # Other no write
            assert mode & stat.S_IXOTH  # Other execute

    def test_error_on_nonexistent_path(self):
        """Test that setting permissions on nonexistent path raises error."""
        fake_path = Path("/nonexistent/path")
        with pytest.raises(SecurityError):
            set_secure_permissions(fake_path)


class TestValidateFilename:
    """Test filename validation."""

    def test_valid_filename(self):
        """Test that valid filenames are accepted."""
        valid_names = [
            "file.txt",
            "my-file_123.py",
            "README.md",
            "a" * 255,  # Max length
        ]
        for name in valid_names:
            result = validate_filename(name)
            assert result == name

    def test_reject_empty_filename(self):
        """Test that empty filenames raise SecurityError."""
        with pytest.raises(SecurityError) as exc_info:
            validate_filename("")
        assert "cannot be empty" in str(exc_info.value)

    def test_reject_null_bytes(self):
        """Test that filenames with null bytes raise SecurityError."""
        with pytest.raises(SecurityError) as exc_info:
            validate_filename("file\x00name")
        assert "Null bytes not allowed" in str(exc_info.value)

    def test_reject_path_separators(self):
        """Test that path separators raise SecurityError."""
        with pytest.raises(SecurityError) as exc_info:
            validate_filename("path/to/file")
        assert "Path separators not allowed" in str(exc_info.value)

        with pytest.raises(SecurityError):
            validate_filename("path\\to\\file")

    def test_reject_dangerous_names(self):
        """Test that dangerous names raise SecurityError."""
        dangerous = [".", "..", "~"]
        for name in dangerous:
            with pytest.raises(SecurityError) as exc_info:
                validate_filename(name)
            assert "Dangerous filename" in str(exc_info.value)

    def test_reject_excessive_length(self):
        """Test that filenames > 255 chars raise SecurityError."""
        long_name = "a" * 256
        with pytest.raises(SecurityError) as exc_info:
            validate_filename(long_name)
        assert "too long" in str(exc_info.value)
