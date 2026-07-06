"""
Config file support for pyforge.

Reads defaults from ~/.newpythonrc (TOML format).
The path can be overridden with the NEWPYTHON_CONFIG environment variable.

Example ~/.newpythonrc:
    author     = "Jane Doe"
    license    = "MIT"
    template   = "basic"
    pre_commit = true
    justfile   = false
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict


# Use stdlib tomllib on Python 3.11+, fall back to tomli on older versions.
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

CONFIG_ENV_VAR = "NEWPYTHON_CONFIG"
DEFAULT_CONFIG_PATH = Path.home() / ".newpythonrc"

# Recognised keys and their expected types for validation.
KNOWN_KEYS: Dict[str, type] = {
    "author": str,
    "license": str,
    "template": str,
    "pre_commit": bool,
    "justfile": bool,
}

VALID_LICENSES = {"MIT", "Apache-2.0", "none"}
BUILTIN_TEMPLATES = {"basic", "cli", "fastapi", "flask"}


def _config_path() -> Path:
    """Return the config file path, respecting the env-var override."""
    env_override = os.environ.get(CONFIG_ENV_VAR)
    if env_override:
        return Path(env_override).expanduser()
    return DEFAULT_CONFIG_PATH


def load_config() -> Dict[str, Any]:
    """
    Load defaults from ~/.newpythonrc.

    Returns an empty dict if the file does not exist or tomllib is unavailable.
    Prints a warning and returns an empty dict on parse errors (never crashes).
    """
    if tomllib is None:
        # tomli not installed and Python < 3.11 — gracefully degrade.
        return {}

    path = _config_path()
    if not path.exists():
        return {}

    try:
        with open(path, "rb") as fh:
            raw = tomllib.load(fh)
    except Exception as exc:
        from rich.console import Console
        Console().print(
            f"[bold yellow]⚠ Could not parse config file {path}: {exc}[/bold yellow]"
        )
        return {}

    return _validate(raw, path)


def _validate(raw: Dict[str, Any], path: Path) -> Dict[str, Any]:
    """Validate and normalise the raw TOML data. Unknown/invalid keys are dropped with a warning."""
    from rich.console import Console
    console = Console()
    clean: Dict[str, Any] = {}

    for key, value in raw.items():
        if key not in KNOWN_KEYS:
            console.print(
                f"[dim yellow]Config: ignoring unknown key '{key}' in {path}[/dim yellow]"
            )
            continue
        expected_type = KNOWN_KEYS[key]
        if not isinstance(value, expected_type):
            console.print(
                f"[dim yellow]Config: '{key}' should be {expected_type.__name__}, "
                f"got {type(value).__name__} — ignoring.[/dim yellow]"
            )
            continue

        # Domain validation
        if key == "license" and value not in VALID_LICENSES:
            console.print(
                f"[dim yellow]Config: 'license' must be one of "
                f"{sorted(VALID_LICENSES)}, got '{value}' — ignoring.[/dim yellow]"
            )
            continue
        if key == "template" and value not in BUILTIN_TEMPLATES and not value.startswith("gh:"):
            console.print(
                f"[dim yellow]Config: 'template' '{value}' is not a built-in template "
                f"and doesn't start with 'gh:' — ignoring.[/dim yellow]"
            )
            continue

        clean[key] = value

    return clean
