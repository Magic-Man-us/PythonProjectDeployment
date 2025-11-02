# Implementation Plan: Comprehensive Security, Logic, Error Handling, and Pydantic Model Enhancement

## [Overview]

Comprehensive refactoring to address security vulnerabilities, improve error handling, enhance Pydantic model usage, strengthen logic robustness, and add environment-based configuration support with BaseSettings.

The implementation will transform the codebase from a basic scaffolding tool into a production-ready, security-hardened application that follows modern Python best practices. This includes adding subprocess security with timeouts, structured error handling with custom exception types, enhanced Pydantic models with proper validation, environment-based configuration with precedence rules, atomic operations with rollback capability, and comprehensive logging with context.

Key improvements:
- Security: Subprocess timeouts, path validation, input sanitization, secure file permissions
- Configuration: BaseSettings for environment/file-based config with CLI override precedence
- Error Handling: Custom exception hierarchy, structured logging, rollback on failure
- Models: Enhanced validators, field constraints, computed fields, proper serialization
- Logic: Atomic operations, TOCTOU race condition fixes, resource verification
- Observability: Structured logging, operation metrics, progress tracking

## [Types]

New type definitions for security, configuration, error handling, and subprocess management.

**Security Types:**
```python
from typing import Literal, TypeAlias, Protocol
from enum import Enum

# Subprocess execution result
class SubprocessResult(BaseModel):
    """Result from subprocess execution."""
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    duration: float
    timed_out: bool

# Security severity levels
class SecurityLevel(str, Enum):
    """Security check severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# Operation timeouts
class TimeoutConfig(BaseModel):
    """Timeout configuration for operations."""
    git_operations: int = Field(default=30, ge=1, le=300)
    package_install: int = Field(default=600, ge=60, le=3600)
    test_execution: int = Field(default=300, ge=30, le=1800)
    docs_build: int = Field(default=180, ge=30, le=900)
```

**Configuration Types:**
```python
from pydantic import Field, field_validator, ConfigDict, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Settings for environment-based configuration
class ScaffolderSettings(BaseSettings):
    """Application settings with environment variable support."""
    model_config = SettingsConfigDict(
        env_prefix="SCAFFOLD_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Timeout configurations
    timeout_git: int = Field(default=30, ge=1, le=300)
    timeout_install: int = Field(default=600, ge=60, le=3600)
    timeout_test: int = Field(default=300, ge=30, le=1800)
    timeout_docs: int = Field(default=180, ge=30, le=900)

    # Security settings
    security_fail_level: SecurityLevel = Field(default=SecurityLevel.MEDIUM)
    validate_binaries: bool = Field(default=True)

    # Logging settings
    log_level: str = Field(default="INFO")
    log_file: Path | None = Field(default=None)
```

**Error Types:**
```python
# Custom exception hierarchy
class ScaffolderError(Exception):
    """Base exception for scaffolder errors."""
    def __init__(self, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.context = context or {}

class ValidationError(ScaffolderError):
    """Validation-related errors."""
    pass

class SecurityError(ScaffolderError):
    """Security-related errors."""
    pass

class SubprocessError(ScaffolderError):
    """Subprocess execution errors."""
    def __init__(self, message: str, result: SubprocessResult, context: dict[str, Any] | None = None):
        super().__init__(message, context)
        self.result = result

class FileSystemError(ScaffolderError):
    """File system operation errors."""
    pass

class RollbackError(ScaffolderError):
    """Errors during rollback operations."""
    pass
```

**Model Enhancements:**
```python
from pydantic import EmailStr, HttpUrl, field_serializer

class ProjectConfig(BaseModel):
    """Enhanced configuration model with proper validation."""
    model_config = ConfigDict(
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=False,
        extra="forbid"
    )

    package_name: str = Field(
        ...,
        description="Valid Python package name",
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$"
    )
    target_dir: Path = Field(..., description="Absolute path to parent directory")
    author_name: str = Field(default="Your Name", min_length=1, max_length=200)
    author_email: EmailStr = Field(default="your.email@example.com")
    description: str = Field(default="A new Python package", max_length=500)
    license_type: Literal["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause"] = Field(default="MIT")
    github_username: str = Field(default="your-username", pattern=r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$")

    @computed_field
    @property
    def destination_path(self) -> Path:
        """Get the full destination path."""
        return self.target_dir / self.package_name

    @computed_field
    @property
    def github_url(self) -> str:
        """Get the GitHub repository URL."""
        return f"https://github.com/{self.github_username}/{self.package_name}"
```

## [Files]

Files to create, modify, and enhance throughout the codebase.

**New Files:**
- `python_project_deployment/config.py` - BaseSettings configuration management
- `python_project_deployment/exceptions.py` - Custom exception hierarchy
- `python_project_deployment/security.py` - Security utilities and validation
- `python_project_deployment/subprocess_runner.py` - Secure subprocess execution wrapper
- `python_project_deployment/rollback.py` - Transaction and rollback management
- `python_project_deployment/logging_config.py` - Structured logging configuration
- `tests/test_config.py` - Tests for configuration management
- `tests/test_exceptions.py` - Tests for exception handling
- `tests/test_security.py` - Tests for security utilities
- `tests/test_subprocess_runner.py` - Tests for subprocess execution
- `tests/test_rollback.py` - Tests for rollback functionality
- `.scaffold.env.example` - Example environment configuration file

**Modified Files:**
- `python_project_deployment/models.py` - Enhanced with validators, EmailStr, computed fields, ConfigDict
- `python_project_deployment/scaffolder.py` - Add rollback, security checks, structured logging, subprocess wrapper
- `python_project_deployment/cli.py` - Add config file support, improved error messages, precedence handling
- `python_project_deployment/__init__.py` - Export new modules and exceptions
- `tests/test_models.py` - Add tests for new validators and computed fields
- `tests/test_scaffolder.py` - Add security tests, rollback tests, error handling tests
- `pyproject.toml` - Add pydantic-settings dependency
- `README.md` - Document new configuration options and security features

**Configuration Files:**
- `.scaffold.env.example` - Example showing all available environment variables
- Template update: `python_project_deployment/templates/.env.j2` - Include timeout and security settings

## [Functions]

New functions and modifications to existing functions for security, configuration, and error handling.

**New Functions in `config.py`:**
```python
def load_settings(env_file: Path | None = None) -> ScaffolderSettings:
    """Load settings with optional env file override."""

def merge_cli_with_settings(cli_args: dict[str, Any], settings: ScaffolderSettings) -> dict[str, Any]:
    """Merge CLI arguments with settings, CLI takes precedence."""
```

**New Functions in `security.py`:**
```python
def validate_path_traversal(path: Path, base_path: Path) -> Path:
    """Ensure path doesn't escape base directory."""

def sanitize_template_value(value: str, max_length: int = 1000) -> str:
    """Sanitize values before template rendering."""

def validate_binary(binary_path: Path, expected_name: str) -> bool:
    """Verify binary is what it claims to be."""

def set_secure_permissions(path: Path, is_directory: bool = False) -> None:
    """Set secure file/directory permissions."""
```

**New Functions in `subprocess_runner.py`:**
```python
def run_command(
    command: list[str],
    cwd: Path,
    timeout: int,
    capture_output: bool = True,
    check: bool = True,
    env: dict[str, str] | None = None
) -> SubprocessResult:
    """Execute command with security checks and timeout."""

def validate_command(command: list[str]) -> None:
    """Validate command before execution."""
```

**New Functions in `rollback.py`:**
```python
class RollbackManager:
    """Manages rollback operations for failed scaffolding."""

    def __init__(self, destination: Path):
        self.destination = destination
        self.operations: list[Callable[[], None]] = []

    def register_operation(self, rollback_fn: Callable[[], None]) -> None:
        """Register a rollback operation."""

    def execute_rollback(self) -> None:
        """Execute all registered rollback operations."""

    def __enter__(self) -> "RollbackManager":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            self.execute_rollback()
        return False
```

**Modified Functions in `scaffolder.py`:**
```python
def __init__(self, config: ProjectConfig, settings: ScaffolderSettings) -> None:
    """Initialize with config and settings."""

def scaffold(self) -> Path:
    """Execute scaffolding with rollback on failure."""
    # Use RollbackManager context

def _create_directory_structure(self, dest: Path, rollback: RollbackManager) -> None:
    """Create directories with atomic operations and rollback registration."""

def _validate_prerequisites(self) -> None:
    """Validate git, uv/pip availability before starting."""

def _execute_subprocess(
    self,
    command: list[str],
    description: str,
    timeout: int,
    cwd: Path | None = None
) -> SubprocessResult:
    """Wrapper for subprocess execution with logging."""
```

**Modified Functions in `models.py`:**
```python
@field_validator("package_name", mode="after")
@classmethod
def validate_package_name_reserved(cls, v: str) -> str:
    """Check against Python reserved keywords."""

@field_validator("target_dir", mode="after")
@classmethod
def validate_target_dir_writable(cls, v: Path) -> Path:
    """Verify write permissions before validation."""

@field_validator("author_email", mode="before")
@classmethod
def normalize_email(cls, v: str | EmailStr) -> EmailStr:
    """Normalize and validate email."""

@field_serializer("target_dir", when_used="json")
def serialize_path(self, value: Path) -> str:
    """Serialize Path to string for JSON."""

def to_template_context(self) -> dict[str, str]:
    """Use model_dump with sanitization."""
```

**Modified Functions in `cli.py`:**
```python
def load_config_from_file(config_file: Path | None) -> ScaffolderSettings:
    """Load configuration from file."""

def merge_configurations(
    cli_config: ProjectConfig,
    env_settings: ScaffolderSettings
) -> tuple[ProjectConfig, ScaffolderSettings]:
    """Merge CLI args with environment settings (CLI precedence)."""

@click.command()
@click.option("--config-file", type=click.Path(exists=True), help="Path to .env config file")
def main(..., config_file: str | None) -> None:
    """Updated to support config file and environment variables."""
```

## [Classes]

New classes and modifications to existing classes for enhanced functionality.

**New Classes:**

`config.py`:
- `ScaffolderSettings(BaseSettings)` - Application settings with environment variable support
- `TimeoutConfig(BaseModel)` - Centralized timeout configuration

`exceptions.py`:
- `ScaffolderError(Exception)` - Base exception
- `ValidationError(ScaffolderError)` - Validation failures
- `SecurityError(ScaffolderError)` - Security violations
- `SubprocessError(ScaffolderError)` - Subprocess failures
- `FileSystemError(ScaffolderError)` - File system errors
- `RollbackError(ScaffolderError)` - Rollback failures

`subprocess_runner.py`:
- `SubprocessResult(BaseModel)` - Structured subprocess result
- `SubprocessRunner` - Secure subprocess execution manager

`rollback.py`:
- `RollbackManager` - Transaction and rollback coordination

`logging_config.py`:
- `StructuredLogger` - Contextual structured logging

**Modified Classes:**

`models.py` - `ProjectConfig`:
- Add `model_config = ConfigDict(...)` for Pydantic v2 configuration
- Add `EmailStr` for author_email validation
- Add `Literal` type for license_type constraint
- Add `@computed_field` for destination_path and github_url
- Add `@field_serializer` for Path serialization
- Add enhanced validators with better error messages
- Add `__repr__` and `__str__` methods

`scaffolder.py` - `Scaffolder`:
- Add `settings: ScaffolderSettings` parameter to `__init__`
- Add `rollback_manager: RollbackManager` as instance variable
- Add `subprocess_runner: SubprocessRunner` for secure execution
- Add `logger: StructuredLogger` for contextual logging
- Update all methods to use structured logging
- Add `_validate_prerequisites()` method
- Add `_cleanup_on_failure()` method
- Refactor subprocess calls to use `SubprocessRunner`

## [Dependencies]

New dependencies and version updates for enhanced functionality.

**Add to pyproject.toml:**
```toml
[project]
dependencies = [
    "click>=8.3.0",
    "jinja2>=3.1.6",
    "pydantic>=2.12.3",
    "pydantic-settings>=2.10.0",  # NEW: For BaseSettings
    "python-dotenv>=1.0.0",       # NEW: For .env file support
    "email-validator>=2.2.0",     # NEW: For EmailStr validation
]

[project.optional-dependencies]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=7.0.0",
    "pytest-timeout>=2.3.0",      # NEW: For testing timeouts
    "pytest-mock>=3.14.0",        # NEW: For mocking
    "black>=25.9.0",
    "isort>=7.0.0",
    "mypy>=1.18.2",
    "ruff>=0.14.3",
    "pre-commit>=4.3.0",
    "bandit>=1.8.6",
    "safety>=3.6.2",
    "sphinx>=8.2.3",
    "sphinx-rtd-theme>=3.0.2",
    "sphinx-autodoc-typehints>=3.5.2",
]
```

**Rationale:**
- `pydantic-settings`: Enables BaseSettings for environment-based configuration
- `python-dotenv`: Provides .env file loading support
- `email-validator`: Required for EmailStr validation
- `pytest-timeout`: Enables timeout testing
- `pytest-mock`: Simplifies mocking in tests

## [Testing]

New test files and modifications to existing tests for comprehensive coverage.

**New Test Files:**

`tests/test_config.py`:
- `test_load_settings_from_env()` - Load from environment variables
- `test_load_settings_from_file()` - Load from .env file
- `test_settings_precedence()` - Verify environment > file precedence
- `test_invalid_timeout_values()` - Validate timeout constraints
- `test_merge_cli_with_settings()` - CLI override precedence

`tests/test_exceptions.py`:
- `test_exception_hierarchy()` - Verify exception inheritance
- `test_exception_context()` - Test context preservation
- `test_subprocess_error_details()` - Verify SubprocessError includes result

`tests/test_security.py`:
- `test_path_traversal_detection()` - Detect ../ attacks
- `test_path_traversal_symlink()` - Detect symlink attacks
- `test_sanitize_template_value()` - Test sanitization
- `test_validate_binary()` - Binary validation
- `test_secure_permissions()` - File permission setting

`tests/test_subprocess_runner.py`:
- `test_command_timeout()` - Verify timeout enforcement
- `test_command_validation()` - Reject invalid commands
- `test_command_execution_success()` - Successful execution
- `test_command_execution_failure()` - Handle failures
- `test_subprocess_result_capture()` - Capture stdout/stderr

`tests/test_rollback.py`:
- `test_rollback_on_failure()` - Execute rollback operations
- `test_rollback_order()` - Verify LIFO execution order
- `test_rollback_partial_failure()` - Handle rollback errors
- `test_context_manager_usage()` - Test context manager protocol

**Modified Test Files:**

`tests/test_models.py`:
- Add `test_email_validation()` - Test EmailStr validator
- Add `test_computed_fields()` - Test destination_path and github_url
- Add `test_license_type_constraint()` - Test Literal constraint
- Add `test_github_username_pattern()` - Test username validation
- Add `test_field_serialization()` - Test Path serialization
- Add `test_model_config()` - Test ConfigDict settings
- Add `test_reserved_keyword_rejection()` - Test Python keyword check
- Add `test_target_dir_writable()` - Test write permission check

`tests/test_scaffolder.py`:
- Add `test_scaffolder_rollback_on_git_failure()` - Rollback test
- Add `test_scaffolder_timeout_handling()` - Timeout test
- Add `test_scaffolder_prerequisites_validation()` - Prerequisite check
- Add `test_scaffolder_with_settings()` - Settings integration
- Add `test_subprocess_security()` - Security validation
- Add `test_atomic_directory_creation()` - Atomic operation test
- Fix `test_template_files_created()` - Remove requirements.txt check
- Add `test_file_permissions()` - Verify secure permissions

## [Implementation Order]

Logical sequence of changes to minimize conflicts and ensure successful integration.

1. **Create exception hierarchy** (`python_project_deployment/exceptions.py`)
   - Establish base ScaffolderError and derived exceptions
   - Add context preservation and error details
   - Write tests in `tests/test_exceptions.py`

2. **Create configuration management** (`python_project_deployment/config.py`)
   - Implement ScaffolderSettings with BaseSettings
   - Add TimeoutConfig model
   - Add load_settings and merge functions
   - Write tests in `tests/test_config.py`
   - Update pyproject.toml with pydantic-settings dependency

3. **Create security utilities** (`python_project_deployment/security.py`)
   - Implement path traversal validation
   - Add template value sanitization
   - Add binary validation
   - Add secure permission setting
   - Write tests in `tests/test_security.py`

4. **Create subprocess runner** (`python_project_deployment/subprocess_runner.py`)
   - Implement SubprocessResult model
   - Create SubprocessRunner class with timeout enforcement
   - Add command validation
   - Write tests in `tests/test_subprocess_runner.py`

5. **Create rollback manager** (`python_project_deployment/rollback.py`)
   - Implement RollbackManager with context manager protocol
   - Add operation registration and execution
   - Write tests in `tests/test_rollback.py`

6. **Create logging configuration** (`python_project_deployment/logging_config.py`)
   - Implement StructuredLogger with context support
   - Add correlation ID tracking
   - Configure formatters and handlers

7. **Enhance ProjectConfig model** (`python_project_deployment/models.py`)
   - Add ConfigDict configuration
   - Replace author_email with EmailStr
   - Add Literal constraint for license_type
   - Add computed_field decorators
   - Add enhanced validators
   - Add field_serializer for Path
   - Add __repr__ and __str__ methods
   - Update tests in `tests/test_models.py`

8. **Update Scaffolder class** (`python_project_deployment/scaffolder.py`)
   - Add settings parameter to __init__
   - Integrate RollbackManager in scaffold() method
   - Replace subprocess.run with SubprocessRunner
   - Add _validate_prerequisites() method
   - Add structured logging throughout
   - Update all subprocess calls with timeouts
   - Add security validation calls
   - Update tests in `tests/test_scaffolder.py`

9. **Update CLI** (`python_project_deployment/cli.py`)
   - Add --config-file option
   - Implement load_config_from_file()
   - Implement merge_configurations()
   - Update main() to load settings and merge with CLI args
   - Improve error message formatting
   - Add config precedence documentation

10. **Update package exports** (`python_project_deployment/__init__.py`)
    - Export new exception classes
    - Export ScaffolderSettings
    - Export SubprocessRunner
    - Update __all__ list

11. **Create example configuration** (`.scaffold.env.example`)
    - Document all available environment variables
    - Include timeout configurations
    - Include security settings
    - Add usage examples

12. **Update documentation** (`README.md`, docs)
    - Document new configuration options
    - Document environment variable support
    - Document precedence rules (CLI > ENV > defaults)
    - Add security best practices section
    - Update examples with config file usage

13. **Update templates** (`python_project_deployment/templates/`)
    - Update .env.j2 to include timeout settings
    - Ensure pyproject.toml.j2 uses latest Pydantic patterns

14. **Run full test suite and fix issues**
    - Run pytest with coverage
    - Fix any test failures
    - Ensure coverage > 90%
    - Run mypy type checking
    - Run security scans (bandit, safety)

15. **Final validation and documentation**
    - Verify all features work end-to-end
    - Update CHANGELOG.md
    - Update version in __init__.py and pyproject.toml
    - Review and finalize all docstrings
