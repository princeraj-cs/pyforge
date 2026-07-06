"""
Interactive TUI prompts for pyforge using questionary.

Provides a beautiful, npm-create-vite-style wizard for collecting project
configuration. Falls back to click.prompt/confirm when questionary is not
available (e.g., non-interactive/CI environments).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from pyforge.remote import is_remote_template, parse_gh_template
from pyforge.template_catalog import BUILTIN_TEMPLATE_CATALOG, BUILTIN_TEMPLATES

console = Console()

LICENSES = ["MIT", "Apache-2.0", "none"]


def _print_header(project_name: str) -> None:
    """Print the styled welcome banner."""
    title = Text("pyforge", style="bold cyan")
    subtitle = Text(f"Scaffolding project: {project_name}", style="dim")
    combined = Text.assemble(
        title,
        "\n",
        subtitle,
        "\n",
        Text("Choose a template, then fill in the project details.", style="dim"),
    )
    console.print(Panel(combined, border_style="cyan", padding=(1, 2)))
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
        return _ask_with_questionary(project_name, defaults, defaults.get("template"))
    else:
        console.print("[dim]Non-interactive mode — using defaults.[/dim]")
        return _ask_with_click(project_name, defaults)


def _print_template_catalog(default_template: Optional[str]) -> None:
    """Render a compact template catalog before the selector appears."""
    cards = []

    for template in BUILTIN_TEMPLATE_CATALOG:
        is_default = template.name == default_template
        title = f"{template.label}"
        if is_default:
            title = f"{title}  [default]"
        body = Text()
        body.append(f"{template.description}\n", style="white")
        body.append(f"Stack: {template.stack}\n", style="green")
        body.append(f"Entry: {template.entrypoint}\n", style="dim")
        body.append(f"Run: {template.run_command}", style="magenta")
        cards.append(
            Panel(
                body,
                title=title,
                border_style="cyan" if is_default else "bright_black",
                padding=(1, 2),
            )
        )

    console.print(Rule("Built-in templates", style="cyan"))
    console.print(Columns(cards, equal=True, expand=True))
    console.print()
    console.print(
        "[dim]Use the arrow keys to choose a built-in template, or pick a custom GitHub template.[/dim]"
    )
    console.print()


def _template_menu_choices(default_template: Optional[str]) -> list[dict[str, str]]:
    """Return numbered menu rows for the built-in templates plus the custom option."""
    choices = []
    for template in BUILTIN_TEMPLATE_CATALOG:
        title = f"{template.label} - {template.description}"
        if template.name == default_template:
            title = f"{title} [default]"
        choices.append({"label": title, "value": template.name})

    choices.append({"label": "Custom GitHub template - gh:owner/repo[@ref]", "value": "custom"})
    return choices


def _choose_template(default_template: Optional[str]) -> str:
    """Render a terminal-native template menu and return the chosen template."""
    _print_template_catalog(default_template)

    choices = _template_menu_choices(default_template)
    for index, choice in enumerate(choices, start=1):
        console.print(f"[bold cyan]{index}[/bold cyan]. {choice['label']}")

    default_index = 1
    if default_template and is_remote_template(default_template):
        default_index = len(choices)
    elif default_template in BUILTIN_TEMPLATES:
        default_index = next(
            (index for index, choice in enumerate(choices, start=1) if choice["value"] == default_template),
            1,
        )

    while True:
        raw_value = console.input(f"[bold]Choose a template[/bold] [dim]({default_index} default)[/dim]: ")
        selection = raw_value.strip()
        if not selection:
            selection = str(default_index)

        if selection.isdigit():
            selected_index = int(selection)
            if 1 <= selected_index <= len(choices):
                selected_value = choices[selected_index - 1]["value"]
                if selected_value == "custom":
                    remote_default = default_template if default_template and is_remote_template(default_template) else "gh:owner/repo"
                    return _prompt_remote_template(remote_default)
                return selected_value

        if selection in BUILTIN_TEMPLATES:
            return selection

        if is_remote_template(selection):
            try:
                parse_gh_template(selection)
            except ValueError:
                pass
            else:
                return selection

        console.print("[bold red]Enter a number from the menu, a built-in template name, or a gh: template.[/bold red]")


def _prompt_remote_template(default_remote: str) -> str:
    """Prompt for a remote GitHub template string and validate it."""
    while True:
        remote_template = console.input(
            f"[bold]Remote template[/bold] [dim](gh:owner/repo[@ref])[/dim] [cyan][{default_remote}] [/cyan]: "
        ).strip()
        if not remote_template:
            remote_template = default_remote
        if is_remote_template(remote_template):
            try:
                user, repo, ref = parse_gh_template(remote_template)
            except ValueError:
                pass
            else:
                console.print(
                    Panel(
                        f"Using [bold]{user}/{repo}[/bold] at [cyan]{ref}[/cyan]",
                        title="Remote template",
                        border_style="green",
                        padding=(0, 2),
                    )
                )
                return remote_template
        console.print(
            "[bold red]Enter a valid remote template like gh:owner/repo or gh:owner/repo@ref.[/bold red]"
        )


def _ask_with_questionary(project_name: str, defaults: Dict[str, Any], template: Optional[str]) -> Dict[str, Any]:
    """Collect answers using questionary (full TUI)."""
    import questionary
    from questionary import Style

    custom_style = Style([
        ("qmark", "fg:#00afff bold"),
        ("question", "bold"),
        ("answer", "fg:#70e1c8 bold"),
        ("pointer", "fg:#00afff bold"),
        ("highlighted", "fg:#00afff bold"),
        ("selected", "fg:#70e1c8"),
        ("separator", "fg:#6c6c6c"),
        ("instruction", "fg:#6c6c6c italic"),
    ])

    selected_template = template or defaults.get("template", "basic")
    if template is None:
        selected_template = _choose_template(defaults.get("template", "basic"))

    console.print(Rule("Project details", style="cyan"))

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
                          license_type, init_venv, init_git, selected_template)


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
                          license_type, init_venv, init_git, defaults.get("template", "basic"))


def _build_context(
    project_name: str,
    defaults: Dict[str, Any],
    description: str,
    author: str,
    license_type: str,
    init_venv: bool,
    init_git: bool,
    template: str,
) -> Dict[str, Any]:
    """Assemble the final context dict passed to the generator and actions."""
    return {
        "project_name": project_name,
        "description": description,
        "author": author,
        "license": license_type,
        "template": template,
        # template and tool flags come from CLI / config, not the wizard
        "init_venv": init_venv,
        "init_git": init_git,
    }
