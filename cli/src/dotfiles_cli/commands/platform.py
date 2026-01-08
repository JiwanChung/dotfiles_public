"""Platform-specific commands."""

from ..config import get_config
from ..utils.console import success, error, warning, info, header, dim
from ..utils.run import run, has_command


def setup():
    """Run platform-specific setup."""
    cfg = get_config()

    if cfg.is_macos:
        _setup_macos(cfg)
    elif cfg.is_linux:
        _setup_linux(cfg)
    else:
        warning(f"No platform setup for: {cfg.platform}")


def update():
    """Update platform packages."""
    cfg = get_config()

    if cfg.is_macos:
        _update_macos()
    elif cfg.is_linux:
        _update_linux()
    else:
        warning(f"No platform update for: {cfg.platform}")


def _setup_macos(cfg):
    """macOS-specific setup."""
    header("macOS Setup")

    # Homebrew
    if not has_command("brew"):
        info("Installing Homebrew...")
        run(
            ["sh", "-c", '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'],
            check=False
        )
    else:
        dim("  Homebrew already installed")

    # Brewfile
    brewfile = cfg.platform_path / "mac" / "Brewfile"
    if brewfile.exists():
        info("Installing from Brewfile...")
        run(["brew", "bundle", f"--file={brewfile}"], check=False)
        success("Brewfile installed")

    # Mackup restore
    mackup_cfg = cfg.platform_path / "mac" / "mackup" / ".mackup.cfg"
    if mackup_cfg.exists() and has_command("mackup"):
        info("Restoring Mackup settings...")
        run(["mackup", "restore", "-f"], check=False)
        success("Mackup restored")


def _setup_linux(cfg):
    """Linux-specific setup."""
    header("Linux Setup")
    dim("  No additional setup configured")


def _update_macos():
    """Update macOS packages."""
    header("Updating macOS packages")

    if not has_command("brew"):
        error("Homebrew not installed")
        return

    info("Updating Homebrew...")
    run(["brew", "update"], check=False)

    info("Upgrading packages...")
    run(["brew", "upgrade"], check=False)

    info("Cleaning up...")
    run(["brew", "cleanup"], check=False)

    success("macOS packages updated")


def _update_linux():
    """Update Linux packages."""
    header("Updating Linux packages")
    dim("  No package manager configured")


# Windows-specific commands (WSL helpers)
def win_user():
    """Print Windows user profile path converted to WSL path."""
    if not has_command("cmd.exe") or not has_command("wslpath"):
        error("cmd.exe or wslpath not found")
        return

    result = run(
        ["cmd.exe", "/C", "echo", "%USERPROFILE%"],
        check=False,
        capture=True,
        quiet=True,
    )
    path = result.stdout.replace("\r", "").strip()
    if not path:
        error("Failed to resolve Windows user profile")
        return

    converted = run(["wslpath", path], check=False, capture=True, quiet=True)
    if converted.returncode != 0:
        error("Failed to convert Windows path with wslpath")
        return

    print(converted.stdout.strip())


def win_dist():
    """Print running WSL distributions."""
    if not has_command("wsl.exe"):
        error("wsl.exe not found")
        return

    result = run(
        ["wsl.exe", "-l", "--running", "-q"],
        check=False,
        capture=True,
        quiet=True,
    )
    if result.returncode != 0:
        error("Failed to list running WSL distributions")
        return

    output = result.stdout.replace("\r", "").replace("\0", "").strip()
    if output:
        print(output)


def win_run(cmd: list[str]):
    """Run a Windows command via cmd.exe."""
    if not cmd:
        error("No command provided")
        return

    if not has_command("cmd.exe"):
        error("cmd.exe not found")
        return

    run(["cmd.exe", "/C", *cmd], check=False)


# macOS-specific commands
def mac_backup():
    """Backup macOS app settings via Mackup."""
    if not has_command("mackup"):
        error("mackup not installed")
        return

    header("Backing up app settings")
    run(["mackup", "backup", "-f"], check=False)
    success("Backup complete")


def mac_restore():
    """Restore macOS app settings via Mackup."""
    if not has_command("mackup"):
        error("mackup not installed")
        return

    header("Restoring app settings")
    run(["mackup", "restore", "-f"], check=False)
    success("Restore complete")


def mac_brewfile():
    """Regenerate Brewfile from installed packages."""
    cfg = get_config()

    if not has_command("brew"):
        error("Homebrew not installed")
        return

    brewfile = cfg.platform_path / "mac" / "Brewfile"
    brewfile.parent.mkdir(parents=True, exist_ok=True)

    header("Generating Brewfile")
    run(["brew", "bundle", "dump", f"--file={brewfile}", "--force"], check=False)
    success(f"Brewfile written to: {brewfile}")
