"""Data models for project configuration using Pydantic."""

import re
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator


class ProjectConfig(BaseModel):
    """Configuration model for a Python project to be scaffolded.

    Attributes:
        package_name: Valid Python package identifier
        target_dir: Absolute path to parent directory where project will be created
        author_name: Name of the package author
        author_email: Email of the package author
        description: Short description of the package
        license_type: License type (MIT, Apache-2.0, GPL-3.0, etc.)
    """

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
    )
    author_email: str = Field(
        default="your.email@example.com",
        description="Author email for package metadata",
    )
    description: str = Field(
        default="A new Python package",
        description="Short description of the package",
    )
    license_type: str = Field(
        default="MIT",
        description="License type (MIT, Apache-2.0, GPL-3.0, etc.)",
    )

    @field_validator("package_name")
    @classmethod
    def validate_package_name(cls, v: str) -> str:
        """Validate that package_name is a valid Python identifier."""
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", v):
            raise ValueError(
                f"Invalid package_name: '{v}'. "
                "Must start with letter or underscore, "
                "followed by letters, numbers, or underscores."
            )
        return v

    @field_validator("target_dir")
    @classmethod
    def validate_target_dir(cls, v: Path) -> Path:
        """Validate that target_dir is an absolute path."""
        if not v.is_absolute():
            raise ValueError(f"target_dir must be an absolute path, got: {v}")
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

    @property
    def destination_path(self) -> Path:
        """Get the full destination path for the project."""
        return self.target_dir / self.package_name

    def to_template_context(self) -> dict[str, str]:
        """Convert config to template context for placeholder substitution."""
        return {
            "PKG": self.package_name,
            "AUTHOR_NAME": self.author_name,
            "AUTHOR_EMAIL": self.author_email,
            "DESCRIPTION": self.description,
            "LICENSE": self.license_type,
        }
