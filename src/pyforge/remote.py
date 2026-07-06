"""
Remote GitHub template support for pyforge.

Parses `gh:user/repo` and `gh:user/repo@ref` template strings,
downloads the GitHub repository as a ZIP archive, and copies its
contents into the target project directory (degit-style: plain file copy,
no Jinja rendering).

Template directory convention
------------------------------
If the downloaded repo contains a top-level `template/` directory, only
that subdirectory is copied. Otherwise the entire repo root is copied.
This lets template authors keep docs, CI config, etc. outside the
scaffolded content.
"""
from __future__ import annotations

import io
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Tuple


def is_remote_template(template: str) -> bool:
    """Return True if the template string refers to a remote GitHub repo."""
    return template.startswith("gh:")


def parse_gh_template(template: str) -> Tuple[str, str, str]:
    """
    Parse a `gh:user/repo@ref` string.

    Returns:
        (user, repo, ref)  — ref defaults to "main".

    Raises:
        ValueError: if the string cannot be parsed.
    """
    body = template[3:]  # strip "gh:"
    ref = "main"

    if "@" in body:
        body, ref = body.rsplit("@", 1)

    parts = body.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError(
            f"Invalid remote template '{template}'. "
            "Expected format: gh:username/repo or gh:username/repo@ref"
        )

    user, repo = parts
    return user, repo, ref


def _zip_url(user: str, repo: str, ref: str) -> str:
    return f"https://github.com/{user}/{repo}/archive/refs/heads/{ref}.zip"


def _zip_url_tag(user: str, repo: str, ref: str) -> str:
    """Alternative URL used when the ref is a tag rather than a branch."""
    return f"https://github.com/{user}/{repo}/archive/refs/tags/{ref}.zip"


def fetch_and_apply(template: str, project_path: Path) -> None:
    """
    Download a GitHub repo and copy its template content into *project_path*.

    Uses a Rich spinner for visual feedback during the download.

    Args:
        template:     The `gh:user/repo[@ref]` string.
        project_path: The (already created) destination project directory.

    Raises:
        RuntimeError: on network errors, 404s, or ZIP extraction failures.
    """
    import httpx
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn

    console = Console()
    user, repo, ref = parse_gh_template(template)

    url = _zip_url(user, repo, ref)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task(
            f"[cyan]Fetching [bold]{user}/{repo}[/bold] @ {ref}…", total=None
        )

        zip_bytes = _download_zip(url, user, repo, ref)
        progress.update(task, description=f"[cyan]Unpacking [bold]{user}/{repo}[/bold]…")
        _extract_zip(zip_bytes, repo, ref, project_path)

    console.print(
        f"[green]✓ Remote template [bold]{user}/{repo}[/bold] applied.[/green]"
    )


def _download_zip(url: str, user: str, repo: str, ref: str) -> bytes:
    """Download the ZIP, retrying the tag URL if the branch URL returns 404."""
    import httpx

    try:
        response = httpx.get(url, follow_redirects=True, timeout=30)
        if response.status_code == 404:
            # Try interpreting the ref as a tag instead of a branch
            tag_url = _zip_url_tag(user, repo, ref)
            response = httpx.get(tag_url, follow_redirects=True, timeout=30)
        response.raise_for_status()
        return response.content
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Could not download template from GitHub "
            f"({exc.response.status_code}). "
            f"Check that '{user}/{repo}' exists and ref '{ref}' is valid."
        ) from exc
    except httpx.RequestError as exc:
        raise RuntimeError(
            f"Network error while fetching template: {exc}"
        ) from exc


def _extract_zip(
    zip_bytes: bytes,
    repo: str,
    ref: str,
    project_path: Path,
) -> None:
    """
    Extract the ZIP archive and copy the template content to project_path.

    GitHub archives are wrapped in a top-level `<repo>-<ref>/` folder.
    We strip that prefix, then look for an inner `template/` subdirectory.
    If found, only its contents are copied; otherwise the whole archive root
    is copied.
    """
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            # Determine the top-level prefix GitHub adds (e.g. "myrepo-main/")
            names = zf.namelist()
            if not names:
                raise RuntimeError("Downloaded ZIP archive is empty.")

            prefix = names[0].split("/")[0] + "/"

            # Decide which sub-path to extract from inside the archive
            template_prefix = prefix + "template/"
            has_template_dir = any(n.startswith(template_prefix) for n in names)
            source_prefix = template_prefix if has_template_dir else prefix

            # Extract matching entries into the project directory
            for member in zf.infolist():
                if not member.filename.startswith(source_prefix):
                    continue
                # Compute relative path inside the project
                relative = member.filename[len(source_prefix):]
                if not relative:
                    continue  # skip the directory entry itself

                dest = project_path / relative

                if member.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(zf.read(member.filename))

    except zipfile.BadZipFile as exc:
        raise RuntimeError(
            f"Downloaded file is not a valid ZIP archive: {exc}"
        ) from exc
