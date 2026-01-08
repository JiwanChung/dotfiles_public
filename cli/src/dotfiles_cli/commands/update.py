"""Self-update for dotfiles-cli."""

from pathlib import Path

from ..config import get_config
from ..utils.console import success, error, info, header
from ..utils.run import run, run_quiet, has_command


def update_cli():
    """Update dotfiles-cli to latest version."""
    cfg = get_config()
    cli_path = cfg.dotfiles_internal / "dotfiles-cli"

    if not cli_path.exists():
        error(f"CLI source not found: {cli_path}")
        return False

    header("Updating dotfiles-cli")

    # Pull latest changes first
    info("Pulling latest changes...")
    result = run_quiet(["git", "-C", str(cfg.dotfiles_path), "pull"])
    if result.returncode != 0:
        error("Failed to pull latest changes")

    # Reinstall CLI
    if has_command("uv"):
        info("Reinstalling with uv...")
        result = run(
            ["uv", "tool", "install", str(cli_path), "--force"],
            check=False
        )
    elif has_command("pip"):
        info("Reinstalling with pip...")
        result = run(
            ["pip", "install", "--user", "--upgrade", str(cli_path)],
            check=False
        )
    else:
        error("Neither uv nor pip found")
        return False

    if result.returncode == 0:
        success("dotfiles-cli updated")
        return True
    else:
        error("Update failed")
        return False


def version():
    """Show version information."""
    try:
        from importlib.metadata import version as get_version
        ver = get_version("dotfiles-cli")
    except Exception:
        ver = "unknown"

    print(f"dotfiles-cli {ver}")
