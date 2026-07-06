"""Tests for pyforge.generator and pyforge.remote parsing."""
from __future__ import annotations

import io
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from pyforge.generator import generate_project
from pyforge.remote import parse_gh_template, is_remote_template


# ── Local template generation ─────────────────────────────────────────────────

def _base_context(**overrides):
    ctx = {
        "project_name": "testproject",
        "description": "A test",
        "author": "Test Author",
        "license": "MIT",
        "template": "basic",
        "use_pre_commit": True,
        "use_justfile": False,
    }
    ctx.update(overrides)
    return ctx


def test_generate_project_basic(tmp_path):
    project_dir = tmp_path / "testproject"
    generate_project(project_dir, _base_context())

    assert project_dir.exists()
    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "README.md").exists()
    assert (project_dir / ".env.example").exists()
    assert (project_dir / "Makefile").exists()
    assert not (project_dir / "Justfile").exists()
    assert (project_dir / ".pre-commit-config.yaml").exists()
    assert (project_dir / "src" / "testproject" / "__init__.py").exists()
    assert (project_dir / "src" / "testproject" / "main.py").exists()
    assert (project_dir / "src" / "testproject" / "__main__.py").exists()
    assert (project_dir / "tests" / "test_main.py").exists()


def test_generate_project_fastapi_justfile(tmp_path):
    project_dir = tmp_path / "fastapiapp"
    ctx = _base_context(
        project_name="fastapiapp",
        template="fastapi",
        use_pre_commit=False,
        use_justfile=True,
    )
    generate_project(project_dir, ctx)

    assert project_dir.exists()
    assert (project_dir / "Justfile").exists()
    assert not (project_dir / "Makefile").exists()
    assert not (project_dir / ".pre-commit-config.yaml").exists()
    assert (project_dir / ".env.example").exists()
    assert (project_dir / "src" / "fastapiapp" / "main.py").exists()
    assert (project_dir / "tests" / "test_main.py").exists()


def test_generate_project_cli_template(tmp_path):
    project_dir = tmp_path / "mycli"
    ctx = _base_context(project_name="mycli", template="cli")
    generate_project(project_dir, ctx)

    assert (project_dir / "src" / "mycli" / "cli.py").exists()
    assert (project_dir / "src" / "mycli" / "__main__.py").exists()
    assert (project_dir / "tests" / "test_cli.py").exists()


def test_generate_project_flask_template(tmp_path):
    project_dir = tmp_path / "myflask"
    ctx = _base_context(project_name="myflask", template="flask")
    generate_project(project_dir, ctx)

    assert (project_dir / "src" / "myflask" / "app.py").exists()
    assert (project_dir / "tests" / "test_app.py").exists()


def test_generate_project_cleanup_on_failure(tmp_path):
    """If generation fails halfway, the partial directory is removed."""
    project_dir = tmp_path / "failproject"
    ctx = _base_context(project_name="failproject")

    with patch("pyforge.generator.render_template", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            generate_project(project_dir, ctx)

    assert not project_dir.exists()


# ── Remote template parsing ───────────────────────────────────────────────────

def test_is_remote_template_true():
    assert is_remote_template("gh:user/repo") is True
    assert is_remote_template("gh:org/my-template@v1") is True


def test_is_remote_template_false():
    assert is_remote_template("basic") is False
    assert is_remote_template("fastapi") is False
    assert is_remote_template("github:user/repo") is False  # wrong prefix


def test_parse_gh_template_simple():
    user, repo, ref = parse_gh_template("gh:alice/my-template")
    assert user == "alice"
    assert repo == "my-template"
    assert ref == "main"


def test_parse_gh_template_with_ref():
    user, repo, ref = parse_gh_template("gh:org/templates@v2.1.0")
    assert user == "org"
    assert repo == "templates"
    assert ref == "v2.1.0"


def test_parse_gh_template_branch_ref():
    user, repo, ref = parse_gh_template("gh:bob/scaffold@develop")
    assert ref == "develop"


@pytest.mark.parametrize("bad_input", [
    "gh:",
    "gh:missingslash",
    "gh:/no-user",
    "gh:user/",
])
def test_parse_gh_template_invalid(bad_input):
    with pytest.raises(ValueError, match="Invalid remote template"):
        parse_gh_template(bad_input)


# ── Remote template fetch (mocked) ────────────────────────────────────────────

def _make_zip(file_tree: dict, prefix: str = "myrepo-main/") -> bytes:
    """Build an in-memory ZIP matching GitHub's archive format."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.mkdir(prefix)  # top-level dir entry
        for name, content in file_tree.items():
            zf.writestr(prefix + name, content)
    return buf.getvalue()


def test_remote_template_with_template_dir(tmp_path):
    """Files inside template/ are extracted; files outside are ignored."""
    from pyforge.remote import fetch_and_apply

    zip_data = _make_zip({
        "README.md": "# outer readme",         # should be IGNORED
        "template/README.md": "# inner readme",  # should be copied
        "template/src/main.py": "print('hi')",
    })

    with patch("pyforge.remote._download_zip", return_value=zip_data):
        project_dir = tmp_path / "remoteproject"
        project_dir.mkdir()
        fetch_and_apply("gh:user/myrepo", project_dir)

    assert (project_dir / "README.md").read_text() == "# inner readme"
    assert (project_dir / "src" / "main.py").read_text() == "print('hi')"


def test_remote_template_no_template_dir(tmp_path):
    """When no template/ dir exists, the full repo root is copied."""
    from pyforge.remote import fetch_and_apply

    zip_data = _make_zip({
        "README.md": "# root readme",
        "main.py": "x = 1",
    })

    with patch("pyforge.remote._download_zip", return_value=zip_data):
        project_dir = tmp_path / "remoteproject2"
        project_dir.mkdir()
        fetch_and_apply("gh:user/bare-repo", project_dir)

    assert (project_dir / "README.md").read_text() == "# root readme"
    assert (project_dir / "main.py").read_text() == "x = 1"
