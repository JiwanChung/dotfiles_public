"""File copy operations."""

from pathlib import Path
from typing import Optional
import shutil
import filecmp
import os


def _backup_existing(dest_abs: Path, backup_dir: Optional[Path]) -> bool:
    """Backup existing file/dir before overwriting.

    Returns True if backup was created.
    """
    if backup_dir is None:
        return False

    if not dest_abs.exists():
        return False

    # Create backup path preserving structure relative to home
    try:
        rel_path = dest_abs.relative_to(Path.home())
    except ValueError:
        rel_path = dest_abs.name

    backup_path = backup_dir / rel_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy the file/dir to backup
    if dest_abs.is_dir():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(dest_abs, backup_path)
    else:
        shutil.copy2(dest_abs, backup_path)

    return True


def copy_file(source: Path, dest: Path, force: bool = False, backup_dir: Optional[Path] = None) -> tuple[bool, str]:
    """Copy a file from source to dest.

    Args:
        source: Source path (absolute, in dotfiles repo)
        dest: Destination path (relative to $HOME)
        force: Overwrite existing files
        backup_dir: Directory to backup existing files before overwriting

    Returns:
        Tuple of (success, status_message)
    """
    dest_abs = Path.home() / dest
    dest_abs.parent.mkdir(parents=True, exist_ok=True)

    if dest_abs.exists():
        # Check if already identical
        if dest_abs.is_file() and source.is_file():
            if filecmp.cmp(source, dest_abs, shallow=False):
                return True, "ok"  # Already identical

        if not force:
            return False, "conflict"  # Would overwrite

        # Backup before overwriting
        _backup_existing(dest_abs, backup_dir)

    # Copy the file (or directory)
    if source.is_dir():
        if dest_abs.exists():
            shutil.rmtree(dest_abs)
        shutil.copytree(source, dest_abs)
    else:
        shutil.copy2(source, dest_abs)

    # Set restrictive permissions for sensitive files
    if _is_sensitive(dest):
        os.chmod(dest_abs, 0o600)

    return True, "copied"


def check_copy(source: Path, dest: Path) -> str:
    """Check copy status.

    Args:
        source: Source path (absolute, in dotfiles repo)
        dest: Destination path (relative to $HOME)

    Returns:
        Status string: "ok", "missing", "changed"
    """
    dest_abs = Path.home() / dest

    if not dest_abs.exists():
        return "missing"

    if source.is_file() and dest_abs.is_file():
        if filecmp.cmp(source, dest_abs, shallow=False):
            return "ok"
        return "changed"

    if source.is_dir() and dest_abs.is_dir():
        # For directories, do a shallow check
        cmp = filecmp.dircmp(source, dest_abs)
        if not cmp.diff_files and not cmp.left_only and not cmp.right_only:
            return "ok"
        return "changed"

    return "changed"


def _is_sensitive(path: Path) -> bool:
    """Check if a path is likely sensitive (SSH keys, secrets, etc.)."""
    path_str = str(path).lower()
    sensitive_patterns = ["ssh", "secret", "key", "credential", "token", "password"]
    return any(p in path_str for p in sensitive_patterns)
