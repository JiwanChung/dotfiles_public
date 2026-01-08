"""Main CLI entry point for dotfiles-cli."""

from typing import Annotated, Optional

from cyclopts import App, Parameter

from .config import get_config

# Command group names
GRP_SYNC = "Sync"
GRP_FILES = "Files"
GRP_SETUP = "Setup"
GRP_QUICK = "Quick Access"
GRP_SUB = "Subcommands"
from .commands import (
    sync, secrets, bootstrap, pkg, platform, scripts, utils, git_cmds,
    templates, hooks, remote, update, validate, completions
)

# Main app
app = App(
    name="dotfiles",
    help="Personal dotfiles management CLI",
    version_flags=["--version", "-V"],
)

# Sub-apps for command groups
secrets_app = App(name="secrets", help="Manage encrypted secrets (git-crypt)")
pkg_app = App(name="pkg", help="Manage packages (wrapper for pkgmanager)")
files_app = App(name="files", help="File management commands")
mac_app = App(name="mac", help="macOS-specific commands")
win_app = App(name="win", help="Windows-specific commands")
util_app = App(name="util", help="Utility commands")
git_app = App(name="git", help="Git helper commands")
backup_app = App(name="backup", help="Backup and restore dotfiles")
remote_app = App(name="remote", help="Remote deployment via SSH")
hooks_app = App(name="hooks", help="Pre/post hooks management")
completion_app = App(name="completion", help="Shell completions")

app.command(secrets_app)
app.command(pkg_app)
app.command(files_app)
app.command(mac_app)
app.command(win_app)
app.command(util_app)
app.command(git_app)
app.command(backup_app)
app.command(remote_app)
app.command(hooks_app)
app.command(completion_app)


# =============================================================================
# Main commands
# =============================================================================


@app.command(group=GRP_SYNC)
def pull():
    """Pull latest changes and apply configs."""
    sync.pull()


@app.command(group=GRP_SYNC)
def push(
    message: Annotated[str, Parameter(name=["-m", "--message"])] = "minor fix",
):
    """Commit and push dotfiles changes."""
    sync.push(message)


@app.command(group=GRP_SYNC)
def apply(
    force: Annotated[bool, Parameter(name=["-f", "--force"])] = False,
    dry_run: Annotated[bool, Parameter(name=["-n", "--dry-run"])] = False,
):
    """Apply dotfiles to system (create symlinks/copies)."""
    sync.apply(force=force, dry_run=dry_run)


@app.command(group=GRP_SYNC)
def collect(
    dry_run: Annotated[bool, Parameter(name=["-n", "--dry-run"])] = False,
):
    """Collect changes from system back to repo (reverse of apply)."""
    sync.collect(dry_run=dry_run)


@app.command(group=GRP_SYNC)
def diff(
    full: Annotated[bool, Parameter(name=["--full"])] = False,
    file: Annotated[Optional[str], Parameter(name=["-f", "--file"])] = None,
):
    """Show pending changes (git status + file status)."""
    if full:
        sync.diff_full(file)
    else:
        sync.diff()


@app.command(group=GRP_SYNC)
def status():
    """Show overall dotfiles status."""
    sync.status()


@app.command(group=GRP_FILES)
def add(
    file: str,
    type: Annotated[str, Parameter(name=["-t", "--type"])] = "symlink",
    secret: Annotated[bool, Parameter(name=["-s", "--secret"])] = False,
    platform_name: Annotated[Optional[str], Parameter(name=["-p", "--platform"])] = None,
):
    """Add a file to dotfiles tracking."""
    sync.add(file, type=type, secret=secret, platform=platform_name)


@app.command(group=GRP_FILES)
def remove(file: str):
    """Remove a file from dotfiles tracking."""
    sync.remove(file)


@app.command(name="bootstrap", group=GRP_SETUP)
def bootstrap_cmd(
    stage: Annotated[Optional[str], Parameter(name=["-s", "--stage"])] = None,
):
    """Complete system setup after clone."""
    bootstrap.bootstrap(stage)


@app.command(group=GRP_SETUP)
def doctor():
    """Verify system health and configuration."""
    bootstrap.doctor()


@app.command(group=GRP_QUICK)
def cd():
    """Print dotfiles path (use: cd $(dotfiles cd))."""
    cfg = get_config()
    print(cfg.dotfiles_path)


@app.command(group=GRP_QUICK)
def edit():
    """Open dotfiles directory in editor."""
    import os
    from .utils.run import run

    cfg = get_config()
    editor = os.environ.get("EDITOR", "hx")
    run([editor, str(cfg.dotfiles_path)], check=False)


@app.command(group=GRP_QUICK)
def run_script(
    name: Optional[str] = None,
    list_all: Annotated[bool, Parameter(name=["-l", "--list"])] = False,
):
    """Run a script from scripts/ directory."""
    if list_all or not name:
        scripts.list_scripts()
    else:
        scripts.run_script(name)


publish_app = App(name="publish", help="Publish dotfiles (local or gist)")
app.command(publish_app)


@publish_app.command(name="local")
def publish_local(
    output: Annotated[Optional[str], Parameter(name=["-o", "--output"])] = None,
    exclude: Annotated[Optional[list[str]], Parameter(name=["-e", "--exclude"])] = None,
    no_push: Annotated[bool, Parameter(name=["--no-push"])] = False,
    message: Annotated[str, Parameter(name=["-m", "--message"])] = "update",
):
    """Sync to public/ and push to public repo."""
    sync.publish(output, exclude, push=not no_push, message=message)


@publish_app.command(name="gist")
def publish_gist(
    gist_id: Annotated[Optional[str], Parameter(name=["-g", "--gist-id"])] = None,
    repo: Annotated[Optional[str], Parameter(name=["-r", "--repo"])] = None,
):
    """Publish bootstrap script to GitHub gist."""
    sync.publish_gist(gist_id, repo)


# =============================================================================
# Secrets commands (git-crypt)
# =============================================================================


@secrets_app.command
def init():
    """Initialize git-crypt in the repo."""
    secrets.init()


@secrets_app.command
def unlock(
    key: Annotated[Optional[str], Parameter(name=["-k", "--key"])] = None,
):
    """Unlock secrets with git-crypt key."""
    secrets.unlock(key)


@secrets_app.command
def lock():
    """Lock secrets (re-encrypt locally)."""
    secrets.lock()


@secrets_app.command(name="status")
def secrets_status():
    """Show git-crypt status."""
    secrets.status()


@secrets_app.command(name="export-key")
def export_key(output: Optional[str] = None):
    """Export git-crypt key for backup."""
    secrets.export_key(output)


@secrets_app.command(name="add-pattern")
def add_pattern(pattern: str):
    """Add encryption pattern to .gitattributes."""
    secrets.add_pattern(pattern)


@secrets_app.command(name="list")
def secrets_list():
    """List all encrypted files."""
    secrets.list_encrypted()


# =============================================================================
# Package commands (pkgmanager wrapper)
# =============================================================================


@pkg_app.command(name="init")
def pkg_init(
    types: Annotated[Optional[str], Parameter(name=["-t", "--types"])] = None,
):
    """Install all packages from manifest."""
    pkg.init(types)


@pkg_app.command(name="install")
def pkg_install(type: str, name: str):
    """Install and track a package."""
    pkg.install(type, name)


@pkg_app.command(name="remove")
def pkg_remove(type: str, name: str):
    """Remove and untrack a package."""
    pkg.remove(type, name)


@pkg_app.command(name="update")
def pkg_update():
    """Update all packages."""
    pkg.update()


@pkg_app.command(name="list")
def pkg_list():
    """List installed packages."""
    pkg.list_packages()


@pkg_app.command(name="install-tool")
def pkg_install_tool():
    """Install pkgmanager itself."""
    pkg.install_tool()


# =============================================================================
# macOS commands
# =============================================================================


@mac_app.command
def backup():
    """Backup macOS app settings via Mackup."""
    platform.mac_backup()


@mac_app.command
def restore():
    """Restore macOS app settings via Mackup."""
    platform.mac_restore()


@mac_app.command
def brewfile():
    """Regenerate Brewfile from installed packages."""
    platform.mac_brewfile()


# =============================================================================
# Windows commands
# =============================================================================


@win_app.command(name="user")
def win_user():
    """Print Windows user profile path (WSL)."""
    platform.win_user()


@win_app.command(name="dist")
def win_dist():
    """Print running WSL distributions."""
    platform.win_dist()


@win_app.command(name="run")
def win_run(
    cmd: Annotated[list[str], Parameter(consume_multiple=True, allow_leading_hyphen=True)],
):
    """Run a Windows command via cmd.exe (/C)."""
    platform.win_run(cmd)


# =============================================================================
# Files commands
# =============================================================================


@files_app.command(name="list")
def files_list():
    """List all tracked files."""
    from .files.manifest import Manifest
    from .utils.console import console, create_table

    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    if not manifest.entries:
        console.print("No files in manifest")
        return

    table = create_table("Type", "Source", "Destination", "Platform")

    for entry in manifest.entries:
        plat = entry.platform or "all"
        table.add_row(entry.type, str(entry.source), f"~/{entry.dest}", plat)

    console.print(table)


@files_app.command(name="check")
def files_check():
    """Verify file status."""
    sync.diff()


# =============================================================================
# Utility commands
# =============================================================================


@util_app.command(name="ip")
def util_ip(
    all_info: Annotated[bool, Parameter(name=["-a", "--all"])] = False,
):
    """Get public IP address."""
    utils.get_ip(all_info)


@util_app.command
def serve(
    port: Annotated[int, Parameter(name=["-p", "--port"])] = 8080,
    bind: Annotated[Optional[str], Parameter(name=["-b", "--bind"])] = None,
):
    """Start HTTP server in current directory."""
    utils.serve(port, bind)


@util_app.command(name="ghostty")
def util_ghostty(host: str):
    """Setup ghostty terminfo on remote host."""
    utils.init_ghostty(host)


@util_app.command(name="ssh-init")
def util_ssh_init(
    host: str,
    user: Annotated[Optional[str], Parameter(name=["-u", "--user"])] = None,
    hostname: Annotated[Optional[str], Parameter(name=["-H", "--hostname"])] = None,
    port: Annotated[int, Parameter(name=["-p", "--port"])] = 22,
):
    """Initialize SSH key, copy to remote, and update config."""
    utils.ssh_init(host, user, hostname, port)


# =============================================================================
# Git helper commands
# =============================================================================


@git_app.command(name="init")
def git_init(
    name: str,
    public: Annotated[bool, Parameter(name=["-p", "--public"])] = False,
):
    """Initialize git repo and create GitHub repository."""
    git_cmds.init_hub(name, public)


@git_app.command
def quick(
    message: Annotated[str, Parameter(name=["-m", "--message"])] = "minor fix",
):
    """Quick commit and push all changes (any repo)."""
    git_cmds.quick(message)


# =============================================================================
# Backup commands
# =============================================================================


@backup_app.command(name="create")
def backup_create(
    name: Annotated[Optional[str], Parameter(name=["-n", "--name"])] = None,
):
    """Create a backup of current dotfiles state."""
    sync.backup(name)


@backup_app.command(name="restore")
def backup_restore(name: str):
    """Restore dotfiles from a backup."""
    sync.restore_backup(name)


@backup_app.command(name="list")
def backup_list():
    """List available backups."""
    sync.list_backups()


# =============================================================================
# Remote commands
# =============================================================================


@remote_app.command(name="deploy")
def remote_deploy(
    host: str,
    path: Annotated[str, Parameter(name=["-p", "--path"])] = "~/dotfiles",
    bootstrap_flag: Annotated[bool, Parameter(name=["-b", "--bootstrap"])] = False,
):
    """Deploy dotfiles to a remote host via SSH."""
    remote.deploy(host, path, bootstrap_flag)


@remote_app.command(name="sync-from")
def remote_sync_from(
    host: str,
    path: Annotated[str, Parameter(name=["-p", "--path"])] = "~/dotfiles",
):
    """Sync dotfiles from a remote host."""
    remote.sync_from(host, path)


# =============================================================================
# Hooks commands
# =============================================================================


@hooks_app.command(name="list")
def hooks_list():
    """List available hooks."""
    hooks.list_hooks()


@hooks_app.command(name="create")
def hooks_create(
    name: str,
    phase: Annotated[str, Parameter(name=["-p", "--phase"])] = "pre",
):
    """Create a new hook script."""
    hooks.create_hook(name, phase)


# =============================================================================
# Completion commands
# =============================================================================


@completion_app.command(name="generate")
def completion_generate(
    shell: Annotated[str, Parameter(name=["-s", "--shell"])] = "fish",
):
    """Generate shell completions."""
    completions.generate(shell)


@completion_app.command(name="install")
def completion_install(
    shell: Annotated[str, Parameter(name=["-s", "--shell"])] = "fish",
):
    """Install shell completions."""
    completions.install(shell)


# =============================================================================
# Additional main commands
# =============================================================================


@app.command(name="import", group=GRP_FILES)
def import_cmd(
    dry_run: Annotated[bool, Parameter(name=["-n", "--dry-run"])] = False,
):
    """Scan home directory for common dotfiles to track."""
    sync.import_dotfiles(dry_run)


@app.command(name="update", group=GRP_SETUP)
def update_cmd():
    """Update dotfiles-cli to latest version."""
    update.update_cli()


@app.command(name="validate", group=GRP_SETUP)
def validate_cmd():
    """Validate all configuration files."""
    validate.validate_all()


# =============================================================================
# Entry point
# =============================================================================


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
