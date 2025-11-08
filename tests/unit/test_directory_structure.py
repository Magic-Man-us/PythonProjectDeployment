"""Tests for directory structure models."""

from pathlib import Path

from python_project_deployment.directory_structure import (
    DirectoryStructure,
    DocsStructure,
    GitHubStructure,
    PackageStructure,
    TestStructure,
)


class TestPackageStructure:
    """Tests for PackageStructure model."""

    def test_create_package_structure(self):
        """Test creating a package structure."""
        structure = PackageStructure(
            root=Path("src/mypackage"),
            utils=Path("src/mypackage/utils"),
            logger=Path("src/mypackage/logger"),
        )

        assert structure.structure_type == "package"
        assert structure.root == Path("src/mypackage")
        assert structure.utils == Path("src/mypackage/utils")
        assert structure.logger == Path("src/mypackage/logger")

    def test_get_all_paths(self):
        """Test getting all paths in order."""
        structure = PackageStructure(
            root=Path("src/mypackage"),
            utils=Path("src/mypackage/utils"),
            logger=Path("src/mypackage/logger"),
        )

        paths = structure.get_all_paths()
        assert len(paths) == 3
        assert paths[0] == Path("src/mypackage")
        assert paths[1] == Path("src/mypackage/utils")
        assert paths[2] == Path("src/mypackage/logger")

    def test_discriminator_serialization(self):
        """Test that discriminator is properly serialized."""
        structure = PackageStructure(
            root=Path("src/mypackage"),
            utils=Path("src/mypackage/utils"),
            logger=Path("src/mypackage/logger"),
        )

        data = structure.model_dump()
        assert data["structure_type"] == "package"


class TestTestStructure:
    """Tests for TestStructure model."""

    def test_create_test_structure(self):
        """Test creating a test structure."""
        structure = TestStructure(
            root=Path("tests"),
            unit=Path("tests/unit"),
            integration=Path("tests/integration"),
        )

        assert structure.structure_type == "test"
        assert structure.root == Path("tests")
        assert structure.unit == Path("tests/unit")
        assert structure.integration == Path("tests/integration")

    def test_get_all_paths(self):
        """Test getting all paths in order."""
        structure = TestStructure(
            root=Path("tests"),
            unit=Path("tests/unit"),
            integration=Path("tests/integration"),
        )

        paths = structure.get_all_paths()
        assert len(paths) == 3
        assert paths[0] == Path("tests")
        assert paths[1] == Path("tests/unit")
        assert paths[2] == Path("tests/integration")


class TestDocsStructure:
    """Tests for DocsStructure model."""

    def test_create_docs_structure(self):
        """Test creating a docs structure."""
        structure = DocsStructure(
            root=Path("docs"),
            api=Path("docs/api"),
        )

        assert structure.structure_type == "docs"
        assert structure.root == Path("docs")
        assert structure.api == Path("docs/api")

    def test_get_all_paths(self):
        """Test getting all paths in order."""
        structure = DocsStructure(
            root=Path("docs"),
            api=Path("docs/api"),
        )

        paths = structure.get_all_paths()
        assert len(paths) == 2
        assert paths[0] == Path("docs")
        assert paths[1] == Path("docs/api")


class TestGitHubStructure:
    """Tests for GitHubStructure model."""

    def test_create_github_structure(self):
        """Test creating a github structure."""
        structure = GitHubStructure(
            workflows=Path(".github/workflows"),
            issue_templates=Path(".github/ISSUE_TEMPLATE"),
        )

        assert structure.structure_type == "github"
        assert structure.workflows == Path(".github/workflows")
        assert structure.issue_templates == Path(".github/ISSUE_TEMPLATE")

    def test_get_all_paths(self):
        """Test getting all paths in order."""
        structure = GitHubStructure(
            workflows=Path(".github/workflows"),
            issue_templates=Path(".github/ISSUE_TEMPLATE"),
        )

        paths = structure.get_all_paths()
        assert len(paths) == 2
        assert paths[0] == Path(".github/workflows")
        assert paths[1] == Path(".github/ISSUE_TEMPLATE")


class TestDirectoryStructure:
    """Tests for DirectoryStructure model."""

    def test_create_with_defaults(self):
        """Test creating directory structure with defaults."""
        structure = DirectoryStructure()

        assert structure.src == Path("src")
        assert structure.data == Path("data")
        assert structure.logs == Path("logs")
        assert structure.scripts == Path("scripts")

    def test_get_package_structure(self):
        """Test getting package structure."""
        structure = DirectoryStructure()
        root = Path("/tmp/test-project")

        package_struct = structure.get_package_structure("mypackage", root)

        assert isinstance(package_struct, PackageStructure)
        assert package_struct.structure_type == "package"
        assert package_struct.root == root / "src" / "mypackage"
        assert package_struct.utils == root / "src" / "mypackage" / "utils"
        assert package_struct.logger == root / "src" / "mypackage" / "logger"

    def test_get_test_structure(self):
        """Test getting test structure."""
        structure = DirectoryStructure()
        root = Path("/tmp/test-project")

        test_struct = structure.get_test_structure(root)

        assert isinstance(test_struct, TestStructure)
        assert test_struct.structure_type == "test"
        assert test_struct.root == root / "tests"
        assert test_struct.unit == root / "tests" / "unit"
        assert test_struct.integration == root / "tests" / "integration"

    def test_get_docs_structure(self):
        """Test getting docs structure."""
        structure = DirectoryStructure()
        root = Path("/tmp/test-project")

        docs_struct = structure.get_docs_structure(root)

        assert isinstance(docs_struct, DocsStructure)
        assert docs_struct.structure_type == "docs"
        assert docs_struct.root == root / "docs"
        assert docs_struct.api == root / "docs" / "api"

    def test_get_github_structure(self):
        """Test getting github structure."""
        structure = DirectoryStructure()
        root = Path("/tmp/test-project")

        github_struct = structure.get_github_structure(root)

        assert isinstance(github_struct, GitHubStructure)
        assert github_struct.structure_type == "github"
        assert github_struct.workflows == root / ".github" / "workflows"
        assert github_struct.issue_templates == root / ".github" / "ISSUE_TEMPLATE"

    def test_get_all_structures(self):
        """Test getting all structures as discriminated union."""
        structure = DirectoryStructure()
        root = Path("/tmp/test-project")

        structures = structure.get_all_structures(root, "mypackage")

        assert len(structures) == 4
        assert isinstance(structures[0], PackageStructure)
        assert isinstance(structures[1], TestStructure)
        assert isinstance(structures[2], DocsStructure)
        assert isinstance(structures[3], GitHubStructure)

        # Verify each has correct discriminator
        assert structures[0].structure_type == "package"
        assert structures[1].structure_type == "test"
        assert structures[2].structure_type == "docs"
        assert structures[3].structure_type == "github"

    def test_get_all_directories(self):
        """Test getting all directories in creation order."""
        structure = DirectoryStructure()
        root = Path("/tmp/test-project")

        directories = structure.get_all_directories(root, "mypackage")

        # Should include simple directories + all structured directories
        assert len(directories) > 10

        # Check simple directories are first
        assert root / "src" in directories
        assert root / "data" in directories
        assert root / "logs" in directories
        assert root / "scripts" in directories

        # Check package directories
        assert root / "src" / "mypackage" in directories
        assert root / "src" / "mypackage" / "utils" in directories
        assert root / "src" / "mypackage" / "logger" in directories

        # Check test directories
        assert root / "tests" in directories
        assert root / "tests" / "unit" in directories
        assert root / "tests" / "integration" in directories

        # Check docs directories
        assert root / "docs" in directories
        assert root / "docs" / "api" in directories

        # Check github directories
        assert root / ".github" / "workflows" in directories
        assert root / ".github" / "ISSUE_TEMPLATE" in directories

    def test_create_all(self, tmp_path):
        """Test creating all directories."""
        structure = DirectoryStructure()
        root = tmp_path / "test-project"

        structure.create_all(root, "mypackage")

        # Verify directories were created
        assert (root / "src").exists()
        assert (root / "src" / "mypackage").exists()
        assert (root / "src" / "mypackage" / "utils").exists()
        assert (root / "src" / "mypackage" / "logger").exists()
        assert (root / "tests").exists()
        assert (root / "tests" / "unit").exists()
        assert (root / "tests" / "integration").exists()
        assert (root / "docs").exists()
        assert (root / "docs" / "api").exists()
        assert (root / ".github" / "workflows").exists()
        assert (root / ".github" / "ISSUE_TEMPLATE").exists()

    def test_create_all_with_permissions_callback(self, tmp_path):
        """Test creating directories with permissions callback."""
        structure = DirectoryStructure()
        root = tmp_path / "test-project"

        called_paths = []

        def track_permissions(path: Path, is_directory: bool):
            called_paths.append((path, is_directory))

        structure.create_all(root, "mypackage", set_permissions_fn=track_permissions)

        # Verify callback was called for each directory
        assert len(called_paths) > 10
        # All should be directories
        assert all(is_dir for _, is_dir in called_paths)


class TestDiscriminatedUnion:
    """Tests for discriminated union functionality."""

    def test_discriminated_union_type_checking(self):
        """Test that discriminated union properly validates structure_type."""
        # This should work - valid discriminator
        package = PackageStructure(
            root=Path("src/pkg"),
            utils=Path("src/pkg/utils"),
            logger=Path("src/pkg/logger"),
        )
        assert package.structure_type == "package"

        test = TestStructure(
            root=Path("tests"),
            unit=Path("tests/unit"),
            integration=Path("tests/integration"),
        )
        assert test.structure_type == "test"

    def test_structures_are_json_serializable(self):
        """Test that structures can be serialized to JSON."""
        structure = DirectoryStructure()
        root = Path("/tmp/test")

        structures = structure.get_all_structures(root, "pkg")

        # Each structure should be serializable
        for struct in structures:
            data = struct.model_dump()
            assert "structure_type" in data
            assert isinstance(data["structure_type"], str)
