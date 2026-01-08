"""Package commands: wrapper around pkgmanager."""

from typing import Optional

from ..config import get_config
from ..utils.console import error, info, success
from ..utils.run import run, has_command


PKGMANAGER_REPO = "git+https://github.com/JiwanChung/pkgmanager.git"


def _check_pkgmanager():
    """Check if pkgmanager is available."""
    if not has_command("pkgmanager"):
        error("pkgmanager not found")
        info("Install with: dotfiles pkg install-tool")
        info("  or manually: uv tool install git+https://github.com/JiwanChung/pkgmanager.git")
        return False
    return True


def install_tool():
    """Install pkgmanager itself."""
    if has_command("pkgmanager"):
        success("pkgmanager is already installed")
        return

    if not has_command("uv"):
        error("uv not found")
        info("Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return

    info("Installing pkgmanager from GitHub...")
    run(["uv", "tool", "install", PKGMANAGER_REPO], check=False)

    if has_command("pkgmanager"):
        success("pkgmanager installed successfully")
    else:
        error("pkgmanager installation failed")


def _run_pkgmanager(*args):
    """Run pkgmanager with given arguments."""
    import os
    cfg = get_config()

    env = os.environ.copy()
    env["PACKAGE_CONFIG"] = str(cfg.packages_yaml)

    run(["pkgmanager", *args], check=False)


def init(types: Optional[str] = None):
    """Install all packages from manifest.

    Args:
        types: Comma-separated package types (conda,python,rust)
    """
    if not _check_pkgmanager():
        return

    args = ["init"]
    if types:
        args.extend(["--types", types])

    _run_pkgmanager(*args)


def install(type: str, name: str):
    """Install and track a package.

    Args:
        type: Package type (conda, python, rust)
        name: Package name
    """
    if not _check_pkgmanager():
        return

    _run_pkgmanager("install", type, name)


def remove(type: str, name: str):
    """Remove and untrack a package.

    Args:
        type: Package type (conda, python, rust)
        name: Package name
    """
    if not _check_pkgmanager():
        return

    _run_pkgmanager("remove", type, name)


def update():
    """Update all packages."""
    if not _check_pkgmanager():
        return

    _run_pkgmanager("update")


def list_packages():
    """List installed packages."""
    if not _check_pkgmanager():
        return

    _run_pkgmanager("list")
