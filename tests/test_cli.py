"""Tests for the pyforge CLI (click entry point)."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from pyforge.cli import main


def test_cli_invalid_name():
    """Hyphens make an invalid Python package name."""
    runner = CliRunner()
    result = runner.invoke(main, ["invalid-name"])
    assert result.exit_code != 0
    assert "not a valid Python package name" in result.output


def test_cli_existing_directory(tmp_path):
    """Fails gracefully if the target directory already exists."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as cwd:
        # Create the conflicting directory inside the runner's CWD
        (Path(cwd) / "myproject").mkdir()
        result = runner.invoke(main, ["myproject", "--yes"])
    assert result.exit_code != 0
    assert "already exists" in result.output


def test_cli_yes_flag_creates_project(tmp_path):
    """--yes skips prompts and generates the project with defaults."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as cwd:
        result = runner.invoke(main, ["myproject", "--yes", "--no-pre-commit"])
        assert result.exit_code == 0, result.output
        assert (Path(cwd) / "myproject" / "pyproject.toml").exists()


def test_cli_invalid_template():
    """An unrecognised, non-gh: template string raises BadParameter."""
    runner = CliRunner()
    result = runner.invoke(main, ["myproject", "--template", "django"])
    assert result.exit_code != 0
    assert "Invalid value for '--template'" in result.output


def test_cli_gh_template_accepted(tmp_path):
    """gh: template strings pass validation and reach generate_project."""
    runner = CliRunner()
    with patch("pyforge.cli.generate_project") as mock_gen:
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                main,
                ["myproject", "--template", "gh:user/repo", "--yes"],
            )
    assert result.exit_code == 0, result.output
    mock_gen.assert_called_once()
    ctx = mock_gen.call_args[0][1]
    assert ctx["template"] == "gh:user/repo"
