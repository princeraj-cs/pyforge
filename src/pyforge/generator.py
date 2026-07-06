"""
Project scaffolding engine for pyforge.

Handles both local built-in templates (Jinja2-rendered) and remote
GitHub templates (plain file copy via remote.fetch_and_apply).
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from pyforge.remote import is_remote_template, fetch_and_apply


def get_templates_dir() -> Path:
    """Return the absolute path to the built-in templates directory."""
    return Path(__file__).parent / "templates"


def render_template(
    env: Environment,
    template_name: str,
    context: Dict[str, Any],
    output_path: Path,
) -> None:
    """Render a single Jinja2 template and write it to *output_path*."""
    # Jinja2 FileSystemLoader expects forward slashes on all platforms.
    template_name_posix = template_name.replace("\\", "/")
    template = env.get_template(template_name_posix)
    content = template.render(**context)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_project(
    project_path: Path,
    context: Dict[str, Any],
) -> None:
    """
    Generate the project files at *project_path* using *context*.

    Dispatches to the remote path when the template string starts with
    ``gh:``; otherwise renders local Jinja2 templates.
    """
    template_type = context.get("template", "basic")

    # ── Remote GitHub template ────────────────────────────────────────────────
    if is_remote_template(template_type):
        project_path.mkdir(parents=True, exist_ok=True)
        try:
            fetch_and_apply(template_type, project_path)
        except Exception:
            if project_path.exists():
                shutil.rmtree(project_path)
            raise
        return

    # ── Local Jinja2 template ─────────────────────────────────────────────────
    use_pre_commit = context.get("use_pre_commit", True)
    use_justfile = context.get("use_justfile", False)
    templates_dir = get_templates_dir()

    project_path.mkdir(parents=True, exist_ok=True)

    # Load templates: template-specific folder takes priority over shared.
    env = Environment(
        loader=FileSystemLoader(
            [
                str(templates_dir / template_type),
                str(templates_dir / "shared"),
            ]
        ),
        keep_trailing_newline=True,
    )

    try:
        # ── Shared files ──────────────────────────────────────────────────────
        render_template(
            env, "pyproject.toml.jinja", context, project_path / "pyproject.toml"
        )
        render_template(
            env, "gitignore.jinja", context, project_path / ".gitignore"
        )
        render_template(
            env, "env.example.jinja", context, project_path / ".env.example"
        )

        if use_pre_commit:
            render_template(
                env,
                "pre-commit-config.yaml.jinja",
                context,
                project_path / ".pre-commit-config.yaml",
            )

        makefile_name = "Justfile" if use_justfile else "Makefile"
        makefile_template = "Justfile.jinja" if use_justfile else "Makefile.jinja"
        render_template(
            env, makefile_template, context, project_path / makefile_name
        )

        # ── Template-specific files ───────────────────────────────────────────
        render_template(
            env, "README.md.jinja", context, project_path / "README.md"
        )
        render_template(
            env,
            "requirements.txt.jinja",
            context,
            project_path / "requirements.txt",
        )

        package_dir = project_path / "src" / context["project_name"]
        render_template(
            env,
            "src/package/__init__.py.jinja",
            context,
            package_dir / "__init__.py",
        )

        if template_type == "basic":
            render_template(
                env,
                "src/package/main.py.jinja",
                context,
                package_dir / "main.py",
            )
            render_template(
                env,
                "src/package/__main__.py.jinja",
                context,
                package_dir / "__main__.py",
            )
        if template_type == "cli":
            render_template(
                env,
                "src/package/__main__.py.jinja",
                context,
                package_dir / "__main__.py",
            )
            render_template(
                env, "src/package/cli.py.jinja", context, package_dir / "cli.py"
            )
            render_template(
                env,
                "tests/test_cli.py.jinja",
                context,
                project_path / "tests" / "test_cli.py",
            )
        elif template_type == "fastapi":
            render_template(
                env, "src/package/main.py.jinja", context, package_dir / "main.py"
            )
            render_template(
                env,
                "tests/test_main.py.jinja",
                context,
                project_path / "tests" / "test_main.py",
            )
        elif template_type == "flask":
            render_template(
                env, "src/package/app.py.jinja", context, package_dir / "app.py"
            )
            render_template(
                env,
                "tests/test_app.py.jinja",
                context,
                project_path / "tests" / "test_app.py",
            )
        else:  # basic
            render_template(
                env,
                "tests/test_main.py.jinja",
                context,
                project_path / "tests" / "test_main.py",
            )

    except Exception:
        # Clean up any partially-created project directory on failure.
        if project_path.exists():
            shutil.rmtree(project_path)
        raise
