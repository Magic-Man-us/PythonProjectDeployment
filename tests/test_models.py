"""Tests for the models module."""

from pathlib import Path

import pytest
from pydantic import ValidationError
from python_project_deployment.models import ProjectConfig


def test_project_config_valid(tmp_path: Path) -> None:
    """Test creating a valid ProjectConfig."""
    config = ProjectConfig(
        package_name="my_package",
        target_dir=tmp_path / "test",
    )

    assert config.package_name == "my_package"
    assert config.target_dir == tmp_path / "test"
    assert config.author_name == "Your Name"
    assert config.author_email == "your.email@example.com"


def test_project_config_invalid_package_name(tmp_path: Path) -> None:
    """Test that invalid package names raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ProjectConfig(
            package_name="123invalid",  # Starts with number
            target_dir=tmp_path / "test",
        )

    errors = exc_info.value.errors()
    assert any("package_name" in str(e["loc"]) for e in errors)


def test_project_config_invalid_package_name_with_hyphen(tmp_path: Path) -> None:
    """Test that package names with hyphens raise ValidationError."""
    with pytest.raises(ValidationError):
        ProjectConfig(
            package_name="my-package",  # Contains hyphen
            target_dir=tmp_path / "test",
        )


def test_project_config_relative_path() -> None:
    """Test that relative paths raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ProjectConfig(
            package_name="my_package",
            target_dir=Path("relative/path"),
        )

    errors = exc_info.value.errors()
    assert any("target_dir" in str(e["loc"]) for e in errors)


def test_project_config_custom_values() -> None:
    """Test ProjectConfig with custom values."""
    config = ProjectConfig(
        package_name="awesome_pkg",
        target_dir=Path("/home/user/projects"),
        author_name="John Doe",
        author_email="john@example.com",
        description="An awesome package",
        license_type="Apache-2.0",
    )

    assert config.package_name == "awesome_pkg"
    assert config.author_name == "John Doe"
    assert config.author_email == "john@example.com"
    assert config.description == "An awesome package"
    assert config.license_type == "Apache-2.0"


def test_destination_path(tmp_path: Path) -> None:
    """Test the destination_path property."""
    config = ProjectConfig(
        package_name="my_package",
        target_dir=tmp_path / "test",
    )

    assert config.destination_path == tmp_path / "test" / "my_package"


def test_to_template_context(tmp_path: Path) -> None:
    """Test conversion to template context."""
    config = ProjectConfig(
        package_name="my_package",
        target_dir=tmp_path / "test",
        author_name="Jane Doe",
        author_email="jane@example.com",
        description="Test package",
        license_type="MIT",
    )

    context = config.to_template_context()

    assert context["PKG"] == "my_package"
    assert context["AUTHOR_NAME"] == "Jane Doe"
    assert context["AUTHOR_EMAIL"] == "jane@example.com"
    assert context["DESCRIPTION"] == "Test package"
    assert context["LICENSE"] == "MIT"


def test_valid_package_names(tmp_path: Path) -> None:
    """Test various valid package names."""
    valid_names = [
        "simple",
        "with_underscore",
        "MixedCase",
        "_leading_underscore",
        "name123",
        "a",
    ]

    for name in valid_names:
        config = ProjectConfig(
            package_name=name,
            target_dir=tmp_path / "test",
        )
        assert config.package_name == name


def test_invalid_package_names(tmp_path: Path) -> None:
    """Test various invalid package names."""
    invalid_names = [
        "123start",  # Starts with number
        "with-hyphen",  # Contains hyphen
        "with space",  # Contains space
        "with.dot",  # Contains dot
        "",  # Empty string
    ]

    for name in invalid_names:
        with pytest.raises(ValidationError):
            ProjectConfig(
                package_name=name,
                target_dir=tmp_path / "test",
            )
