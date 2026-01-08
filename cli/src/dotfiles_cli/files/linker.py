"""Symlink operations."""

from pathlib import Path
from typing import Optional
import shutil


def _backup_existing(dest_abs: Path, backup_dir: Optional[Path]) -> bool:
    """Backup existing file/dir before overwriting.

    Returns True if backup was created.
    """
    if backup_dir is None:
        return False

    if not (dest_abs.exists() or dest_abs.is_symlink()):
        return False

    # Create backup path preserving structure relative to home
    try:
        rel_path = dest_abs.relative_to(Path.home())
    except ValueError:
        rel_path = dest_abs.name

    backup_path = backup_dir / rel_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    # Copy the file/dir to backup
    if dest_abs.is_symlink():
        # For symlinks, just record the target
        target = dest_abs.resolve() if dest_abs.exists() else "broken"
        backup_path.with_suffix(".symlink").write_text(str(target))
    elif dest_abs.is_dir():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(dest_abs, backup_path)
    else:
        shutil.copy2(dest_abs, backup_path)

    return True


def create_symlink(source: Path, dest: Path, force: bool = False, backup_dir: Optional[Path] = None) -> tuple[bool, str]:
    """Create a symlink from dest -> source.

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

    if dest_abs.exists() or dest_abs.is_symlink():
        if dest_abs.is_symlink():
            try:
                if dest_abs.resolve() == source.resolve():
                    return True, "ok"  # Already correct
            except OSError:
                pass  # Broken symlink

        if not force:
            return False, "conflict"  # Would overwrite

        # Backup before removing
        _backup_existing(dest_abs, backup_dir)

        # Remove existing
        if dest_abs.is_dir() and not dest_abs.is_symlink():
            shutil.rmtree(dest_abs)
        else:
            dest_abs.unlink()

    dest_abs.symlink_to(source)
    return True, "created"


def remove_symlink(dest: Path) -> bool:
    """Remove a symlink.

    Args:
        dest: Destination path (relative to $HOME)

    Returns:
        True if removed, False if not a symlink
    """
    dest_abs = Path.home() / dest

    if dest_abs.is_symlink():
        dest_abs.unlink()
        return True
    return False


def check_symlink(source: Path, dest: Path) -> str:
    """Check symlink status.

    Args:
        source: Source path (absolute, in dotfiles repo)
        dest: Destination path (relative to $HOME)

    Returns:
        Status string: "ok", "missing", "wrong", "conflict", "broken"
    """
    dest_abs = Path.home() / dest

    if not dest_abs.exists() and not dest_abs.is_symlink():
        return "missing"

    if not dest_abs.is_symlink():
        return "conflict"  # Regular file/dir exists

    # It's a symlink, check if it points to the right place
    try:
        if dest_abs.resolve() == source.resolve():
            return "ok"
        else:
            return "wrong"  # Points elsewhere
    except OSError:
        return "broken"  # Broken symlink
