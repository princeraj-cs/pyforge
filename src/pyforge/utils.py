import subprocess
import venv
from pathlib import Path
from rich.console import Console

console = Console()


def is_valid_package_name(name: str) -> bool:
    """Check if the given name is a valid Python package name."""
    import keyword

    if not name.isidentifier():
        return False
    # Python keywords can't be used as module names.
    if keyword.iskeyword(name):
        return False
    return True


def create_virtual_environment(project_dir: Path) -> None:
    """Create a virtual environment in the project directory."""
    venv_dir = project_dir / ".venv"
    try:
        console.print("[dim]Creating virtual environment...[/dim]")
        venv.create(venv_dir, with_pip=True)
    except Exception as e:
        console.print(
            f"[bold red]Failed to create virtual environment: {e}[/bold red]"
        )


def init_git_repo(project_dir: Path) -> None:
    """Initialize a git repository and make the initial commit."""
    try:
        console.print("[dim]Initializing git repository...[/dim]")
        subprocess.run(
            ["git", "init"],
            cwd=project_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["git", "add", "."],
            cwd=project_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=project_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        console.print(
            f"[bold yellow]Git initialization failed. Is git installed? (Error: {e})[/bold yellow]"
        )
    except FileNotFoundError:
        console.print(
            "[bold yellow]Git executable not found. Skipping git init.[/bold yellow]"
        )
