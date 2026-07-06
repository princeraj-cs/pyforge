# pyforge

`pyforge` is a terminal-first Python project scaffolder. It creates a clean project layout, starter tests, tooling files, and a template-specific entry point so you can start building immediately.

---

## Highlights

- **Fast setup**: Generate a project in a single command.
- **Polished terminal UI**: Choose templates from a Rich-powered interactive menu.
- **Built-in templates**: `basic`, `cli`, `fastapi`, and `flask`.
- **Remote templates**: Use any public GitHub repository with `gh:owner/repo` or `gh:owner/repo@ref`.
- **Configurable defaults**: Persist author, license, template, and tooling preferences in `~/.newpythonrc`.
- **Modern packaging**: Generates a PEP 621 `pyproject.toml` using `hatchling`.
- **Project automation**: Optional virtual environment creation, Git initialization, `pre-commit`, `Makefile`, or `Justfile` support.

---

## Installation

Install from PyPI:

```bash
pip install pyforge-init
```

Or install with `pipx`:

```bash
pipx install pyforge-init
```

---

## Quick Start

Create a new project:

```bash
newpython myproject
```

When run interactively, `pyforge` first shows a template picker, then asks for project details.

You can skip prompts entirely:

```bash
newpython myproject --yes
```

Or choose a template directly:

```bash
newpython myproject --template fastapi
```

---

## Template Quick Codes

Use these commands to create each built-in template quickly.

### Basic

Minimal package layout with a simple module entry point.

```bash
newpython myproject --template basic
```

Generated entry points:

- `src/myproject/main.py`
- `src/myproject/__main__.py`

Use this when you want a clean starting point for a library or small application.

### CLI

Click-based command-line application with a console script.

```bash
newpython mycli --template cli
```

Generated entry points:

- `src/mycli/cli.py`
- `src/mycli/__main__.py`

Use this when you want a terminal utility, automation tool, or developer CLI.

### FastAPI

API scaffold with a root route and a `/health` endpoint.

```bash
newpython api-service --template fastapi
```

Generated entry points:

- `src/api-service/main.py`

Use this when you want to start a JSON API or microservice.

### Flask

Factory-style Flask application with a test client and simple route.

```bash
newpython web-app --template flask
```

Generated entry points:

- `src/web-app/app.py`

Use this when you want a lightweight web app or server-rendered project.

---

## Interactive Template Picker

In an interactive terminal, the template picker shows:

1. `basic` - minimal package scaffold
2. `cli` - Click-based command-line app
3. `fastapi` - API scaffold with health endpoint
4. `flask` - Flask app factory scaffold
5. `custom GitHub template` - `gh:owner/repo[@ref]`

If you choose the custom GitHub option, `pyforge` will ask for a repository like `gh:username/repo` or `gh:username/repo@branch`.

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
  --no-pre-commit      Skip generating .pre-commit-config.yaml.
  --justfile           Generate a Justfile instead of a Makefile.
  -y, --yes            Skip interactive prompts and accept defaults.
  --help               Show this message and exit.
```

---

## What Gets Generated

All templates generate a standard project foundation:

- `pyproject.toml` with build, dependency, and tooling configuration
- `README.md` for the generated project
- `.gitignore`
- `.env.example`
- `requirements.txt`
- `Makefile` or `Justfile`
- Optional `.pre-commit-config.yaml`
- A `src/<project_name>/` package layout
- Template-specific tests and entry points

### Basic layout

```text
myproject/
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── __main__.py
│       └── main.py
├── tests/
│   └── test_main.py
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
├── README.md
├── pyproject.toml
└── requirements.txt
```

---

## Remote Templates

You can use any public GitHub repository as a template:

```bash
newpython myproject --template gh:username/repo-name
newpython myproject --template gh:username/repo-name@v1.0.0
```

Remote templates are copied as-is.

- If the repository contains a top-level `template/` folder, only that folder is copied.
- If there is no `template/` folder, the repository root is copied.

---

## Configuration File

`pyforge` reads defaults from `~/.newpythonrc`.

```toml
# ~/.newpythonrc
author = "Jane Doe"
license = "MIT"
template = "basic"
pre_commit = true
justfile = false
```

### Precedence

Settings are applied in this order:

1. CLI flags
2. `~/.newpythonrc`
3. Interactive defaults

To use a custom config file:

```bash
export NEWPYTHON_CONFIG="/path/to/custom/config.toml"
```

---

## Generated Project Commands

The generated `Makefile` or `Justfile` includes common development commands:

- `install` - install the project in editable mode with dev dependencies
- `test` - run the test suite
- `lint` - run Ruff checks
- `format` - format code with Ruff
- `run` - start the template-specific app or command
- `clean` - remove caches and build artifacts

---

## Publishing To PyPI

If you generate a package you want to publish, the project is already configured for `hatchling`.

```bash
pip install build twine
python -m build
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
