"""Central test configuration and shared fixtures.

This file serves as the CENTRAL location for all shared test fixtures,
as required by .clinerules/03-testing.md. DO NOT duplicate fixtures
across test files.
"""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory.

    Returns:
        Path to the project root directory.
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def src_dir(project_root: Path) -> Path:
    """Return the src directory.

    Args:
        project_root: Path to project root.

    Returns:
        Path to the src directory.
    """
    return project_root / "src"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory that is cleaned up after the test.

    Yields:
        Path to temporary directory.
    """
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def clean_env() -> Generator[dict[str, str], None, None]:
    """Provide a clean environment, restoring original after test.

    Yields:
        Dictionary containing original environment variables.
    """
    original_env = os.environ.copy()
    # Clear SCAFFOLD_ prefixed variables for clean testing
    scaffold_vars = [key for key in os.environ if key.startswith("SCAFFOLD_")]
    for var in scaffold_vars:
        del os.environ[var]

    yield original_env

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_temp_project(temp_dir: Path) -> Path:
    """Create a mock project structure in a temporary directory.

    Args:
        temp_dir: Temporary directory path.

    Returns:
        Path to the mock project root.
    """
    project_dir = temp_dir / "test_project"
    project_dir.mkdir()
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()
    return project_dir
