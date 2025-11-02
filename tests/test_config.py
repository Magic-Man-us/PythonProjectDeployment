"""Tests for configuration management."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from pydantic import ValidationError
from python_project_deployment.config import (
    ScaffolderSettings,
    SecurityLevel,
    load_settings,
    merge_cli_with_settings,
)
from python_project_deployment.exceptions import ConfigurationError


class TestSecurityLevel:
    """Test SecurityLevel enum."""

    def test_security_level_values(self):
        """Test that SecurityLevel has the expected values."""
        assert SecurityLevel.LOW == "LOW"
        assert SecurityLevel.MEDIUM == "MEDIUM"
        assert SecurityLevel.HIGH == "HIGH"

    def test_security_level_from_string(self):
        """Test creating SecurityLevel from string."""
        assert SecurityLevel("LOW") == SecurityLevel.LOW
        assert SecurityLevel("MEDIUM") == SecurityLevel.MEDIUM
        assert SecurityLevel("HIGH") == SecurityLevel.HIGH


class TestScaffolderSettings:
    """Test ScaffolderSettings configuration."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = ScaffolderSettings()
        assert settings.timeout_git == 30
        assert settings.timeout_install == 600
        assert settings.timeout_test == 300
        assert settings.timeout_docs == 180
        assert settings.validate_binaries is True
        assert settings.log_level == "INFO"
        assert settings.log_file is None

    def test_environment_variable_prefix(self):
        """Test that environment variables use SCAFFOLD_ prefix."""
        # Set environment variable
        os.environ["SCAFFOLD_TIMEOUT_GIT"] = "60"
        try:
            settings = ScaffolderSettings()
            assert settings.timeout_git == 60
        finally:
            # Clean up
            del os.environ["SCAFFOLD_TIMEOUT_GIT"]

    def test_custom_timeout_values(self):
        """Test setting custom timeout values."""
        settings = ScaffolderSettings(
            timeout_git=60, timeout_install=900, timeout_test=600, timeout_docs=300
        )
        assert settings.timeout_git == 60
        assert settings.timeout_install == 900
        assert settings.timeout_test == 600
        assert settings.timeout_docs == 300

    def test_timeout_validation_min(self):
        """Test that timeout values respect minimum constraints."""
        with pytest.raises(ValidationError):
            ScaffolderSettings(timeout_git=0)
        with pytest.raises(ValidationError):
            ScaffolderSettings(timeout_install=30)
        with pytest.raises(ValidationError):
            ScaffolderSettings(timeout_test=10)
        with pytest.raises(ValidationError):
            ScaffolderSettings(timeout_docs=10)

    def test_timeout_validation_max(self):
        """Test that timeout values respect maximum constraints."""
        with pytest.raises(ValidationError):
            ScaffolderSettings(timeout_git=500)
        with pytest.raises(ValidationError):
            ScaffolderSettings(timeout_install=5000)
        with pytest.raises(ValidationError):
            ScaffolderSettings(timeout_test=2000)
        with pytest.raises(ValidationError):
            ScaffolderSettings(timeout_docs=1000)

    def test_validate_binaries_flag(self):
        """Test validate_binaries configuration."""
        settings = ScaffolderSettings(validate_binaries=False)
        assert settings.validate_binaries is False

        settings = ScaffolderSettings(validate_binaries=True)
        assert settings.validate_binaries is True

    def test_log_level_validation(self):
        """Test log level validation."""
        # Valid log levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = ScaffolderSettings(log_level=level)
            assert settings.log_level == level

        # Case insensitive
        settings = ScaffolderSettings(log_level="info")
        assert settings.log_level == "INFO"

        # Invalid log level
        with pytest.raises(ConfigurationError) as exc_info:
            ScaffolderSettings(log_level="INVALID")
        assert "Invalid log level" in str(exc_info.value)

    def test_log_file_none(self):
        """Test that log_file can be None."""
        settings = ScaffolderSettings()
        assert settings.log_file is None

    def test_log_file_path(self):
        """Test setting log file path."""
        with TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            settings = ScaffolderSettings(log_file=log_file)
            assert settings.log_file == log_file

    def test_log_file_creates_directory(self):
        """Test that log file validator creates parent directory."""
        with TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            log_file = log_dir / "test.log"
            # Directory doesn't exist yet
            assert not log_dir.exists()
            # Creating settings should create the directory
            settings = ScaffolderSettings(log_file=log_file)
            assert log_dir.exists()
            assert log_dir.is_dir()
            assert settings.log_file == log_file

    def test_get_timeout_for_operation(self):
        """Test get_timeout_for_operation method."""
        settings = ScaffolderSettings()
        assert settings.get_timeout_for_operation("git") == 30
        assert settings.get_timeout_for_operation("install") == 600
        assert settings.get_timeout_for_operation("test") == 300
        assert settings.get_timeout_for_operation("docs") == 180

    def test_get_timeout_for_invalid_operation(self):
        """Test get_timeout_for_operation with invalid operation."""
        settings = ScaffolderSettings()
        with pytest.raises(ConfigurationError) as exc_info:
            settings.get_timeout_for_operation("invalid")
        assert "Unknown operation" in str(exc_info.value)
        assert "invalid" in str(exc_info.value)


class TestLoadSettings:
    """Test load_settings function."""

    def test_load_settings_default(self):
        """Test loading settings with defaults."""
        settings = load_settings()
        assert isinstance(settings, ScaffolderSettings)
        assert settings.timeout_git == 30

    def test_load_settings_from_env_file(self):
        """Test loading settings from .env file."""
        with TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / "test.env"
            env_file.write_text("SCAFFOLD_TIMEOUT_GIT=90\nSCAFFOLD_LOG_LEVEL=DEBUG\n")

            settings = load_settings(env_file=env_file)
            assert settings.timeout_git == 90
            assert settings.log_level == "DEBUG"

    def test_load_settings_env_variables_override(self):
        """Test that environment variables override .env file."""
        with TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / "test.env"
            env_file.write_text("SCAFFOLD_TIMEOUT_GIT=90\n")

            # Set environment variable
            os.environ["SCAFFOLD_TIMEOUT_GIT"] = "120"
            try:
                settings = load_settings(env_file=env_file)
                # Environment variable should take precedence
                assert settings.timeout_git == 120
            finally:
                del os.environ["SCAFFOLD_TIMEOUT_GIT"]

    def test_load_settings_invalid_env_file(self):
        """Test loading settings with non-existent .env file."""
        # Non-existent file should not raise error, just use defaults
        settings = load_settings(env_file=Path("/nonexistent/file.env"))
        assert isinstance(settings, ScaffolderSettings)


class TestMergeCliWithSettings:
    """Test merge_cli_with_settings function."""

    def test_merge_empty_cli_args(self):
        """Test merging with empty CLI arguments."""
        # Clean up any environment variables from previous tests
        env_vars_to_clean = [k for k in os.environ.keys() if k.startswith("SCAFFOLD_")]
        for var in env_vars_to_clean:
            del os.environ[var]

        settings = ScaffolderSettings()
        cli_args: dict[str, None] = {}
        merged = merge_cli_with_settings(cli_args, settings)
        assert merged["timeout_git"] == 30
        assert merged["log_level"] == "INFO"

    def test_merge_cli_overrides_settings(self):
        """Test that CLI arguments override settings."""
        settings = ScaffolderSettings(timeout_git=30)
        cli_args = {"timeout_git": 60}
        merged = merge_cli_with_settings(cli_args, settings)
        assert merged["timeout_git"] == 60

    def test_merge_none_values_ignored(self):
        """Test that None values in CLI args don't override settings."""
        settings = ScaffolderSettings(timeout_git=30)
        cli_args = {"timeout_git": None, "log_level": "DEBUG"}
        merged = merge_cli_with_settings(cli_args, settings)
        assert merged["timeout_git"] == 30  # Not overridden
        assert merged["log_level"] == "DEBUG"  # Overridden

    def test_merge_preserves_all_settings(self):
        """Test that merge preserves all settings fields."""
        settings = ScaffolderSettings()
        cli_args = {"timeout_git": 60}
        merged = merge_cli_with_settings(cli_args, settings)
        # Check all fields are present
        assert "timeout_git" in merged
        assert "timeout_install" in merged
        assert "timeout_test" in merged
        assert "timeout_docs" in merged
        assert "validate_binaries" in merged
        assert "log_level" in merged
        assert "log_file" in merged


class TestConfigurationIntegration:
    """Integration tests for configuration management."""

    def test_full_configuration_flow(self):
        """Test complete configuration flow: .env -> env vars -> CLI."""
        with TemporaryDirectory() as tmpdir:
            # Create .env file
            env_file = Path(tmpdir) / "test.env"
            env_file.write_text(
                "SCAFFOLD_TIMEOUT_GIT=45\nSCAFFOLD_TIMEOUT_INSTALL=700\nSCAFFOLD_LOG_LEVEL=DEBUG\n"
            )

            # Load settings from .env
            settings = load_settings(env_file=env_file)
            assert settings.timeout_git == 45
            assert settings.timeout_install == 700
            assert settings.log_level == "DEBUG"

            # Simulate CLI override
            cli_args = {"timeout_git": 120}
            merged = merge_cli_with_settings(cli_args, settings)
            assert merged["timeout_git"] == 120  # CLI override
            assert merged["timeout_install"] == 700  # From .env
            assert merged["log_level"] == "DEBUG"  # From .env

    def test_configuration_precedence(self):
        """Test that configuration precedence is correct: CLI > env > .env > defaults."""
        with TemporaryDirectory() as tmpdir:
            # 1. Start with .env file
            env_file = Path(tmpdir) / "test.env"
            env_file.write_text("SCAFFOLD_TIMEOUT_GIT=50\n")

            # 2. Set environment variable (higher precedence than .env)
            os.environ["SCAFFOLD_TIMEOUT_GIT"] = "80"
            try:
                settings = load_settings(env_file=env_file)
                assert settings.timeout_git == 80  # Env var wins

                # 3. CLI override (highest precedence)
                cli_args = {"timeout_git": 120}
                merged = merge_cli_with_settings(cli_args, settings)
                assert merged["timeout_git"] == 120  # CLI wins
            finally:
                del os.environ["SCAFFOLD_TIMEOUT_GIT"]
