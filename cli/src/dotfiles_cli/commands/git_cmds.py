"""Git helper commands."""

from typing import Optional

from ..utils.console import success, error, info, header
from ..utils.run import run, run_quiet, has_command


def init_hub(name: str, public: bool = False):
    """Initialize git repo and create GitHub repository.

    Args:
        name: Repository name
        public: Create public repo (default: private)
    """
    if not has_command("gh"):
        error("GitHub CLI (gh) not installed")
        info("Install with: brew install gh")
        return False

    # Check if remote already exists
    result = run_quiet(["git", "remote", "show", "origin"])
    if result.returncode == 0:
        error("Remote 'origin' already exists")
        run(["git", "remote", "-v"], check=False)
        return False

    header(f"Creating {'public' if public else 'private'} repo: {name}")

    # Initialize git if needed
    result = run_quiet(["git", "rev-parse", "--is-inside-work-tree"])
    if result.returncode != 0:
        info("Initializing git...")
        run(["git", "init"], check=False)

    # Create GitHub repo
    visibility = "--public" if public else "--private"
    result = run_quiet(["gh", "repo", "create", name, visibility])
    if result.returncode != 0:
        error("Failed to create GitHub repo")
        return False

    # Get username from gh
    result = run_quiet(["gh", "api", "user", "-q", ".login"])
    if result.returncode == 0:
        username = result.stdout.strip()
    else:
        error("Failed to get GitHub username")
        return False

    # Add remote
    remote_url = f"https://github.com/{username}/{name}.git"
    run(["git", "remote", "add", "origin", remote_url], check=False)

    # Initial commit and push
    run(["git", "add", "."], check=False)

    result = run_quiet(["git", "status", "--porcelain"])
    if result.stdout.strip():
        run(["git", "commit", "-m", "init"], check=False)

    run(["git", "push", "--set-upstream", "origin", "main"], check=False)

    success(f"Repository created: {remote_url}")
    return True


def quick(message: str = "minor fix"):
    """Quick commit and push all changes.

    Args:
        message: Commit message (default: "minor fix")
    """
    # Check if in git repo
    result = run_quiet(["git", "rev-parse", "--is-inside-work-tree"])
    if result.returncode != 0:
        error("Not in a git repository")
        return False

    run(["git", "add", "."], check=False)

    # Check if there are changes
    result = run_quiet(["git", "status", "--porcelain"])
    if not result.stdout.strip():
        info("No changes to commit")
        return True

    run(["git", "commit", "-m", message], check=False)
    run(["git", "push"], check=False)

    success("Changes pushed")
    return True
