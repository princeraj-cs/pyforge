# pyforge

`pyforge` is a lightweight, interactive command-line interface (CLI) tool designed to scaffold production-ready Python projects in seconds. Inspired by standard scaffolding tools like `create-react-app`, `pyforge` automates project initialization, environment setup, testing configuration, linting, formatting, and dependency management.

---

## Key Features

* **Interactive TUI**: Driven by `questionary` for guided project configuration (supports non-interactive overrides).
* **Multiple Built-in Templates**: Native templates for `basic` packages, `cli` tools, `fastapi` microservices, and `flask` applications.
* **Remote Templates**: Pull custom project layouts directly from public GitHub repositories using the `gh:owner/repo` syntax.
* **Configurable Defaults**: Save persistent author, license, and tool choices in a `~/.newpythonrc` configuration file.
* **Standards-Compliant**: Generates PEP 621-compliant `pyproject.toml` using `hatchling` as the build backend.
* **Tooling Configuration**: Preconfigured integration with `pytest`, `ruff` (linter and formatter), and `pre-commit` hooks.
* **Task Automation**: Automated creation of a local virtual environment, Git repository initialization, and generation of a template-aware `Makefile` or `Justfile`.

---

## Installation

Install `pyforge` globally via PyPI:

```bash
pip install pyforge
```

Or install it in an isolated environment using `pipx`:

```bash
pipx install pyforge
```

---

## Quick Start

Initialize a new project by running:

```bash
newpython myproject
```

The CLI will start the interactive configuration wizard:

```
? Project description: A new Python project
? Author name: Jane Doe
? License: MIT
? Initialize a virtual environment (.venv)? Yes
? Initialize a git repository? Yes
```

Once the wizard completes, your project directory is created and populated. Execute the following commands to begin development:

```bash
cd myproject
source .venv/bin/activate    # On Windows use: .venv\Scripts\activate
make install                 # Installs the package and all dev dependencies
make run                     # Runs the application (varies by template)
```

---

## CLI Reference

```
Usage: newpython [OPTIONS] PROJECT_NAME

  Scaffold a new Python project.

Arguments:
  PROJECT_NAME  Name of the project (must be a valid Python identifier)

Options:
  --template TEXT      Built-in template (basic, cli, fastapi, flask)
                       or a remote GitHub repo (gh:owner/repo[@ref]) [default: basic]
  --no-pre-commit      Skip generating .pre-commit-config.yaml
  --justfile           Generate a Justfile instead of a Makefile
  -y, --yes            Skip interactive prompts and accept defaults
  --help               Show this message and exit.
```

---

## Project Structure (Basic Template)

The default template (`basic`) generates the following directory structure:

```
myproject/
├── src/
│   └── myproject/
│       └── __init__.py          # Package initialization
├── tests/
│   └── test_main.py             # Starter unit test
├── .env.example                 # Example environment variables
├── .gitignore                   # Standard Python git ignore rules
├── .pre-commit-config.yaml      # Pre-configured linting/formatting hooks
├── Makefile                     # Task runner
├── README.md                    # Generated project documentation
├── pyproject.toml               # Metadata, dependencies, and tool settings
└── requirements.txt             # Project dependencies
```

---

## Templates

### Built-in Templates

| Template | Primary Stack | Generated Entry Point | Run Command |
|---|---|---|---|
| `basic` | Pure Python | `src/package/__init__.py` | `python -m package` |
| `cli` | `click` | `src/package/cli.py` & `__main__.py` | Registered console script |
| `fastapi` | `fastapi`, `uvicorn`, `httpx` | `src/package/main.py` | `uvicorn src.package.main:app` |
| `flask` | `flask` (Factory pattern) | `src/package/app.py` | `flask run` |

### Remote Templates

You can import any public GitHub repository to use as a project template:

```bash
# Uses the main/master branch
newpython myproject --template gh:username/repo-name

# Pin to a specific branch, tag, or commit hash
newpython myproject --template gh:username/repo-name@v1.0.0
```

#### Remote Repository Requirements
Remote templates are fetched and copied as-is (no Jinja template rendering is performed on remote files). 
* If the remote repository has a top-level `template/` directory, only the contents of that folder are copied to the destination.
* If no `template/` directory is present, the entire contents of the repository root will be copied.

---

## Configuration File (`~/.newpythonrc`)

You can persist configuration defaults in a `~/.newpythonrc` (TOML format) file to pre-fill prompt values and skip entering them on every run.

```toml
# ~/.newpythonrc
author = "Jane Doe"
license = "MIT"
template = "basic"
pre_commit = true
justfile = false
```

### Precedence Order
When resolving configurations, `pyforge` applies overrides in the following order (highest to lowest):
1. **CLI Flags** (e.g. `--template`, `--justfile`)
2. **Configuration file** (`~/.newpythonrc`)
3. **Interactive Prompt Defaults**

To override the default config location, set the `NEWPYTHON_CONFIG` environment variable:
```bash
export NEWPYTHON_CONFIG="/path/to/custom/config.toml"
```

---

## Automated Task Runner

The generated `Makefile` (or `Justfile` if `--justfile` is passed) exposes standard commands for project maintenance:

* `make install`: Installs the project locally in editable mode alongside all development dependencies (`pip install -e ".[dev]"`).
* `make test`: Executes the test suite using `pytest`.
* `make lint`: Performs static analysis checking with `ruff`.
* `make format`: Auto-formats code styles using `ruff format`.
* `make run`: Starts the application server or CLI script (template-aware).
* `make clean`: Recursively cleans local cache directories (`__pycache__`, `.pytest_cache`, `.ruff_cache`, `build`, `dist`).

---

## Publishing to PyPI

Projects generated by `pyforge` use `hatchling` as the build system and are ready to be built and uploaded to PyPI:

1. Install build and publication dependencies:
   ```bash
   pip install build twine
   ```
2. Build the project distribution packages (source archive and wheel):
   ```bash
   python -m build
   ```
3. Upload to PyPI (or TestPyPI first):
   ```bash
   python -m twine upload dist/*
   ```

---

## Contributing

Contributions to `pyforge` are welcome. To set up a local development environment:

```bash
git clone https://github.com/your-name/pyforge.git
cd pyforge
pip install -e ".[dev]"
python -m pytest -v
```
