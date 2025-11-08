"""Data models for project configuration using Pydantic."""

import keyword
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, Literal, get_args

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)


class ProjectConfig(BaseModel):
    """Configuration model for a Python project to be scaffolded.

    Attributes:
        package_name: Valid Python package identifier
        target_dir: Absolute path to parent directory where project will be created
        author_name: Name of the package author
        author_email: Email of the package author (validated)
        description: Short description of the package
        license_type: License type (constrained to specific values)
        github_username: GitHub username for repository URLs and badges
    """

    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=False,
        extra="forbid",
    )

    package_name: str = Field(
        ...,
        description="Valid Python package name (letters, numbers, underscores)",
        min_length=1,
        max_length=100,
    )
    target_dir: Path = Field(
        ...,
        description="Absolute path to parent directory for the project",
    )
    author_name: str = Field(
        default="Your Name",
        description="Author name for package metadata",
        min_length=1,
        max_length=200,
    )
    author_email: EmailStr = Field(
        default="your.email@example.com",
        description="Author email for package metadata",
    )
    description: str = Field(
        default="A new Python package",
        description="Short description of the package",
        max_length=500,
    )
    license_type: Literal["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"] = Field(
        default="MIT",
        description="License type",
    )

    # Class variable to expose valid license types
    VALID_LICENSES: ClassVar[tuple[str, ...]] = get_args(__annotations__["license_type"])
    github_username: str = Field(
        default="your-username",
        description="GitHub username for URLs and badges",
        pattern=r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$",
    )

    @field_validator("package_name", mode="after")
    @classmethod
    def validate_package_name_format(cls, v: str) -> str:
        """Validate that package_name is a valid Python identifier."""
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", v):
            raise ValueError(
                f"Invalid package_name: '{v}'. "
                "Must start with letter or underscore, "
                "followed by letters, numbers, or underscores."
            )
        return v

    @field_validator("package_name", mode="after")
    @classmethod
    def validate_package_name_not_reserved(cls, v: str) -> str:
        """Check that package_name is not a Python reserved keyword."""
        if keyword.iskeyword(v):
            raise ValueError(
                f"Invalid package_name: '{v}' is a Python reserved keyword. "
                f"Please choose a different name."
            )
        return v

    @field_validator("target_dir", mode="after")
    @classmethod
    def validate_target_dir_absolute(cls, v: Path) -> Path:
        """Validate that target_dir is an absolute path."""
        if not v.is_absolute():
            raise ValueError(
                f"target_dir must be an absolute path, got: {v}. "
                f"Use Path.cwd() / 'relative/path' to convert relative paths."
            )
        return v

    @field_validator("target_dir", mode="after")
    @classmethod
    def validate_target_dir_writable(cls, v: Path) -> Path:
        """Verify target_dir exists and is writable."""
        if not v.exists():
            raise ValueError(
                f"target_dir does not exist: {v}. "
                "Please create the directory first or choose an existing one."
            )
        if not v.is_dir():
            raise ValueError(
                f"target_dir is not a directory: {v}. Please specify a valid directory path."
            )
        # Check write permissions by attempting to create a test file
        test_file = v / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError) as e:
            raise ValueError(f"target_dir is not writable: {v}. Permission denied: {e}") from e
        return v

    @model_validator(mode="after")
    def validate_destination_not_exists(self) -> "ProjectConfig":
        """Validate that destination directory doesn't already exist."""
        destination = self.target_dir / self.package_name
        if destination.exists():
            raise ValueError(
                f"Destination already exists: {destination}. "
                "Please choose a different package_name or target_dir."
            )
        return self

    @computed_field  # type: ignore[misc]
    @property
    def destination_path(self) -> Path:
        """Get the full destination path for the project."""
        return self.target_dir / self.package_name

    @computed_field  # type: ignore[misc]
    @property
    def github_url(self) -> str:
        """Get the GitHub repository URL."""
        return f"https://github.com/{self.github_username}/{self.package_name}"

    @field_serializer("target_dir", when_used="json")
    def serialize_path(self, value: Path) -> str:
        """Serialize Path to string for JSON."""
        return str(value)

    def to_template_context(self) -> dict[str, str]:
        """Convert config to template context for placeholder substitution.

        Returns:
            Dictionary with template placeholders and their values
        """
        current_date = datetime.now(UTC).strftime("%Y-%m-%d")
        return {
            "PKG": self.package_name,
            "AUTHOR_NAME": self.author_name,
            "AUTHOR_EMAIL": str(self.author_email),
            "DESCRIPTION": self.description,
            "LICENSE": self.license_type,
            "GITHUB_USERNAME": self.github_username,
            "GITHUB_URL": self.github_url,
            "CURRENT_DATE": current_date,
        }

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return (
            f"ProjectConfig("
            f"package_name={self.package_name!r}, "
            f"target_dir={self.target_dir!r}, "
            f"author_name={self.author_name!r}, "
            f"author_email={self.author_email!r})"
        )

    def __str__(self) -> str:
        """Return human-readable representation."""
        return (
            f"Project: {self.package_name}\n"
            f"  Destination: {self.destination_path}\n"
            f"  Author: {self.author_name} <{self.author_email}>\n"
            f"  License: {self.license_type}"
        )
