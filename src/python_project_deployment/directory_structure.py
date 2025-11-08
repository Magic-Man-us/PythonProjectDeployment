"""Directory structure models for project scaffolding."""

from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class PackageStructure(BaseModel):
    """Model representing the package directory structure."""

    structure_type: Literal["package"] = "package"
    root: Path = Field(description="Package root directory")
    utils: Path = Field(description="Utilities module directory")
    logger: Path = Field(description="Logger module directory")

    def get_all_paths(self) -> list[Path]:
        """Get all package paths in creation order.

        Returns:
            List of all package directory paths
        """
        return [self.root, self.utils, self.logger]


class TestStructure(BaseModel):
    """Model representing the test directory structure."""

    __test__ = False  # Tell pytest this is not a test class

    structure_type: Literal["test"] = "test"
    root: Path = Field(description="Test root directory")
    unit: Path = Field(description="Unit tests directory")
    integration: Path = Field(description="Integration tests directory")

    def get_all_paths(self) -> list[Path]:
        """Get all test paths in creation order.

        Returns:
            List of all test directory paths
        """
        return [self.root, self.unit, self.integration]


class DocsStructure(BaseModel):
    """Model representing the documentation directory structure."""

    structure_type: Literal["docs"] = "docs"
    root: Path = Field(description="Documentation root directory")
    api: Path = Field(description="API documentation directory")

    def get_all_paths(self) -> list[Path]:
        """Get all documentation paths in creation order.

        Returns:
            List of all documentation directory paths
        """
        return [self.root, self.api]


class GitHubStructure(BaseModel):
    """Model representing the GitHub directory structure."""

    structure_type: Literal["github"] = "github"
    workflows: Path = Field(description="GitHub Actions workflows directory")
    issue_templates: Path = Field(description="GitHub issue templates directory")

    def get_all_paths(self) -> list[Path]:
        """Get all GitHub paths in creation order.

        Returns:
            List of all GitHub directory paths
        """
        return [self.workflows, self.issue_templates]


# Discriminated union of all structure types
AnyStructure = Annotated[
    Union[PackageStructure, TestStructure, DocsStructure, GitHubStructure],
    Field(discriminator="structure_type"),
]


class DirectoryStructure(BaseModel):
    """Model defining the complete directory structure for a scaffolded project.

    This model defines all directories that should be created during scaffolding
    using nested Pydantic models for each logical group of directories with
    discriminated unions for type safety.
    """

    # Simple directories
    src: Path = Field(default=Path("src"), description="Source code directory")
    data: Path = Field(default=Path("data"), description="Data directory")
    logs: Path = Field(default=Path("logs"), description="Logs directory")
    scripts: Path = Field(default=Path("scripts"), description="Scripts directory")

    def get_package_structure(self, package_name: str, root: Path) -> PackageStructure:
        """Get the package directory structure.

        Args:
            package_name: Name of the package
            root: Project root directory

        Returns:
            PackageStructure model with all package paths
        """
        base = root / self.src / package_name
        return PackageStructure(
            root=base,
            utils=base / "utils",
            logger=base / "logger",
        )

    def get_test_structure(self, root: Path) -> TestStructure:
        """Get the test directory structure.

        Args:
            root: Project root directory

        Returns:
            TestStructure model with all test paths
        """
        tests_root = root / "tests"
        return TestStructure(
            root=tests_root,
            unit=tests_root / "unit",
            integration=tests_root / "integration",
        )

    def get_docs_structure(self, root: Path) -> DocsStructure:
        """Get the documentation directory structure.

        Args:
            root: Project root directory

        Returns:
            DocsStructure model with all documentation paths
        """
        docs_root = root / "docs"
        return DocsStructure(
            root=docs_root,
            api=docs_root / "api",
        )

    def get_github_structure(self, root: Path) -> GitHubStructure:
        """Get the GitHub directory structure.

        Args:
            root: Project root directory

        Returns:
            GitHubStructure model with all GitHub paths
        """
        github_root = root / ".github"
        return GitHubStructure(
            workflows=github_root / "workflows",
            issue_templates=github_root / "ISSUE_TEMPLATE",
        )

    def get_all_structures(self, root: Path, package_name: str) -> list[AnyStructure]:
        """Get all directory structures as discriminated models.

        Args:
            root: Project root directory
            package_name: Name of the package

        Returns:
            List of all structure models with discriminators
        """
        return [
            self.get_package_structure(package_name, root),
            self.get_test_structure(root),
            self.get_docs_structure(root),
            self.get_github_structure(root),
        ]

    def get_all_directories(self, root: Path, package_name: str) -> list[Path]:
        """Get all directories to create in the correct order.

        Args:
            root: Project root directory
            package_name: Name of the package

        Returns:
            List of all directories in creation order
        """
        dirs = []

        # Add simple directories first
        dirs.extend(
            [
                root / self.src,
                root / self.data,
                root / self.logs,
                root / self.scripts,
            ]
        )

        # Add structured directories using discriminated models
        for structure in self.get_all_structures(root, package_name):
            dirs.extend(structure.get_all_paths())

        return dirs

    def create_all(
        self,
        root: Path,
        package_name: str,
        set_permissions_fn: Callable[[Path, bool], None] | None = None,
    ) -> None:
        """Create all directories under the given root.

        Args:
            root: Root directory to create structure under
            package_name: Name of the package
            set_permissions_fn: Optional function to set permissions on directories
        """
        for directory in self.get_all_directories(root, package_name):
            directory.mkdir(parents=True, exist_ok=True)

            if set_permissions_fn:
                set_permissions_fn(directory, True)
