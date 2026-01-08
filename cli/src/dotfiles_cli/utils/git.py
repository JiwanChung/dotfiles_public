"""Git operation utilities."""

from pathlib import Path
from typing import Optional

from .run import run, run_quiet


def git_status(repo: Path) -> str:
    """Get git status output."""
    result = run_quiet(["git", "status", "--porcelain"], cwd=repo)
    return result.stdout.strip()


def is_clean(repo: Path) -> bool:
    """Check if repo has no uncommitted changes."""
    return git_status(repo) == ""


def current_branch(repo: Path) -> str:
    """Get current branch name."""
    result = run_quiet(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo)
    return result.stdout.strip()


def pull(repo: Path, rebase: bool = True) -> bool:
    """Pull latest changes."""
    cmd = ["git", "pull"]
    if rebase:
        cmd.append("--rebase")

    result = run(cmd, cwd=repo, check=False)
    return result.returncode == 0


def push(repo: Path) -> bool:
    """Push changes to remote."""
    result = run(["git", "push"], cwd=repo, check=False)
    return result.returncode == 0


def add_all(repo: Path):
    """Stage all changes."""
    run(["git", "add", "."], cwd=repo)


def commit(repo: Path, message: str) -> bool:
    """Create a commit with message."""
    result = run(["git", "commit", "-m", message], cwd=repo, check=False)
    return result.returncode == 0


def diff_stat(repo: Path) -> str:
    """Get diff stat output."""
    result = run_quiet(["git", "diff", "--stat"], cwd=repo)
    return result.stdout.strip()


def is_ahead_of_remote(repo: Path) -> Optional[int]:
    """Check how many commits ahead of remote. Returns None if no remote."""
    result = run_quiet(
        ["git", "rev-list", "--count", "@{upstream}..HEAD"],
        cwd=repo
    )
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def is_behind_remote(repo: Path) -> Optional[int]:
    """Check how many commits behind remote. Returns None if no remote."""
    result = run_quiet(
        ["git", "rev-list", "--count", "HEAD..@{upstream}"],
        cwd=repo
    )
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None
