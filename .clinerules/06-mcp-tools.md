# MCP Server Usage

## Primary Tool for Documentation Access
Use the MCP server for AI Documentation Access as your primary tool for accessing project documentation. This tool allows you to query the project's documentation in real-time, providing accurate and up-to-date information about the codebase.

## MCP Server Capabilities

### Search and Reference
- Search docstrings and API documentation
- Understand current codebase structure
- Reference exact function signatures and type hints
- Quote documentation verbatim
- Provide context-aware suggestions based on established patterns

### Features
- **Local-first**: Works offline, all data stays on your machine
- **Fast BM25 search**: Sub-millisecond query times
- **Auto-sync**: Rebuilds docs on every commit via pre-commit hooks
- **Complete coverage**: Extracts all docstrings, type hints, and examples

## Documentation Index Tags

The server indexes the following metadata for fast retrieval:

| Tag | Description |
|-----|-------------|
| `purpose` | Module, class, or function intent |
| `models` | Pydantic models, dataclasses, typed structures |
| `methods` | Class methods and their roles |
| `classes` | Class definitions and inheritance |
| `modules` | Module structure and imports |
| `functions` | Function definitions and usage |
| `signatures` | Parameters, return types, type annotations |
| `exceptions` | Raised exceptions and error conditions |
| `behaviors` | Side effects, branches, conditions |
| `dependencies` | External libraries and internal imports |

## Usage Guidelines

- Query the MCP server when implementing new features
- Use documentation index tags to refine searches
- Reference MCP server to ensure code aligns with established patterns
- Use pydantic-docs MCP when working with Pydantic models
- Always leverage the MCP server for current project standards
