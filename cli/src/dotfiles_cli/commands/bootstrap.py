"""Bootstrap commands: bootstrap, doctor."""

from pathlib import Path
from typing import Optional

from ..config import get_config
from ..files.manifest import Manifest
from ..files.linker import check_symlink
from ..files.copier import check_copy
from ..utils.console import success, error, warning, info, header, dim, console, create_table
from ..utils.run import run, has_command, require_command
from . import sync, secrets


STAGES = ["files", "rust", "packages", "secrets", "platform", "shell"]


def bootstrap(stage: Optional[str] = None):
    """Complete system setup.

    Args:
        stage: Run specific stage only (comma-separated), or None for all
    """
    cfg = get_config()

    stages_to_run = STAGES
    if stage:
        stages_to_run = [s.strip() for s in stage.split(",")]
        for s in stages_to_run:
            if s not in STAGES:
                error(f"Unknown stage: {s}")
                info(f"Available stages: {', '.join(STAGES)}")
                return False

    header("Bootstrap")
    console.print(f"  Platform: {cfg.platform}")
    console.print(f"  Stages: {', '.join(stages_to_run)}")
    print()

    for i, s in enumerate(stages_to_run):
        stage_num = f"[{i+1}/{len(stages_to_run)}]"

        if s == "files":
            header(f"{stage_num} Applying files")
            sync.apply(force=True)

        elif s == "rust":
            header(f"{stage_num} Installing Rust")
            _stage_rust(cfg)

        elif s == "packages":
            header(f"{stage_num} Installing packages")
            _stage_packages(cfg)

        elif s == "secrets":
            header(f"{stage_num} Unlocking secrets")
            _stage_secrets(cfg)

        elif s == "platform":
            header(f"{stage_num} Platform setup ({cfg.platform})")
            _stage_platform(cfg)

        elif s == "shell":
            header(f"{stage_num} Shell setup")
            _stage_shell(cfg)

    print()
    success("Bootstrap complete!")
    return True


def _stage_rust(cfg):
    """Install Rust toolchain."""
    rust_script = cfg.scripts_path / "install_rust.sh"

    if rust_script.exists():
        run(["bash", str(rust_script)], check=False)
    elif not has_command("cargo"):
        info("Installing Rust via rustup...")
        run(
            ["sh", "-c", "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"],
            check=False
        )
    else:
        dim("  Rust already installed")


def _stage_packages(cfg):
    """Install packages via pkgmanager."""
    import os

    # Install pkgmanager if not available
    if not has_command("pkgmanager"):
        info("Installing pkgmanager from GitHub...")

        if not has_command("uv"):
            warning("uv not found, cannot install pkgmanager")
            info("Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh")
            return

        run(["uv", "tool", "install", "git+https://github.com/JiwanChung/pkgmanager.git"], check=False)

    # Verify installation
    if not has_command("pkgmanager"):
        warning("pkgmanager installation failed, skipping package installation")
        return

    env = os.environ.copy()
    env["PACKAGE_CONFIG"] = str(cfg.packages_yaml)

    run(["pkgmanager", "init"], check=False)


def _stage_secrets(cfg):
    """Unlock secrets if git-crypt is available and key exists."""
    git_crypt_dir = cfg.dotfiles_path / ".git" / "git-crypt"

    if not git_crypt_dir.exists():
        dim("  git-crypt not initialized, skipping")
        return

    if not has_command("git-crypt"):
        warning("git-crypt not found, skipping secrets unlock")
        info("Install with: brew install git-crypt")
        return

    if not cfg.git_crypt_key.exists():
        warning(f"Key not found at {cfg.git_crypt_key}")
        info("Copy your key or run: dotfiles secrets unlock -k /path/to/key")
        return

    secrets.unlock()


def _stage_platform(cfg):
    """Platform-specific setup."""
    if cfg.is_macos:
        _setup_macos(cfg)
    elif cfg.is_linux:
        _setup_linux(cfg)
    else:
        dim(f"  No platform setup for: {cfg.platform}")


def _setup_macos(cfg):
    """macOS-specific setup."""
    # Homebrew
    if not has_command("brew"):
        info("Installing Homebrew...")
        run(
            ["sh", "-c", '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'],
            check=False
        )

    # Brewfile
    brewfile = cfg.platform_path / "mac" / "Brewfile"
    if brewfile.exists():
        info("Installing from Brewfile...")
        run(["brew", "bundle", f"--file={brewfile}"], check=False)

    # Mackup restore
    mackup_cfg = cfg.platform_path / "mac" / "mackup" / ".mackup.cfg"
    if mackup_cfg.exists() and has_command("mackup"):
        info("Restoring Mackup settings...")
        run(["mackup", "restore", "-f"], check=False)


def _setup_linux(cfg):
    """Linux-specific setup."""
    dim("  Linux setup: (no additional steps configured)")


def _stage_shell(cfg):
    """Shell setup."""
    # Run shell-related scripts
    scripts = [
        ("install_helix.sh", "bash"),
        ("init_git_delta.sh", "bash"),
        ("install_fisher.fish", "fish"),
    ]

    for script, interpreter in scripts:
        script_path = cfg.scripts_path / script
        if script_path.exists():
            info(f"Running {script}...")
            run([interpreter, str(script_path)], check=False)


def doctor():
    """Verify system health."""
    cfg = get_config()

    header("System Health Check")

    checks = []

    # Check: Git repo exists
    git_dir = cfg.dotfiles_path / ".git"
    checks.append(("Git repo", git_dir.exists(), str(cfg.dotfiles_path)))

    # Check: files.yaml exists
    checks.append(("files.yaml", cfg.files_yaml.exists(), str(cfg.files_yaml)))

    # Check: Required tools
    tools = [
        ("git", ""),
        ("git-crypt", "brew install git-crypt"),
        ("fish", ""),
        ("pkgmanager", "dotfiles pkg install-tool"),
    ]
    for tool, hint in tools:
        checks.append((f"Tool: {tool}", has_command(tool), hint))

    # Check: git-crypt key
    checks.append(("git-crypt key", cfg.git_crypt_key.exists(), str(cfg.git_crypt_key)))

    # Check: GitHub auth
    gh_auth = False
    if has_command("gh"):
        from ..utils.run import run_quiet
        result = run_quiet(["gh", "auth", "status"])
        gh_auth = result.returncode == 0
    checks.append(("GitHub auth", gh_auth, "gh auth login"))

    # Print results
    table = create_table("Check", "Status", "Details")

    all_ok = True
    for name, ok, detail in checks:
        if ok:
            table.add_row(name, "[green]\u2713[/green]", detail or "[dim]-[/dim]")
        else:
            table.add_row(name, "[red]\u2717[/red]", detail or "")
            all_ok = False

    console.print(table)

    # Check file status
    print()
    header("File Status")
    manifest = Manifest.load(cfg.files_yaml)
    entries = manifest.for_platform(cfg.platform)

    if not entries:
        dim("  No files in manifest")
    else:
        issues = 0
        for entry in entries:
            source_abs = cfg.dotfiles_path / entry.source

            if not source_abs.exists():
                issues += 1
                continue

            if entry.type == "symlink":
                status = check_symlink(source_abs, entry.dest)
            else:
                status = check_copy(source_abs, entry.dest)

            if status != "ok":
                issues += 1

        if issues:
            warning(f"  {issues} file(s) need attention")
            info("  Run 'dotfiles diff' for details")
        else:
            success(f"  All {len(entries)} files OK")

    print()
    if all_ok:
        success("All checks passed")
    else:
        warning("Some checks failed")

    return all_ok
