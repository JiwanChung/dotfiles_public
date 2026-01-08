"""Shell command execution utilities."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional

from .console import dim, error


def run(
    cmd: list[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    capture: bool = False,
    quiet: bool = False,
) -> subprocess.CompletedProcess:
    """Run a shell command.

    Args:
        cmd: Command and arguments as list
        cwd: Working directory
        check: Raise exception on non-zero exit
        capture: Capture stdout/stderr
        quiet: Don't print command

    Returns:
        CompletedProcess instance
    """
    if not quiet:
        dim(f"$ {' '.join(cmd)}")

    kwargs = {
        "cwd": cwd,
        "check": check,
    }

    if capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True

    return subprocess.run(cmd, **kwargs)


def run_quiet(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command silently, capturing output."""
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def has_command(cmd: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(cmd) is not None


def require_command(cmd: str, install_hint: str = ""):
    """Ensure a command exists, exit with error if not."""
    if not has_command(cmd):
        msg = f"Required command not found: {cmd}"
        if install_hint:
            msg += f" ({install_hint})"
        error(msg)
        raise SystemExit(1)
