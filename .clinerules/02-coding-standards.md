# Python Coding Standards

## PEP 8 Compliance
- Follow PEP 8 guidelines strictly
- Max line length: 100 characters
- Proper indentation and spacing

## Naming Conventions
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants

## Imports
Group in order, separated by blank lines:
1. Standard library
2. Third-party packages
3. Local application imports

## Type Hints
Use type hints for all function signatures to improve readability and enable static analysis.

## String Formatting
- Use f-strings when no user input is involved
- Use `.format()` method when user input is present (security)

## Data Structures
- Use Pydantic models for external data boundaries (API, database, user input)
- Use standard dataclasses for internal structures
- Prefer `frozen=True` for immutability

## Error Handling
- Implement structured logging throughout
- Never log sensitive information
- Use appropriate exception types

## Code Organization
- Avoid deep nesting (max 3-4 levels)
- Keep functions focused and single-purpose
- Extract complex logic into helper functions
