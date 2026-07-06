"""Metadata for the built-in pyforge templates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class TemplateInfo:
    """Describe a built-in template for display and validation."""

    name: str
    label: str
    description: str
    stack: str
    entrypoint: str
    run_command: str


BUILTIN_TEMPLATE_CATALOG: Tuple[TemplateInfo, ...] = (
    TemplateInfo(
        name="basic",
        label="Basic package",
        description="Minimal package with a real entry point and starter test.",
        stack="stdlib only",
        entrypoint="src/{{ project_name }}/main.py",
        run_command="python -m {{ project_name }}",
    ),
    TemplateInfo(
        name="cli",
        label="Click CLI",
        description="Console application with a click command and script entry point.",
        stack="click",
        entrypoint="src/{{ project_name }}/cli.py",
        run_command="{{ project_name }}",
    ),
    TemplateInfo(
        name="fastapi",
        label="FastAPI service",
        description="API service scaffold with a simple root route and TestClient test.",
        stack="fastapi + uvicorn + httpx",
        entrypoint="src/{{ project_name }}/main.py",
        run_command="uvicorn src.{{ project_name }}.main:app --reload",
    ),
    TemplateInfo(
        name="flask",
        label="Flask app",
        description="Factory-style web app with a clean app factory and test client.",
        stack="flask",
        entrypoint="src/{{ project_name }}/app.py",
        run_command="flask run",
    ),
)

BUILTIN_TEMPLATES: Tuple[str, ...] = tuple(info.name for info in BUILTIN_TEMPLATE_CATALOG)
BUILTIN_TEMPLATE_SET = set(BUILTIN_TEMPLATES)


def get_template_info(name: str) -> Optional[TemplateInfo]:
    """Return the catalog entry for a built-in template name."""
    for template in BUILTIN_TEMPLATE_CATALOG:
        if template.name == name:
            return template
    return None