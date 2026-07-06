"""
Interactive TUI prompts for pyforge using questionary.

Provides a beautiful, npm-create-vite-style wizard for collecting project
configuration. Falls back to click.prompt/confirm when questionary is not
available (e.g., non-interactive/CI environments).
"""
from __future__ import annotations

from typing import Any, Dict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

BUILTIN_TEMPLATES = ["basic", "cli", "fastapi", "flask"]
LICENSES = ["MIT", "Apache-2.0", "none"]


def _print_header(project_name: str) -> None:
    """Print the styled welcome banner."""
    title = Text("✨  newpython", style="bold cyan")
    subtitle = Text(f"Scaffolding project: {project_name}", style="dim")
    combined = Text.assemble(title, "\n", subtitle)
    console.print(Panel(combined, border_style="cyan", padding=(0, 2)))
    console.print()


def _is_interactive() -> bool:
    """Return True if we are attached to a real TTY."""
    import sys
    return sys.stdin.isatty()


def ask_questions(project_name: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the interactive questionary wizard (or fall back to click prompts in CI).

    Args:
        project_name: The project name already validated and accepted via CLI arg.
        defaults: Pre-populated values from the config file.

    Returns:
        A fully populated context dict ready for the generator.
    """
    _print_header(project_name)

    if _is_interactive():
        return _ask_with_questionary(project_name, defaults)
    else:
        console.print("[dim]Non-interactive mode — using defaults.[/dim]")
        return _ask_with_click(project_name, defaults)


def _ask_with_questionary(project_name: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    """Collect answers using questionary (full TUI)."""
    import questionary
    from questionary import Style

    custom_style = Style([
        ("qmark",        "fg:#5f87ff bold"),
        ("question",     "bold"),
        ("answer",       "fg:#5fd7ff bold"),
        ("pointer",      "fg:#5f87ff bold"),
        ("highlighted",  "fg:#5f87ff bold"),
        ("selected",     "fg:#5fd7ff"),
        ("separator",    "fg:#6c6c6c"),
        ("instruction",  "fg:#6c6c6c italic"),
    ])

    # ── Description ───────────────────────────────────────────────────────────
    description = questionary.text(
        "Project description:",
        default=defaults.get("description", "A new Python project"),
        style=custom_style,
    ).ask()
    if description is None:  # user hit Ctrl-C
        raise KeyboardInterrupt

    # ── Author ─────────────────────────────────────────────────────────────────
    author = questionary.text(
        "Author name:",
        default=defaults.get("author", "Your Name"),
        style=custom_style,
    ).ask()
    if author is None:
        raise KeyboardInterrupt

    # ── License ────────────────────────────────────────────────────────────────
    license_default = defaults.get("license", "MIT")
    license_type = questionary.select(
        "License:",
        choices=LICENSES,
        default=license_default if license_default in LICENSES else "MIT",
        style=custom_style,
    ).ask()
    if license_type is None:
        raise KeyboardInterrupt

    # ── Virtual environment ────────────────────────────────────────────────────
    init_venv = questionary.confirm(
        "Initialize a virtual environment (.venv)?",
        default=True,
        style=custom_style,
    ).ask()
    if init_venv is None:
        raise KeyboardInterrupt

    # ── Git ────────────────────────────────────────────────────────────────────
    init_git = questionary.confirm(
        "Initialize a git repository?",
        default=True,
        style=custom_style,
    ).ask()
    if init_git is None:
        raise KeyboardInterrupt

    console.print()
    return _build_context(project_name, defaults, description, author,
                          license_type, init_venv, init_git)


def _ask_with_click(project_name: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback: collect answers using plain click prompts (CI / non-TTY)."""
    import click

    description = click.prompt(
        "Project description",
        default=defaults.get("description", "A new Python project"),
    )
    author = click.prompt(
        "Author name",
        default=defaults.get("author", "Your Name"),
    )
    license_type = click.prompt(
        "License",
        type=click.Choice(LICENSES),
        default=defaults.get("license", "MIT"),
    )
    init_venv = click.confirm("Initialize virtual environment?", default=True)
    init_git = click.confirm("Initialize git repository?", default=True)

    return _build_context(project_name, defaults, description, author,
                          license_type, init_venv, init_git)


def _build_context(
    project_name: str,
    defaults: Dict[str, Any],
    description: str,
    author: str,
    license_type: str,
    init_venv: bool,
    init_git: bool,
) -> Dict[str, Any]:
    """Assemble the final context dict passed to the generator and actions."""
    return {
        "project_name": project_name,
        "description": description,
        "author": author,
        "license": license_type,
        # template and tool flags come from CLI / config, not the wizard
        "init_venv": init_venv,
        "init_git": init_git,
    }
