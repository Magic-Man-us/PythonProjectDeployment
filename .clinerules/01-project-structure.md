# Project Structure

**CRITICAL:** Verify file tree structure matches the standard layout before starting any work.

## Standard Directory Layout

Replace `{package_name}` with the actual package name.

```
project_root/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── src/
│   └── {package_name}/
│       ├── __init__.py
│       ├── main.py
│       ├── utils/
│       └── logger/
│           └── logger.py
│
├── data/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
│
├── docs/
├── logs/
├── scripts/
├── requirements.txt
├── Makefile
├── README.md
├── LICENSE
├── .gitignore
├── CONTRIBUTING.md
├── SECURITY.md
├── uv.lock
├── .env
└── pyproject.toml
```

## Directory Roles

| Path | Purpose |
|------|---------|
| `.github/workflows/` | CI/CD pipeline definitions |
| `src/{package_name}/` | Application source code |
| `src/{package_name}/main.py` | Entry point |
| `src/{package_name}/utils/` | Helper functions |
| `src/{package_name}/logger/` | Logging setup |
| `data/` | Raw data files |
| `tests/unit/` | Unit tests |
| `tests/integration/` | Integration tests |
| `tests/conftest.py` | Test fixtures |
| `docs/` | Documentation |
| `logs/` | Runtime logs |
| `scripts/` | Automation scripts |
| `requirements.txt` | Dependencies |
| `uv.lock` | UV lock file |
| `.env` | Environment variables |
| `Makefile` | Build commands |

## Required Files

- `__init__.py` in all package directories
- `conftest.py` for pytest fixtures
- `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`
- `.gitignore`, `.env`
- `Makefile` with UV commands
- `pyproject.toml`

## Verification

Before creating new features or refactoring:
1. Run `tree` command in project root
2. Compare against standard layout
3. Clean up old files/directories no longer needed
4. Check for duplicate files before creating new ones
