"""Script runner commands."""

from pathlib import Path

from ..config import get_config
from ..utils.console import success, error, info, header, console
from ..utils.run import run


def run_script(name: str):
    """Run a script from scripts/ directory.

    Args:
        name: Script name (with or without .sh extension)
    """
    cfg = get_config()

    # Add .sh extension if not present
    if not name.endswith(".sh") and not name.endswith(".fish"):
        name = f"{name}.sh"

    script_path = cfg.scripts_path / name

    if not script_path.exists():
        error(f"Script not found: {name}")
        info(f"Available scripts: dotfiles run --list")
        return False

    header(f"Running {name}")

    # Determine interpreter
    if name.endswith(".fish"):
        interpreter = "fish"
    else:
        interpreter = "bash"

    result = run([interpreter, str(script_path)], check=False)

    if result.returncode == 0:
        success(f"Script completed: {name}")
        return True
    else:
        error(f"Script failed with exit code {result.returncode}")
        return False


def list_scripts():
    """List available scripts."""
    cfg = get_config()

    header("Available scripts")

    if not cfg.scripts_path.exists():
        info("No scripts directory found")
        return

    scripts = sorted(cfg.scripts_path.glob("*"))
    scripts = [s for s in scripts if s.is_file() and not s.name.startswith(".")]

    if not scripts:
        info("No scripts found")
        return

    for script in scripts:
        console.print(f"  {script.name}")
