"""Tests for the interactive prompt helpers."""
from __future__ import annotations

from pyforge.prompts import _template_menu_choices


def test_template_menu_choices_include_custom_remote_option():
    choices = _template_menu_choices("fastapi")

    assert choices[-1] == {"label": "Custom GitHub template - gh:owner/repo[@ref]", "value": "custom"}
    assert any(choice["value"] == "fastapi" and "FastAPI service" in choice["label"] for choice in choices)
    assert any(choice["value"] == "fastapi" and "[default]" in choice["label"] for choice in choices)