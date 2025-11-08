# Testing Standards

## Test Structure
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Shared fixtures in `tests/conftest.py` (CENTRAL LOCATION - DO NOT DUPLICATE)

## Test Guidelines
- Mock external dependencies
- Keep tests focused, deterministic, and fast
- Cover main paths and exception handling
- Use hypothesis for property-based tests when valuable
- Integration tests cover edge cases

## Fixture Management
- Use `tests/conftest.py` as the CENTRAL fixture location
- DO NOT duplicate fixtures across test files
- Define shared fixtures once in conftest.py
- Use fixture scopes appropriately (function, class, module, session)

## Test Organization
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Group related tests in classes when appropriate
- Keep test functions small and focused
