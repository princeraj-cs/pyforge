"""Tests for pyforge.config — config file loading and validation."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from pyforge.config import load_config, _config_path, CONFIG_ENV_VAR


# ── _config_path ──────────────────────────────────────────────────────────────

def test_default_config_path():
    """Default path is ~/.newpythonrc."""
    # Unset env var to ensure we get the default.
    env = os.environ.copy()
    env.pop(CONFIG_ENV_VAR, None)
    old = os.environ.pop(CONFIG_ENV_VAR, None)
    try:
        path = _config_path()
        assert path == Path.home() / ".newpythonrc"
    finally:
        if old is not None:
            os.environ[CONFIG_ENV_VAR] = old


def test_env_var_overrides_config_path(tmp_path):
    """NEWPYTHON_CONFIG env var should override the default path."""
    custom = tmp_path / "custom_config.toml"
    os.environ[CONFIG_ENV_VAR] = str(custom)
    try:
        path = _config_path()
        assert path == custom
    finally:
        del os.environ[CONFIG_ENV_VAR]


# ── load_config — missing file ────────────────────────────────────────────────

def test_load_config_missing_file(tmp_path):
    """Missing config file returns an empty dict without error."""
    missing = tmp_path / "no_such_file.toml"
    os.environ[CONFIG_ENV_VAR] = str(missing)
    try:
        cfg = load_config()
        assert cfg == {}
    finally:
        del os.environ[CONFIG_ENV_VAR]


# ── load_config — valid file ──────────────────────────────────────────────────

def test_load_config_valid(tmp_path):
    """Valid config keys are loaded correctly."""
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        'author = "Jane Doe"\nlicense = "MIT"\npre_commit = true\n',
        encoding="utf-8",
    )
    os.environ[CONFIG_ENV_VAR] = str(config_file)
    try:
        cfg = load_config()
        assert cfg["author"] == "Jane Doe"
        assert cfg["license"] == "MIT"
        assert cfg["pre_commit"] is True
    finally:
        del os.environ[CONFIG_ENV_VAR]


# ── load_config — invalid / unknown keys ─────────────────────────────────────

def test_load_config_unknown_key_ignored(tmp_path):
    """Unknown keys are silently dropped (with a warning)."""
    config_file = tmp_path / "config.toml"
    config_file.write_text('author = "Ava"\nunknown_key = 42\n', encoding="utf-8")
    os.environ[CONFIG_ENV_VAR] = str(config_file)
    try:
        cfg = load_config()
        assert "unknown_key" not in cfg
        assert cfg["author"] == "Ava"
    finally:
        del os.environ[CONFIG_ENV_VAR]


def test_load_config_invalid_license_ignored(tmp_path):
    """An unrecognised license value is dropped."""
    config_file = tmp_path / "config.toml"
    config_file.write_text('license = "GPL-3.0"\n', encoding="utf-8")
    os.environ[CONFIG_ENV_VAR] = str(config_file)
    try:
        cfg = load_config()
        assert "license" not in cfg
    finally:
        del os.environ[CONFIG_ENV_VAR]


def test_load_config_wrong_type_ignored(tmp_path):
    """A key with the wrong TOML type is dropped."""
    config_file = tmp_path / "config.toml"
    # pre_commit should be bool, not string
    config_file.write_text('pre_commit = "yes"\n', encoding="utf-8")
    os.environ[CONFIG_ENV_VAR] = str(config_file)
    try:
        cfg = load_config()
        assert "pre_commit" not in cfg
    finally:
        del os.environ[CONFIG_ENV_VAR]


def test_load_config_gh_template_accepted(tmp_path):
    """A gh: template value in the config is accepted."""
    config_file = tmp_path / "config.toml"
    config_file.write_text('template = "gh:myorg/my-template"\n', encoding="utf-8")
    os.environ[CONFIG_ENV_VAR] = str(config_file)
    try:
        cfg = load_config()
        assert cfg["template"] == "gh:myorg/my-template"
    finally:
        del os.environ[CONFIG_ENV_VAR]


def test_load_config_bad_toml(tmp_path):
    """A malformed TOML file returns empty dict and does not crash."""
    config_file = tmp_path / "config.toml"
    config_file.write_bytes(b"this is not \x00 valid toml !!!")
    os.environ[CONFIG_ENV_VAR] = str(config_file)
    try:
        cfg = load_config()
        assert cfg == {}
    finally:
        del os.environ[CONFIG_ENV_VAR]
