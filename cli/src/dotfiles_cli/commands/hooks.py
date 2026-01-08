"""Pre/post hooks for dotfiles operations."""

from pathlib import Path
from typing import Optional

from ..config import get_config
from ..utils.console import success, error, info, dim
from ..utils.run import run


def get_hooks_dir() -> Path:
    """Get hooks directory path."""
    cfg = get_config()
    return cfg.dotfiles_internal / "hooks"


def run_hook(name: str, phase: str = "pre") -> bool:
    """Run a hook script if it exists.

    Args:
        name: Hook name (e.g., "apply", "pull", "push")
        phase: "pre" or "post"

    Returns:
        True if hook ran successfully or doesn't exist
    """
    hooks_dir = get_hooks_dir()
    hook_name = f"{phase}-{name}"

    # Check for hook script
    for ext in ["", ".sh", ".fish", ".py"]:
        hook_path = hooks_dir / f"{hook_name}{ext}"
        if hook_path.exists() and hook_path.is_file():
            return _execute_hook(hook_path, hook_name)

    return True  # No hook found, that's OK


def _execute_hook(hook_path: Path, hook_name: str) -> bool:
    """Execute a hook script."""
    dim(f"  Running hook: {hook_name}")

    # Determine interpreter
    suffix = hook_path.suffix
    if suffix == ".fish":
        interpreter = ["fish"]
    elif suffix == ".py":
        interpreter = ["python3"]
    else:
        interpreter = ["bash"]

    result = run(interpreter + [str(hook_path)], check=False)

    if result.returncode != 0:
        error(f"Hook failed: {hook_name}")
        return False

    return True


def list_hooks():
    """List all available hooks."""
    hooks_dir = get_hooks_dir()

    if not hooks_dir.exists():
        info("No hooks directory found")
        info(f"Create hooks in: {hooks_dir}")
        return

    hooks = sorted(hooks_dir.glob("*"))
    hooks = [h for h in hooks if h.is_file() and not h.name.startswith(".")]

    if not hooks:
        info("No hooks found")
        info(f"Create hooks in: {hooks_dir}")
        info("Examples: pre-apply.sh, post-pull.sh, pre-push.fish")
        return

    info("Available hooks:")
    for hook in hooks:
        print(f"  {hook.name}")


def create_hook(name: str, phase: str = "pre"):
    """Create a new hook script.

    Args:
        name: Hook name (apply, pull, push, etc.)
        phase: pre or post
    """
    hooks_dir = get_hooks_dir()
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_path = hooks_dir / f"{phase}-{name}.sh"

    if hook_path.exists():
        error(f"Hook already exists: {hook_path}")
        return False

    template = f"""#!/usr/bin/env bash
# {phase}-{name} hook
# Runs {'before' if phase == 'pre' else 'after'} dotfiles {name}

set -e

echo "Running {phase}-{name} hook..."

# Add your commands here

"""
    hook_path.write_text(template)
    hook_path.chmod(0o755)

    success(f"Created hook: {hook_path}")
    return True
