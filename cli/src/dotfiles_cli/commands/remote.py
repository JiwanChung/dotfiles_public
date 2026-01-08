"""Remote deployment of dotfiles via SSH."""

from pathlib import Path
from typing import Optional

from ..config import get_config
from ..utils.console import success, error, warning, info, header, dim
from ..utils.run import run, run_quiet, has_command


def deploy(host: str, path: str = "~/dotfiles", bootstrap: bool = False):
    """Deploy dotfiles to a remote host via SSH.

    Args:
        host: SSH host (from ~/.ssh/config or user@hostname)
        path: Remote path for dotfiles (default: ~/dotfiles)
        bootstrap: Run bootstrap after deploy
    """
    cfg = get_config()

    if not has_command("rsync"):
        error("rsync not installed")
        return False

    header(f"Deploying to {host}")

    # Test SSH connection
    info("Testing SSH connection...")
    result = run_quiet(["ssh", "-o", "ConnectTimeout=5", host, "echo ok"])
    if result.returncode != 0:
        error(f"Cannot connect to {host}")
        return False

    # Create remote directory
    info(f"Creating remote directory: {path}")
    run_quiet(["ssh", host, f"mkdir -p {path}"])

    # Sync dotfiles
    info("Syncing dotfiles...")
    rsync_args = [
        "rsync", "-avz", "--delete",
        "--exclude", ".git",
        "--exclude", "public",
        "--exclude", "__pycache__",
        "--exclude", "*.pyc",
        "--exclude", ".venv",
        "--exclude", "backups",
        f"{cfg.dotfiles_path}/",
        f"{host}:{path}/"
    ]

    result = run(rsync_args, check=False)
    if result.returncode != 0:
        error("rsync failed")
        return False

    success("Dotfiles synced")

    # Install CLI on remote
    info("Installing dotfiles-cli on remote...")
    install_cmd = f"cd {path} && uv tool install .dotfiles/dotfiles-cli --force 2>/dev/null || pip install --user .dotfiles/dotfiles-cli"
    result = run_quiet(["ssh", host, install_cmd])

    if result.returncode == 0:
        success("CLI installed on remote")
    else:
        warning("CLI installation may have failed (uv/pip might not be available)")

    # Run bootstrap if requested
    if bootstrap:
        info("Running bootstrap on remote...")
        bootstrap_cmd = f"export DOTFILES={path} && dotfiles bootstrap"
        run(["ssh", "-t", host, bootstrap_cmd], check=False)

    success(f"Deployed to {host}:{path}")
    info(f"SSH in and run: DOTFILES={path} dotfiles apply")
    return True


def sync_from(host: str, path: str = "~/dotfiles"):
    """Sync dotfiles from a remote host.

    Args:
        host: SSH host
        path: Remote dotfiles path
    """
    cfg = get_config()

    if not has_command("rsync"):
        error("rsync not installed")
        return False

    header(f"Syncing from {host}")

    # Test SSH connection
    result = run_quiet(["ssh", "-o", "ConnectTimeout=5", host, "echo ok"])
    if result.returncode != 0:
        error(f"Cannot connect to {host}")
        return False

    # Sync from remote
    info("Syncing dotfiles from remote...")
    rsync_args = [
        "rsync", "-avz",
        "--exclude", ".git",
        "--exclude", "public",
        "--exclude", "__pycache__",
        "--exclude", "*.pyc",
        "--exclude", ".venv",
        f"{host}:{path}/",
        f"{cfg.dotfiles_path}/"
    ]

    result = run(rsync_args, check=False)
    if result.returncode != 0:
        error("rsync failed")
        return False

    success(f"Synced from {host}:{path}")
    return True
