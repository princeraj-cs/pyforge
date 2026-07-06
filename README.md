# pyforge

`pyforge` is a lightweight command-line tool for scaffolding Python projects in seconds. It creates a working project layout, starter tests, basic tooling config, and a template-specific entry point so you can start coding immediately.

---

## Key Features

- **Terminal-native TUI**: A Rich-powered wizard with a visual template menu and styled prompts.
- **Multiple Built-in Templates**: Native templates for `basic` packages, `cli` tools, `fastapi` services, and `flask` applications.
- **Remote Templates**: Pull custom project layouts directly from public GitHub repositories using the `gh:owner/repo` syntax.
- **Configurable Defaults**: Save persistent author, license, template, and tool choices in a `~/.newpythonrc` configuration file.
- **Standards-Compliant**: Generates PEP 621-compliant `pyproject.toml` using `hatchling` as the build backend.
- **Tooling Configuration**: Preconfigured integration with `pytest`, `ruff`, and optional `pre-commit` hooks.
- **Task Automation**: Optional virtual environment creation, Git repository initialization, and generation of a template-aware `Makefile` or `Justfile`.

---

## Installation

Install `pyforge-init` globally via PyPI:

```bash
pip install pyforge-init
```

Or install it in an isolated environment using `pipx`:

```bash
pipx install pyforge-init
```

---

## Quick Start

Initialize a new project by running:

```bash
newpython myproject
```

In an interactive terminal, `pyforge` opens a template picker first and then asks for project details. The template menu includes:

```text
1. Basic package - Minimal package with a real entry point and starter test.
2. Click CLI - Console application with a click command and script entry point.
3. FastAPI service - API scaffold with a health endpoint.
4. Flask app - Factory-style web app.
5. Custom GitHub template - gh:owner/repo[@ref]
```

If you pass `--yes`, `pyforge` skips prompts and uses defaults. You can also pass `--template` directly to bypass the picker.

Once the wizard completes, your project directory is created and populated. Typical next steps are:

```bash
cd myproject
source .venv/bin/activate    # On Windows use: .venv\Scripts\activate
make install                 # Installs the package and all dev dependencies
make run                     # Runs the application or command
```

---

## CLI Reference

```text
Usage: newpython [OPTIONS] PROJECT_NAME

  Scaffold a new Python project.

Arguments:
  PROJECT_NAME  Name of the project (must be a valid Python identifier)

Options:
  --template TEXT      Built-in template or remote GitHub template.
                       Built-ins: basic, cli, fastapi, flask.
                       Remote: gh:owner/repo or gh:owner/repo@ref.
                       If omitted, an interactive template picker is shown.
  --no-pre-commit      Skip generating .pre-commit-config.yaml
  --justfile           Generate a Justfile instead of a Makefile
  -y, --yes            Skip interactive prompts and accept defaults
  --help               Show this message and exit.
```

---

## Built-in Templates

### Basic

Minimal package scaffold with an executable module layout.

- `src/<project>/main.py`
- `src/<project>/__main__.py`
- `tests/test_main.py`

### CLI

Click-based command-line application with a console script entry point.

- `src/<project>/cli.py`
- `src/<project>/__main__.py`
- `tests/test_cli.py`

### FastAPI

API scaffold with a root route and a `/health` endpoint.

- `src/<project>/main.py`
- `tests/test_main.py`

### Flask

Factory-style Flask application with a test client setup.

- `src/<project>/app.py`
- `tests/test_app.py`

---

## Project Structure

The default `basic` template generates the following directory structure:

```text
myproject/
├── src/
│   └── myproject/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Module entry point
│       └── main.py              # Console entry point
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

### Remote Templates

`pyforge` is a lightweight command-line tool for scaffolding Python projects in seconds. It creates a working project layout, starter tests, basic tooling config, and a template-specific entry point so you can start coding immediately.

---

## Key Features

- **Terminal-native TUI**: A Rich-powered wizard with a visual template menu and styled prompts.
- **Multiple Built-in Templates**: Native templates for `basic` packages, `cli` tools, `fastapi` services, and `flask` applications.
- **Remote Templates**: Pull custom project layouts directly from public GitHub repositories using the `gh:owner/repo` syntax.
- **Configurable Defaults**: Save persistent author, license, template, and tool choices in a `~/.newpythonrc` configuration file.
- **Standards-Compliant**: Generates PEP 621-compliant `pyproject.toml` using `hatchling` as the build backend.
- **Tooling Configuration**: Preconfigured integration with `pytest`, `ruff`, and optional `pre-commit` hooks.
- **Task Automation**: Optional virtual environment creation, Git repository initialization, and generation of a template-aware `Makefile` or `Justfile`.

---

## Installation

Install `pyforge-init` globally via PyPI:

```bash
pip install pyforge-init
```

Or install it in an isolated environment using `pipx`:

```bash
pipx install pyforge-init
```

---

## Quick Start

Initialize a new project by running:

```bash
newpython myproject
```

In an interactive terminal, `pyforge` opens a template picker first and then asks for project details. The template menu includes:

```text
1. Basic package - Minimal package with a real entry point and starter test.
2. Click CLI - Console application with a click command and script entry point.
3. FastAPI service - API scaffold with a health endpoint.
4. Flask app - Factory-style web app.
5. Custom GitHub template - gh:owner/repo[@ref]
```

If you pass `--yes`, `pyforge` skips prompts and uses defaults. You can also pass `--template` directly to bypass the picker.

Once the wizard completes, your project directory is created and populated. Typical next steps are:

```bash
cd myproject
source .venv/bin/activate    # On Windows use: .venv\Scripts\activate
make install                 # Installs the package and all dev dependencies
make run                     # Runs the application or command
```

---

## CLI Reference

```text
Usage: newpython [OPTIONS] PROJECT_NAME

  Scaffold a new Python project.

Arguments:
  PROJECT_NAME  Name of the project (must be a valid Python identifier)

Options:
  --template TEXT      Built-in template or remote GitHub template.
                       Built-ins: basic, cli, fastapi, flask.
                       Remote: gh:owner/repo or gh:owner/repo@ref.
                       If omitted, an interactive template picker is shown.
  --no-pre-commit      Skip generating .pre-commit-config.yaml
  --justfile           Generate a Justfile instead of a Makefile
  -y, --yes            Skip interactive prompts and accept defaults
  --help               Show this message and exit.
```

---

## Built-in Templates

### Basic

Minimal package scaffold with an executable module layout.

- `src/<project>/main.py`
- `src/<project>/__main__.py`
- `tests/test_main.py`

### CLI

Click-based command-line application with a console script entry point.

- `src/<project>/cli.py`
- `src/<project>/__main__.py`
- `tests/test_cli.py`

### FastAPI

API scaffold with a root route and a `/health` endpoint.

- `src/<project>/main.py`
- `tests/test_main.py`

### Flask

Factory-style Flask application with a test client setup.

- `src/<project>/app.py`
- `tests/test_app.py`

---

## Project Structure

The default `basic` template generates the following directory structure:

```text
myproject/
├── src/
│   └── myproject/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Module entry point
│       └── main.py              # Console entry point
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

## Remote Templates

You can import any public GitHub repository to use as a project template:

```bash
# Uses the main/master branch
newpython myproject --template gh:username/repo-name

# Pin to a specific branch, tag, or commit hash
newpython myproject --template gh:username/repo-name@v1.0.0
```

### Remote Repository Requirements

Remote templates are fetched and copied as-is, so no Jinja rendering is performed on remote files.

- If the remote repository has a top-level `template/` directory, only the contents of that folder are copied to the destination.
- If no `template/` directory is present, the entire contents of the repository root are copied.

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

When resolving configurations, `pyforge` applies overrides in the following order, from highest to lowest:

1. CLI flags, such as `--template` and `--justfile`
2. Configuration file, `~/.newpythonrc`
3. Interactive prompt defaults

To override the default config location, set the `NEWPYTHON_CONFIG` environment variable:

```bash
export NEWPYTHON_CONFIG="/path/to/custom/config.toml"
```

---

## Automated Task Runner

The generated `Makefile` or `Justfile` exposes standard commands for project maintenance:

- `install`: Install the project locally in editable mode alongside all development dependencies.
- `test`: Execute the test suite using `pytest`.
- `lint`: Perform static analysis with `ruff`.
- `format`: Auto-format code styles using `ruff format`.
- `run`: Start the application server or CLI script, depending on the selected template.
- `clean`: Remove local cache and build directories such as `__pycache__`, `.pytest_cache`, `.ruff_cache`, `build`, and `dist`.

---

## Publishing to PyPI

Projects generated by `pyforge` use `hatchling` as the build system and are ready to be built and uploaded to PyPI:

1. Install build and publication dependencies:
   ```bash
   pip install build twine
   ```
2. Build the project distribution packages, source archive and wheel:
   ```bash
   python -m build
   ```
3. Upload to PyPI, or TestPyPI first:
   ```bash
   python -m twine upload dist/*
   ```

---

## Development

To work on `pyforge` locally:

```bash
git clone https://github.com/your-name/pyforge.git
cd pyforge
pip install -e ".[dev]"
python -m pytest -v
```

---

## Contributing

Contributions are welcome. Open an issue or pull request if you find a bug or want to propose an improvement.
