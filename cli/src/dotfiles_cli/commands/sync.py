"""Sync commands: pull, push, apply, diff, add, status, import, backup."""

from pathlib import Path
from typing import Optional
import shutil
import subprocess

from ..config import get_config
from ..files.manifest import Manifest
from ..files.linker import create_symlink, check_symlink
from ..files.copier import copy_file, check_copy
from ..utils.console import (
    success,
    error,
    warning,
    info,
    header,
    dim,
    create_table,
    console,
)
from ..utils import git


# Common dotfiles to look for when importing
COMMON_DOTFILES = [
    ".bashrc",
    ".bash_profile",
    ".zshrc",
    ".zprofile",
    ".profile",
    ".gitconfig",
    ".gitignore_global",
    ".vimrc",
    ".tmux.conf",
    ".inputrc",
    ".editorconfig",
    ".npmrc",
    ".yarnrc",
    ".gemrc",
    ".config/fish",
    ".config/nvim",
    ".config/helix",
    ".config/starship.toml",
    ".config/kitty",
    ".config/alacritty",
    ".config/wezterm",
    ".config/ghostty",
    ".config/tmux",
    ".config/yazi",
    ".config/zellij",
    ".config/atuin",
    ".config/bat",
    ".config/lazygit",
    ".config/gh",
    ".ssh/config",
]


def apply(force: bool = False, dry_run: bool = False):
    """Apply dotfiles to system (create symlinks/copies)."""
    from datetime import datetime

    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    if not manifest.entries:
        warning("No files in manifest. Add files with: dotfiles add <file>")
        return

    header("Applying files")
    entries = manifest.for_platform(cfg.platform)

    # Create backup directory if force mode
    backup_dir = None
    if force and not dry_run:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = cfg.dotfiles_path / "backups" / f"pre-apply-{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

    ok_count = 0
    skip_count = 0
    error_count = 0
    backup_count = 0

    for entry in entries:
        source_abs = cfg.dotfiles_path / entry.source
        dest_display = f"~/{entry.dest}"

        if not source_abs.exists():
            error(f"{dest_display} - source not found: {entry.source}")
            error_count += 1
            continue

        if dry_run:
            info(f"[dry-run] {entry.type} {entry.source} -> {dest_display}")
            continue

        if entry.type == "symlink":
            ok, status = create_symlink(
                source_abs, entry.dest, force=force, backup_dir=backup_dir
            )
        else:
            ok, status = copy_file(
                source_abs, entry.dest, force=force, backup_dir=backup_dir
            )

        if ok:
            if status == "ok":
                dim(f"  {dest_display} (already ok)")
            else:
                success(f"{dest_display}")
            ok_count += 1
        else:
            if status == "conflict" and not force:
                warning(f"{dest_display} - exists (use --force to overwrite)")
                skip_count += 1
            else:
                error(f"{dest_display} - failed: {status}")
                error_count += 1

    if not dry_run:
        print()
        if ok_count:
            success(f"{ok_count} files applied")
        if skip_count:
            warning(f"{skip_count} files skipped")
        if error_count:
            error(f"{error_count} errors")

        # Report backup location or clean up empty backup dir
        if backup_dir:
            if any(backup_dir.iterdir()):
                info(f"Backups saved to: {backup_dir}")
            else:
                backup_dir.rmdir()  # Remove empty backup dir


def collect(dry_run: bool = False):
    """Collect changes from system back to dotfiles repo (reverse of apply)."""
    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    if not manifest.entries:
        warning("No files in manifest")
        return

    header("Collecting files")
    entries = manifest.for_platform(cfg.platform)

    collected = 0
    skipped = 0

    for entry in entries:
        source_abs = cfg.dotfiles_path / entry.source
        dest_abs = Path.home() / entry.dest
        dest_display = f"~/{entry.dest}"

        if not dest_abs.exists():
            dim(f"  {dest_display} - not found, skipping")
            skipped += 1
            continue

        # Skip symlinks - they already point to repo
        if dest_abs.is_symlink():
            dim(f"  {dest_display} - symlink, skipping")
            skipped += 1
            continue

        # Check if different
        if source_abs.exists():
            if dest_abs.is_dir():
                # For directories, always collect (can't easily diff)
                pass
            else:
                if source_abs.read_bytes() == dest_abs.read_bytes():
                    dim(f"  {dest_display} - unchanged")
                    skipped += 1
                    continue

        if dry_run:
            info(f"[dry-run] would collect {dest_display}")
            collected += 1
            continue

        # Copy from home to repo
        try:
            source_abs.parent.mkdir(parents=True, exist_ok=True)
            if dest_abs.is_dir():
                if source_abs.exists():
                    shutil.rmtree(source_abs)
                shutil.copytree(dest_abs, source_abs)
            else:
                shutil.copy2(dest_abs, source_abs)
            success(f"{dest_display}")
            collected += 1
        except Exception as e:
            error(f"{dest_display} - {e}")

    print()
    if collected:
        success(f"{collected} files collected")
    if skipped:
        dim(f"{skipped} files skipped")


def pull():
    """Pull latest changes and apply."""
    cfg = get_config()

    header("Pulling changes")

    if not git.pull(cfg.dotfiles_path):
        error("git pull failed")
        return False

    success("Pulled latest changes")
    apply()
    return True


def push(message: str = "minor fix"):
    """Commit and push changes."""
    cfg = get_config()

    header("Pushing changes")

    # Check for changes
    if git.is_clean(cfg.dotfiles_path):
        info("No changes to commit")
        return True

    # Stage all changes
    git.add_all(cfg.dotfiles_path)

    # Show what we're committing
    dim(git.diff_stat(cfg.dotfiles_path))

    # Commit
    if not git.commit(cfg.dotfiles_path, message):
        error("git commit failed")
        return False

    # Push
    if not git.push(cfg.dotfiles_path):
        error("git push failed")
        return False

    success(f"Pushed: {message}")
    return True


def diff():
    """Show pending changes."""
    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    # Git status
    header("Git status")
    status = git.git_status(cfg.dotfiles_path)
    if status:
        for line in status.split("\n"):
            print(f"  {line}")
    else:
        dim("  Clean - no uncommitted changes")

    # File status
    header("File status")
    entries = manifest.for_platform(cfg.platform)

    if not entries:
        dim("  No files in manifest")
        return

    table = create_table("Status", "Type", "Destination")

    for entry in entries:
        source_abs = cfg.dotfiles_path / entry.source
        dest_display = f"~/{entry.dest}"

        if not source_abs.exists():
            table.add_row("[red]missing src[/red]", entry.type, dest_display)
            continue

        if entry.type == "symlink":
            status = check_symlink(source_abs, entry.dest)
        else:
            status = check_copy(source_abs, entry.dest)

        if status == "ok":
            table.add_row("[green]\u2713 ok[/green]", entry.type, dest_display)
        elif status == "missing":
            table.add_row("[yellow]missing[/yellow]", entry.type, dest_display)
        elif status == "conflict":
            table.add_row("[red]conflict[/red]", entry.type, dest_display)
        elif status == "changed":
            table.add_row("[yellow]changed[/yellow]", entry.type, dest_display)
        elif status == "wrong":
            table.add_row("[yellow]wrong link[/yellow]", entry.type, dest_display)
        else:
            table.add_row(f"[red]{status}[/red]", entry.type, dest_display)

    console.print(table)


def add(
    file: str,
    type: str = "symlink",
    secret: bool = False,
    platform: Optional[str] = None,
):
    """Add a file to dotfiles tracking.

    Args:
        file: Path to file (absolute or relative to home)
        type: "symlink" or "copy"
        secret: If True, place in secrets/ directory (encrypted by git-crypt)
        platform: Platform-specific ("darwin", "linux", or None for all)
    """
    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    # Resolve file path
    file_path = Path(file).expanduser().resolve()

    if not file_path.exists():
        error(f"File not found: {file}")
        return False

    # Determine destination (relative to home)
    try:
        dest = file_path.relative_to(Path.home())
    except ValueError:
        error(f"File must be under home directory: {file}")
        return False

    # Determine source location in repo
    if secret:
        # Place in secrets/ directory
        source = Path("secrets") / dest.name
    elif str(dest).startswith(".config/"):
        # Place in files/config/ directory
        source = Path("files/config") / Path(*dest.parts[1:])
    elif str(dest).startswith("."):
        # Hidden file in home, place in files/home/
        source = Path("files/home") / dest
    else:
        # Other files
        source = Path("files") / dest

    source_abs = cfg.dotfiles_path / source

    # Create parent directories
    source_abs.parent.mkdir(parents=True, exist_ok=True)

    # Move or copy file to repo
    if file_path.is_dir():
        if source_abs.exists():
            shutil.rmtree(source_abs)
        shutil.copytree(file_path, source_abs)
    else:
        shutil.copy2(file_path, source_abs)

    # Add to manifest
    manifest.add(source, dest, type, platform)

    # If symlink type, remove original and create symlink
    if type == "symlink":
        if file_path.is_dir():
            shutil.rmtree(file_path)
        else:
            file_path.unlink()
        file_path.symlink_to(source_abs)

    if secret:
        info(f"Added to secrets/ (will be encrypted by git-crypt)")

    success(f"Added: {source} -> ~/{dest}")
    return True


def status():
    """Show overall status."""
    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    header("Dotfiles Status")

    # Git info
    branch = git.current_branch(cfg.dotfiles_path)
    ahead = git.is_ahead_of_remote(cfg.dotfiles_path)
    behind = git.is_behind_remote(cfg.dotfiles_path)

    sync_status = ""
    if ahead and ahead > 0:
        sync_status += f" [yellow]{ahead} ahead[/yellow]"
    if behind and behind > 0:
        sync_status += f" [yellow]{behind} behind[/yellow]"
    if not sync_status:
        sync_status = " [green]up to date[/green]"

    console.print(f"  Branch: [bold]{branch}[/bold]{sync_status}")

    # File counts
    entries = manifest.for_platform(cfg.platform)
    symlinks = sum(1 for e in entries if e.type == "symlink")
    copies = sum(1 for e in entries if e.type == "copy")

    console.print(f"  Files: {symlinks} symlinks, {copies} copies")

    # Check for issues
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
        warning(f"  {issues} file(s) need attention - run 'dotfiles diff' for details")
    else:
        success("  All files in sync")


def remove(file: str):
    """Remove a file from dotfiles tracking.

    Args:
        file: Destination path (relative to home, e.g., .config/fish)
    """
    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    dest = Path(file)

    entry = manifest.find_by_dest(dest)
    if not entry:
        error(f"Not tracked: {file}")
        return False

    # Remove from manifest
    manifest.remove(dest)

    # Remove symlink if exists
    dest_abs = Path.home() / dest
    if dest_abs.is_symlink():
        dest_abs.unlink()
        info(f"Removed symlink: ~/{dest}")

    success(f"Removed from tracking: {file}")
    return True


# Default patterns to exclude when publishing
DEFAULT_EXCLUDE = [
    ".git",
    "public",
    "dot_ssh",
    "dot_gitconfig",
    "private_*",
    "secret*",
    "*.age",
    ".env",
    "*.key",
    ".dotfiles-key",
]


def _load_publish_config() -> dict:
    """Load publish configuration from publish.yaml."""
    import yaml

    cfg = get_config()

    if not cfg.publish_yaml.exists():
        return {}

    with open(cfg.publish_yaml) as f:
        return yaml.safe_load(f) or {}


def _save_publish_config(data: dict):
    """Save publish configuration to publish.yaml."""
    import yaml

    cfg = get_config()
    cfg.publish_yaml.parent.mkdir(parents=True, exist_ok=True)

    with open(cfg.publish_yaml, "w") as f:
        yaml.dump(data, f, default_flow_style=False)


def publish(
    output: Optional[str] = None,
    exclude: Optional[list[str]] = None,
    push: bool = True,
    message: str = "update",
):
    """Create sanitized public copy of dotfiles (without secrets).

    Args:
        output: Output directory (default: public/)
        exclude: Additional patterns to exclude
        push: Push to public repo after sync (default: True)
        message: Commit message for push
    """
    import subprocess

    cfg = get_config()
    publish_cfg = _load_publish_config()

    output_dir = Path(output) if output else cfg.dotfiles_path / "public"

    # Build exclude list
    excludes = DEFAULT_EXCLUDE.copy()
    # Add excludes from config
    if "exclude" in publish_cfg:
        excludes.extend(publish_cfg["exclude"])
    if exclude:
        excludes.extend(exclude)

    header("Publishing dotfiles")
    info(f"Output: {output_dir}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build rsync command
    rsync_args = ["rsync", "-av", "--delete"]
    for pattern in excludes:
        rsync_args.extend(["--exclude", pattern])
    rsync_args.extend([f"{cfg.dotfiles_path}/", str(output_dir)])

    # Run rsync
    result = subprocess.run(rsync_args, capture_output=True, text=True)

    if result.returncode != 0:
        error("rsync failed")
        if result.stderr:
            print(result.stderr)
        return False

    # Additional cleanup for any files that slipped through
    cleanup_patterns = [
        "**/secrets.fish",
        "**/.env",
        "**/private_*",
    ]

    for pattern in cleanup_patterns:
        for match in output_dir.glob(pattern):
            if match.is_file():
                match.unlink()
                dim(f"  Removed: {match.relative_to(output_dir)}")
            elif match.is_dir():
                shutil.rmtree(match)
                dim(f"  Removed: {match.relative_to(output_dir)}/")

    success(f"Synced to: {output_dir}")

    # Push to public repo if configured
    if push:
        public_repo = publish_cfg.get("public_repo")

        if not public_repo:
            info("No public repo configured. To enable auto-push:")
            info(f"  Add 'public_repo: <url>' to {cfg.publish_yaml}")
            return True

        # Initialize git if needed
        git_dir = output_dir / ".git"
        if not git_dir.exists():
            info("Initializing git repo...")
            subprocess.run(["git", "init"], cwd=output_dir, capture_output=True)
            subprocess.run(
                ["git", "remote", "add", "origin", public_repo],
                cwd=output_dir,
                capture_output=True,
            )

        # Check remote is correct
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=output_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip() != public_repo:
            info(f"Updating remote to: {public_repo}")
            subprocess.run(
                ["git", "remote", "set-url", "origin", public_repo],
                cwd=output_dir,
                capture_output=True,
            )

        # Commit and push
        info("Pushing to public repo...")
        subprocess.run(["git", "add", "."], cwd=output_dir, capture_output=True)

        # Check if there are changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=output_dir,
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            info("No changes to push")
            return True

        subprocess.run(
            ["git", "commit", "-m", message], cwd=output_dir, capture_output=True
        )

        result = subprocess.run(
            ["git", "push", "-u", "origin", "main", "--force"],
            cwd=output_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # Try master branch
            result = subprocess.run(
                ["git", "push", "-u", "origin", "master", "--force"],
                cwd=output_dir,
                capture_output=True,
                text=True,
            )

        if result.returncode == 0:
            success(f"Pushed to: {public_repo}")
        else:
            error("Push failed")
            if result.stderr:
                print(result.stderr)
            return False

    return True


def generate_bootstrap(repo: Optional[str] = None) -> str:
    """Generate bootstrap script content.

    Args:
        repo: Git repository URL (default: auto-detect from git remote)
    """
    cfg = get_config()

    if not repo:
        # Try to get repo URL from git remote
        import subprocess

        result = subprocess.run(
            ["git", "-C", str(cfg.dotfiles_path), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            repo = result.stdout.strip()
        else:
            repo = "git@github.com:USERNAME/dotfiles.git"

    # Read template from scripts/bootstrap.sh
    template_path = cfg.scripts_path / "bootstrap.sh"
    template = template_path.read_text()
    return template.format(repo=repo)


def publish_gist(
    gist_id: Optional[str] = None,
    repo: Optional[str] = None,
    filename: str = "bootstrap.sh",
):
    """Publish bootstrap script to GitHub gist.

    Args:
        gist_id: Existing gist ID to update (creates new if not provided)
        repo: Git repository URL for the bootstrap script
        filename: Filename in the gist (default: bootstrap.sh)
    """
    from ..utils.run import run_quiet, has_command

    if not has_command("gh"):
        error("GitHub CLI (gh) not installed")
        info("Install with: brew install gh")
        return False

    # Check gh auth
    result = run_quiet(["gh", "auth", "status"])
    if result.returncode != 0:
        error("Not authenticated with GitHub")
        info("Run: gh auth login")
        return False

    header("Publishing bootstrap gist")

    # Generate bootstrap script
    content = generate_bootstrap(repo)

    # Write to temp file with correct name
    import tempfile
    import os

    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, filename)
    with open(temp_path, "w") as f:
        f.write(content)

    try:
        if gist_id:
            # Update existing gist via API
            info(f"Updating gist: {gist_id}")
            import subprocess
            import json

            # Get existing files to delete old ones
            view_result = subprocess.run(
                ["gh", "api", f"/gists/{gist_id}", "-q", ".files | keys[]"],
                capture_output=True,
                text=True,
            )
            old_files = (
                view_result.stdout.strip().split("\n")
                if view_result.returncode == 0
                else []
            )

            # Build payload: add new file, delete old files
            files_payload = {filename: {"content": content}}
            for old_file in old_files:
                if old_file and old_file != filename:
                    files_payload[old_file] = None  # null deletes the file

            result = subprocess.run(
                ["gh", "api", "-X", "PATCH", f"/gists/{gist_id}", "--input", "-"],
                input=json.dumps({"files": files_payload}),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                error("Failed to update gist")
                if result.stderr:
                    print(result.stderr)
                return False
            gist_url = f"https://gist.github.com/{gist_id}"
        else:
            # Create new gist
            info("Creating new gist...")
            import subprocess

            result = subprocess.run(
                ["gh", "gist", "create", "--public", temp_path],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                error("Failed to create gist")
                if result.stderr:
                    print(result.stderr)
                return False
            gist_url = result.stdout.strip()
            # Extract gist ID from URL
            gist_id = gist_url.split("/")[-1]

        success(f"Gist published: {gist_url}")

        # Generate one-liner
        raw_url = f"https://gist.githubusercontent.com/{gist_id}/raw/{filename}"

        # Try to get actual raw URL
        result = run_quiet(["gh", "gist", "view", gist_id, "--raw", "-f", filename])
        if result.returncode == 0:
            info("One-liner for README:")
            print()
            # Get username
            user_result = run_quiet(["gh", "api", "user", "-q", ".login"])
            username = (
                user_result.stdout.strip()
                if user_result.returncode == 0
                else "USERNAME"
            )
            print(
                f"curl -fsSL https://gist.githubusercontent.com/{username}/{gist_id}/raw/{filename} | bash"
            )
            print()

        return True

    finally:
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)


def import_dotfiles(dry_run: bool = False):
    """Scan home directory for common dotfiles and offer to add them.

    Args:
        dry_run: Only show what would be imported
    """
    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    # Get already tracked destinations
    tracked = {str(e.dest) for e in manifest.entries}

    header("Scanning for dotfiles")

    found = []
    for dotfile in COMMON_DOTFILES:
        path = Path.home() / dotfile
        if path.exists() and dotfile not in tracked:
            # Check if it's a symlink pointing to our repo
            if path.is_symlink():
                target = path.resolve()
                if str(cfg.dotfiles_path) in str(target):
                    continue  # Already managed
            found.append(dotfile)

    if not found:
        info("No new dotfiles found to import")
        return

    table = create_table("File", "Type", "Size")
    for dotfile in found:
        path = Path.home() / dotfile
        ftype = "dir" if path.is_dir() else "file"
        if path.is_dir():
            size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        else:
            size = path.stat().st_size
        size_str = f"{size / 1024:.1f}K" if size > 1024 else f"{size}B"
        table.add_row(f"~/{dotfile}", ftype, size_str)

    console.print(table)
    print()

    if dry_run:
        info(f"Found {len(found)} dotfiles (dry-run, not importing)")
        return

    info(f"Found {len(found)} dotfiles")
    info("Use 'dotfiles add <file>' to add individually")
    info("Or 'dotfiles import --all' to add all (not implemented yet)")


def backup(name: Optional[str] = None):
    """Create backup of current dotfiles state.

    Args:
        name: Backup name (default: timestamp)
    """
    import datetime

    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    if not manifest.entries:
        warning("No files in manifest to backup")
        return False

    # Create backup directory
    backup_dir = cfg.dotfiles_internal / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate backup name
    if not name:
        name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_path = backup_dir / name
    if backup_path.exists():
        error(f"Backup already exists: {name}")
        return False

    backup_path.mkdir()

    header(f"Creating backup: {name}")

    count = 0
    for entry in manifest.for_platform(cfg.platform):
        dest_abs = Path.home() / entry.dest

        if not dest_abs.exists():
            continue

        # Create parent dirs in backup
        backup_file = backup_path / entry.dest
        backup_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file/dir
        if dest_abs.is_dir():
            shutil.copytree(dest_abs, backup_file, symlinks=True)
        else:
            shutil.copy2(dest_abs, backup_file)
        count += 1
        dim(f"  {entry.dest}")

    success(f"Backed up {count} files to: {backup_path}")
    return True


def restore_backup(name: str):
    """Restore dotfiles from a backup.

    Args:
        name: Backup name to restore
    """
    cfg = get_config()

    backup_dir = cfg.dotfiles_internal / "backups"
    backup_path = backup_dir / name

    if not backup_path.exists():
        error(f"Backup not found: {name}")
        # List available backups
        if backup_dir.exists():
            backups = sorted(backup_dir.iterdir())
            if backups:
                info("Available backups:")
                for b in backups:
                    print(f"  {b.name}")
        return False

    header(f"Restoring backup: {name}")

    count = 0
    for item in backup_path.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(backup_path)
            dest = Path.home() / rel_path

            # Remove existing (could be symlink)
            if dest.exists() or dest.is_symlink():
                if dest.is_dir() and not dest.is_symlink():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()

            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
            count += 1
            dim(f"  {rel_path}")

    success(f"Restored {count} files from backup")
    return True


def list_backups():
    """List available backups."""
    cfg = get_config()
    backup_dir = cfg.dotfiles_internal / "backups"

    if not backup_dir.exists():
        info("No backups found")
        return

    backups = sorted(backup_dir.iterdir(), reverse=True)
    if not backups:
        info("No backups found")
        return

    header("Available backups")
    table = create_table("Name", "Date", "Files")

    for b in backups:
        if b.is_dir():
            file_count = sum(1 for _ in b.rglob("*") if _.is_file())
            # Parse date from name if possible
            try:
                date = datetime.datetime.strptime(b.name, "%Y%m%d_%H%M%S")
                date_str = date.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                date_str = "-"
            table.add_row(b.name, date_str, str(file_count))

    console.print(table)


def diff_full(file: Optional[str] = None):
    """Show full file content diffs.

    Args:
        file: Specific file to diff (optional)
    """
    cfg = get_config()
    manifest = Manifest.load(cfg.files_yaml)

    entries = manifest.for_platform(cfg.platform)
    if file:
        entries = [e for e in entries if str(e.dest) == file or str(e.source) == file]

    if not entries:
        info("No files to diff")
        return

    has_diff = False
    for entry in entries:
        source_abs = cfg.dotfiles_path / entry.source
        dest_abs = Path.home() / entry.dest

        if not source_abs.exists():
            continue

        # For symlinks, check if pointing to right place
        if entry.type == "symlink":
            if dest_abs.is_symlink():
                if dest_abs.resolve() == source_abs.resolve():
                    continue  # OK
            elif not dest_abs.exists():
                header(f"~/{entry.dest} (missing)")
                info("File does not exist, will be created as symlink")
                has_diff = True
                continue

        # For copies or conflicts, show diff
        if dest_abs.exists() and dest_abs.is_file() and source_abs.is_file():
            result = subprocess.run(
                ["diff", "-u", str(dest_abs), str(source_abs)],
                capture_output=True,
                text=True,
            )
            if result.stdout:
                header(f"~/{entry.dest}")
                print(result.stdout)
                has_diff = True
        elif dest_abs.is_dir() and source_abs.is_dir():
            result = subprocess.run(
                ["diff", "-rq", str(dest_abs), str(source_abs)],
                capture_output=True,
                text=True,
            )
            if result.stdout:
                header(f"~/{entry.dest}/")
                print(result.stdout)
                has_diff = True

    if not has_diff:
        success("All files in sync")
