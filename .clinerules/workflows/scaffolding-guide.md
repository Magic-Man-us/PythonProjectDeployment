
# Scaffold Python Package – Create & Launch New Project

## 🎯 Purpose
Implement a scaffolding project that allows you to launch new Python packages with full setup: `uv` venv management, `pyproject.toml`, `pytest + coverage`, `Sphinx` docs, Git repo, CI config.

## ✅ Inputs
- `package_name` — Package name (PEP 8 valid, e.g. `my_cool_pkg`)
- `target_dir` — Absolute path to parent directory where the project folder will be created

## ✅ Sequence of Tasks

### 1. Validate inputs
- [ ] Run shell script to check `package_name` matches `[a-zA-Z_][a-zA-Z0-9_]*`
- [ ] Ensure `target_dir` is an absolute path
```bash
set -e
PKG="${package_name}"
DIR="${target_dir}"
python3 - <<'PY'
import re, sys, os
pkg=sys.argv[1]; dir_=sys.argv[2]
if not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', pkg):
    print(f"Invalid package_name: {pkg}"); sys.exit(1)
if not os.path.isabs(dir_):
    print(f"target_dir must be absolute: {dir_}"); sys.exit(1)
print("Inputs OK.")
PY "$PKG" "$DIR"
````

### 2. Prepare template workspace

* [ ] Create a temporary workspace `.cline_tmp_pkg_template`
* [ ] Within it, create directory structure for TEMPLATE:

  * `TEMPLATE/{{PKG}}/`
  * `TEMPLATE/tests/`
  * `TEMPLATE/docs/`
  * `TEMPLATE/.github/workflows/`
* [ ] Add the following files in TEMPLATE (with placeholder `{{PKG}}` inside):

  * `pyproject.toml`
  * `README.md`
  * `LICENSE`
  * `.gitignore`
  * `.github/workflows/ci.yaml`
  * `{{PKG}}/__init__.py`, `{{PKG}}/hello.py`
  * `tests/test_hello.py`
  * `docs/conf.py`, `docs/index.rst`
  * `requirements-dev.txt`
  * `Makefile`
  * Optional `setup.cfg` or patch file for dev-extras

### 3. Materialize project & substitute placeholders

* [ ] Compute `DEST="${target_dir}/${package_name}"`
* [ ] Fail if `DEST` already exists
* [ ] Copy all files from workspace TEMPLATE to `${DEST}`
* [ ] Recursively replace placeholder `{{PKG}}` with actual `package_name` in all files
* [ ] Print “Project created at: ${DEST}”

### 4. Initialize git repository

* [ ] `cd` into `${DEST}`
* [ ] `git init`
* [ ] `git add .`
* [ ] `git commit -m "chore: initial scaffold"`
* [ ] Print “Git repo initialized.”

### 5. Setup `uv` environment & install dev extras

* [ ] `cd "${DEST}"`
* [ ] `uv venv`
 * [ ] `uv sync --all-extras`
* [ ] Print “Environment ready.”

### 6. Run tests & coverage

* [ ] `cd "${DEST}"`
* [ ] `uv run pytest --cov="${package_name}" --cov-report=term-missing`

### 7. Build Sphinx documentation

* [ ] `cd "${DEST}"`
* [ ] `uv run sphinx-build -b html docs docs/_build/html`
* [ ] Print “Docs built at: docs/_build/html”

### 8. Output summary

* [ ] Print “Scaffold complete.”
* [ ] Print project path: `${DEST}`
* [ ] Print next steps:

  ```text
  cd "${DEST}"
  source .venv/bin/activate  # (or use uv run)
  uv run python -c "import ${package_name}; print(${package_name}.hello())"
  ```

## 📁 Generated Structure

```
${package_name}/
  .github/workflows/ci.yaml
  docs/
    conf.py
    index.rst
    _build/           (after docs build)
  tests/
    test_hello.py
  ${package_name}/
    __init__.py
    hello.py
  .gitignore
  LICENSE
  Makefile
  README.md
  pyproject.toml
  requirements-dev.txt
  setup.cfg
```

## 📝 Notes

* Uses `uv` for virtualenv management.
* Configured for `pytest + pytest-cov`.
* Sphinx docs with theme `furo` (can edit in `docs/conf.py`).
* Dev extras via `pyproject.toml` optional-deps.
* CI workflow provided in `.github/workflows/ci.yaml`.

```
