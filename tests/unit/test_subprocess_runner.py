"""Tests for subprocess runner module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from python_project_deployment.exceptions import SecurityError, SubprocessError
from python_project_deployment.subprocess_runner import (
    SubprocessResult,
    SubprocessRunner,
    run_command,
)


class TestSubprocessResult:
    """Tests for SubprocessResult model."""

    def test_valid_result(self):
        """Test creating a valid subprocess result."""
        result = SubprocessResult(
            command=["echo", "hello"],
            returncode=0,
            stdout="hello\n",
            stderr="",
            duration=0.1,
            timed_out=False,
        )
        assert result.command == ["echo", "hello"]
        assert result.returncode == 0
        assert result.stdout == "hello\n"
        assert result.duration == 0.1
        assert not result.timed_out

    def test_empty_command_rejected(self):
        """Test that empty command list is rejected."""
        with pytest.raises(ValueError, match="Command list cannot be empty"):
            SubprocessResult(
                command=[],
                returncode=0,
                stdout="",
                stderr="",
                duration=0.1,
                timed_out=False,
            )

    def test_negative_duration_rejected(self):
        """Test that negative duration is rejected."""
        with pytest.raises(ValueError):
            SubprocessResult(
                command=["echo", "hello"],
                returncode=0,
                stdout="",
                stderr="",
                duration=-1.0,
                timed_out=False,
            )

    def test_str_representation(self):
        """Test string representation of result."""
        result = SubprocessResult(
            command=["git", "init"],
            returncode=0,
            stdout="",
            stderr="",
            duration=1.23,
            timed_out=False,
        )
        str_repr = str(result)
        assert "git init" in str_repr
        assert "exit 0" in str_repr
        assert "1.23s" in str_repr

    def test_str_representation_timeout(self):
        """Test string representation for timed out result."""
        result = SubprocessResult(
            command=["sleep", "100"],
            returncode=-1,
            stdout="",
            stderr="",
            duration=30.0,
            timed_out=True,
        )
        str_repr = str(result)
        assert "TIMEOUT" in str_repr


class TestSubprocessRunner:
    """Tests for SubprocessRunner class."""

    @pytest.fixture
    def runner(self):
        """Create a subprocess runner instance."""
        return SubprocessRunner()

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path

    def test_runner_initialization(self, runner):
        """Test that runner can be initialized."""
        assert runner is not None

    def test_successful_command_execution(self, runner, temp_dir):
        """Test executing a successful command."""
        result = runner.run_command(
            command=["echo", "hello"],
            cwd=temp_dir,
            timeout=10,
        )
        assert result.returncode == 0
        assert "hello" in result.stdout
        assert result.duration >= 0
        assert not result.timed_out

    def test_command_with_non_zero_exit(self, runner, temp_dir):
        """Test command that returns non-zero exit code."""
        with pytest.raises(SubprocessError) as exc_info:
            runner.run_command(
                command=["false"],
                cwd=temp_dir,
                timeout=10,
                check=True,
            )
        assert exc_info.value.result.returncode != 0
        assert "failed with exit code" in str(exc_info.value).lower()

    def test_command_non_zero_exit_no_check(self, runner, temp_dir):
        """Test command with non-zero exit when check=False."""
        result = runner.run_command(
            command=["false"],
            cwd=temp_dir,
            timeout=10,
            check=False,
        )
        assert result.returncode != 0
        assert not result.timed_out

    @patch("subprocess.run")
    def test_command_timeout(self, mock_run, runner, temp_dir):
        """Test that timeout is enforced."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["sleep", "100"],
            timeout=1,
            output=b"",
            stderr=b"",
        )

        with pytest.raises(SubprocessError) as exc_info:
            runner.run_command(
                command=["sleep", "100"],
                cwd=temp_dir,
                timeout=1,
            )

        assert exc_info.value.result.timed_out
        assert "timed out" in str(exc_info.value).lower()
        assert exc_info.value.result.returncode == -1

    def test_command_with_stderr(self, runner, temp_dir):
        """Test capturing stderr output."""
        # Create a simple script that writes to stderr
        script_path = temp_dir / "test_stderr.py"
        script_path.write_text("import sys\nsys.stderr.write('error\\n')")

        result = runner.run_command(
            command=["python", str(script_path)],
            cwd=temp_dir,
            timeout=10,
            check=False,
        )
        assert "error" in result.stderr

    def test_working_directory_does_not_exist(self, runner):
        """Test that non-existent working directory is rejected."""
        non_existent = Path("/tmp/does_not_exist_12345")
        with pytest.raises(SecurityError) as exc_info:
            runner.run_command(
                command=["echo", "hello"],
                cwd=non_existent,
                timeout=10,
            )
        assert "does not exist" in str(exc_info.value).lower()

    def test_working_directory_is_file(self, runner, temp_dir):
        """Test that file path is rejected as working directory."""
        file_path = temp_dir / "file.txt"
        file_path.write_text("test")

        with pytest.raises(SecurityError) as exc_info:
            runner.run_command(
                command=["echo", "hello"],
                cwd=file_path,
                timeout=10,
            )
        assert "not a directory" in str(exc_info.value).lower()

    def test_negative_timeout_rejected(self, runner, temp_dir):
        """Test that negative timeout is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.run_command(
                command=["echo", "hello"],
                cwd=temp_dir,
                timeout=-1,
            )
        assert "timeout must be positive" in str(exc_info.value).lower()

    def test_zero_timeout_rejected(self, runner, temp_dir):
        """Test that zero timeout is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.run_command(
                command=["echo", "hello"],
                cwd=temp_dir,
                timeout=0,
            )
        assert "timeout must be positive" in str(exc_info.value).lower()

    def test_capture_output_false(self, runner, temp_dir):
        """Test that capture_output=False works."""
        result = runner.run_command(
            command=["echo", "hello"],
            cwd=temp_dir,
            timeout=10,
            capture_output=False,
        )
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""

    def test_custom_environment_variables(self, runner, temp_dir):
        """Test passing custom environment variables."""
        import os
        import sys

        # Create a simple script that prints an environment variable
        script_path = temp_dir / "test_env.py"
        script_path.write_text("import os\nprint(os.environ.get('CUSTOM_VAR', ''))")

        # Merge custom env with current environment so python is still in PATH
        test_env = os.environ.copy()
        test_env["CUSTOM_VAR"] = "test_value"

        result = runner.run_command(
            command=[sys.executable, str(script_path)],
            cwd=temp_dir,
            timeout=10,
            env=test_env,
        )
        assert "test_value" in result.stdout

    @patch("subprocess.run")
    def test_unexpected_exception_handling(self, mock_run, runner, temp_dir):
        """Test handling of unexpected exceptions during execution."""
        mock_run.side_effect = RuntimeError("Unexpected error")

        with pytest.raises(SubprocessError) as exc_info:
            runner.run_command(
                command=["echo", "hello"],
                cwd=temp_dir,
                timeout=10,
            )

        assert "unexpected error" in str(exc_info.value).lower()
        assert exc_info.value.result.returncode == -1
        assert "RuntimeError" in str(exc_info.value.context.get("error_type", ""))


class TestCommandValidation:
    """Tests for command validation."""

    @pytest.fixture
    def runner(self):
        """Create a subprocess runner instance."""
        return SubprocessRunner()

    def test_empty_command_rejected(self, runner):
        """Test that empty command is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command([])
        assert "empty" in str(exc_info.value).lower()

    def test_command_not_list_rejected(self, runner):
        """Test that non-list command is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command("echo hello")  # type: ignore
        assert "must be a list" in str(exc_info.value).lower()

    def test_command_with_non_string_parts_rejected(self, runner):
        """Test that command with non-string parts is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command(["echo", 123])  # type: ignore
        assert "not a string" in str(exc_info.value).lower()

    def test_command_with_empty_string_rejected(self, runner):
        """Test that command with empty strings is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command(["echo", "", "hello"])
        assert "empty strings" in str(exc_info.value).lower()

    def test_command_with_semicolon_rejected(self, runner):
        """Test that command with semicolon is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command(["echo", "hello; rm -rf /"])
        assert "suspicious characters" in str(exc_info.value).lower()

    def test_command_with_pipe_rejected(self, runner):
        """Test that command with pipe is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command(["echo", "hello | cat"])
        assert "suspicious characters" in str(exc_info.value).lower()

    def test_command_with_ampersand_rejected(self, runner):
        """Test that command with ampersand is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command(["echo", "hello & sleep 10"])
        assert "suspicious characters" in str(exc_info.value).lower()

    def test_command_with_dollar_rejected(self, runner):
        """Test that command with dollar sign is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command(["echo", "$PATH"])
        assert "suspicious characters" in str(exc_info.value).lower()

    def test_command_with_backtick_rejected(self, runner):
        """Test that command with backtick is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command(["echo", "`ls`"])
        assert "suspicious characters" in str(exc_info.value).lower()

    def test_command_with_newline_rejected(self, runner):
        """Test that command with newline is rejected."""
        with pytest.raises(SecurityError) as exc_info:
            runner.validate_command(["echo", "hello\nworld"])
        assert "suspicious characters" in str(exc_info.value).lower()

    def test_valid_command_accepted(self, runner):
        """Test that valid command is accepted."""
        # Should not raise
        runner.validate_command(["git", "init"])
        runner.validate_command(["echo", "hello world"])
        runner.validate_command(["python", "-m", "pytest"])


class TestConvenienceFunction:
    """Tests for module-level run_command function."""

    def test_run_command_function(self, tmp_path):
        """Test the convenience run_command function."""
        result = run_command(
            command=["echo", "test"],
            cwd=tmp_path,
            timeout=10,
        )
        assert result.returncode == 0
        assert "test" in result.stdout

    def test_run_command_function_with_error(self, tmp_path):
        """Test the convenience function with command that fails."""
        with pytest.raises(SubprocessError):
            run_command(
                command=["false"],
                cwd=tmp_path,
                timeout=10,
                check=True,
            )

    def test_run_command_function_no_check(self, tmp_path):
        """Test the convenience function with check=False."""
        result = run_command(
            command=["false"],
            cwd=tmp_path,
            timeout=10,
            check=False,
        )
        assert result.returncode != 0
