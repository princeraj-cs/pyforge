"""
CLI entry point for pyforge (the `newpython` command).

Precedence for values (highest → lowest):
  1. CLI flags          (--template, --no-pre-commit, --justfile, --yes)
  2. Config file        (~/.newpythonrc)
  3. Interactive prompts / built-in defaults
"""
from __future__ import annotations

import sys
import click
from pathlib import Path
from rich.console import Console

from pyforge.config import load_config
from pyforge.prompts import ask_questions
from pyforge.utils import is_valid_package_name, create_virtual_environment, init_git_repo
from pyforge.generator import generate_project
from pyforge.remote import is_remote_template

console = Console()

BUILTIN_TEMPLATES = {"basic", "cli", "fastapi", "flask"}


def _validate_template(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Click callback that validates both built-in names and gh: strings."""
    if value in BUILTIN_TEMPLATES or is_remote_template(value):
        return value
    raise click.BadParameter(
        f"'{value}' is not a built-in template (basic, cli, fastapi, flask) "
        "and does not start with 'gh:'. "
        "Use --template basic or --template gh:username/repo."
    )


@click.command()
@click.argument("project_name")
@click.option(
    "--template",
    default="basic",
    show_default=True,
    callback=_validate_template,
    is_eager=True,
    help=(
        "Project template. Built-ins: basic, cli, fastapi, flask. "
        "Remote: gh:username/repo or gh:username/repo@ref."
    ),
)
@click.option(
    "--no-pre-commit",
    "no_pre_commit",
    is_flag=True,
    default=False,
    help="Skip generating .pre-commit-config.yaml.",
)
@click.option(
    "--justfile",
    is_flag=True,
    default=False,
    help="Generate a Justfile instead of a Makefile.",
)
@click.option(
    "--yes",
    "-y",
    "accept_defaults",
    is_flag=True,
    default=False,
    help="Accept all defaults — skip interactive prompts (useful for CI/scripting).",
)
def main(
    project_name: str,
    template: str,
    no_pre_commit: bool,
    justfile: bool,
    accept_defaults: bool,
) -> None:
    """✨ Scaffold a new Python project."""

    # ── Validate project name ─────────────────────────────────────────────────
    if not is_valid_package_name(project_name):
        console.print(
            f"[bold red]Error: '{project_name}' is not a valid Python package name.\n"
            "Package names must be valid Python identifiers (letters, digits, underscores; "
            "no hyphens or spaces).[/bold red]"
        )
        sys.exit(1)

    project_dir = Path.cwd() / project_name
    if project_dir.exists():
        console.print(
            f"[bold red]Error: Directory '{project_dir}' already exists.[/bold red]"
        )
        sys.exit(1)

    # ── Load config file defaults ─────────────────────────────────────────────
    cfg = load_config()

    # CLI flags override config-file values.
    # (no_pre_commit and justfile are False by default, so only override
    #  when the user actually passed the flag on the CLI.)
    effective_no_pre_commit = no_pre_commit or not cfg.get("pre_commit", True)
    effective_justfile = justfile or cfg.get("justfile", False)

    # Template: CLI always wins over config.
    # (template is already validated by the click callback)
    effective_template = template  # CLI value (default "basic" or user-supplied)
    if template == "basic" and "template" in cfg:
        # Only use config template when the CLI value is the pure default.
        effective_template = cfg["template"]

    # ── Collect answers ───────────────────────────────────────────────────────
    if accept_defaults:
        # Non-interactive: use config + built-in defaults, skip all prompts.
        context = {
            "project_name": project_name,
            "description": cfg.get("description", "A new Python project"),
            "author": cfg.get("author", "Your Name"),
            "license": cfg.get("license", "MIT"),
            "template": effective_template,
            "use_pre_commit": not effective_no_pre_commit,
            "use_justfile": effective_justfile,
        }
        init_venv = False
        init_git = False
    else:
        # Interactive: merge config defaults into the prompts.
        wizard_defaults = {
            "description": cfg.get("description", "A new Python project"),
            "author": cfg.get("author", "Your Name"),
            "license": cfg.get("license", "MIT"),
        }
        try:
            answers = ask_questions(project_name, wizard_defaults)
        except (KeyboardInterrupt, click.exceptions.Abort):
            console.print("\n[dim]Aborted.[/dim]")
            sys.exit(0)

        init_venv = answers.pop("init_venv", True)
        init_git = answers.pop("init_git", True)

        context = {
            **answers,
            "template": effective_template,
            "use_pre_commit": not effective_no_pre_commit,
            "use_justfile": effective_justfile,
        }

    # ── Generate project ──────────────────────────────────────────────────────
    try:
        generate_project(project_dir, context)
    except Exception as e:
        console.print(f"\n[bold red]✗ Error during project generation:[/bold red] {e}")
        sys.exit(1)

    # ── Post-generation actions ───────────────────────────────────────────────
    if init_venv:
        create_virtual_environment(project_dir)

    if init_git:
        init_git_repo(project_dir)

    # ── Success message ───────────────────────────────────────────────────────
    make_cmd = "just" if context["use_justfile"] else "make"

    console.print(
        f"\n[bold green]✓ Project [bold white]{project_name}[/bold white] created "
        f"with template [bold white]{effective_template}[/bold white]![/bold green]"
    )
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  [cyan]cd {project_name}[/cyan]")

    if init_venv:
        console.print(
            "  [cyan].venv\\Scripts\\activate[/cyan]"
            "  [dim]# Windows[/dim]"
        )
        console.print(
            "  [cyan]source .venv/bin/activate[/cyan]"
            "  [dim]# macOS / Linux[/dim]"
        )

    console.print(f"  [cyan]{make_cmd} install[/cyan]")

    if context["use_pre_commit"]:
        console.print("  [cyan]pre-commit install[/cyan]")

    console.print(f"  [cyan]{make_cmd} run[/cyan]")
    console.print()


if __name__ == "__main__":
    main()
