"""Config validation for dotfiles."""

from pathlib import Path

import yaml

from ..config import get_config
from ..utils.console import success, error, warning, info, header, dim


def validate_all():
    """Validate all configuration files."""
    cfg = get_config()

    header("Validating configuration")

    all_ok = True

    # Validate files.yaml
    if not _validate_files_yaml(cfg):
        all_ok = False

    # Validate publish.yaml
    if not _validate_publish_yaml(cfg):
        all_ok = False

    # Validate packages.yaml
    if not _validate_packages_yaml(cfg):
        all_ok = False

    # Validate vars.yaml (for templates)
    if not _validate_vars_yaml(cfg):
        all_ok = False

    print()
    if all_ok:
        success("All configuration files valid")
    else:
        warning("Some configuration issues found")

    return all_ok


def _validate_files_yaml(cfg) -> bool:
    """Validate files.yaml manifest."""
    if not cfg.files_yaml.exists():
        dim("  files.yaml: not found (will be created on first add)")
        return True

    try:
        with open(cfg.files_yaml) as f:
            data = yaml.safe_load(f)

        if not data:
            warning("  files.yaml: empty")
            return True

        # Check structure
        if "entries" in data:
            entries = data["entries"]
            if not isinstance(entries, list):
                error("  files.yaml: 'entries' must be a list")
                return False

            for i, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    error(f"  files.yaml: entry {i} must be a dict")
                    return False
                if "source" not in entry:
                    error(f"  files.yaml: entry {i} missing 'source'")
                    return False
                if "dest" not in entry:
                    error(f"  files.yaml: entry {i} missing 'dest'")
                    return False

                # Check source exists
                source = cfg.dotfiles_path / entry["source"]
                if not source.exists():
                    warning(f"  files.yaml: source not found: {entry['source']}")

        success("  files.yaml: valid")
        return True

    except yaml.YAMLError as e:
        error(f"  files.yaml: invalid YAML - {e}")
        return False


def _validate_publish_yaml(cfg) -> bool:
    """Validate publish.yaml."""
    if not cfg.publish_yaml.exists():
        dim("  publish.yaml: not found (optional)")
        return True

    try:
        with open(cfg.publish_yaml) as f:
            data = yaml.safe_load(f)

        if not data:
            dim("  publish.yaml: empty")
            return True

        # Check public_repo is a valid URL
        if "public_repo" in data:
            repo = data["public_repo"]
            if not (repo.startswith("http") or repo.startswith("git@")):
                warning(f"  publish.yaml: public_repo looks invalid: {repo}")

        # Check exclude is a list
        if "exclude" in data and not isinstance(data["exclude"], list):
            error("  publish.yaml: 'exclude' must be a list")
            return False

        success("  publish.yaml: valid")
        return True

    except yaml.YAMLError as e:
        error(f"  publish.yaml: invalid YAML - {e}")
        return False


def _validate_packages_yaml(cfg) -> bool:
    """Validate packages.yaml."""
    if not cfg.packages_yaml.exists():
        dim("  packages.yaml: not found (optional)")
        return True

    try:
        with open(cfg.packages_yaml) as f:
            data = yaml.safe_load(f)

        if not data:
            dim("  packages.yaml: empty")
            return True

        success("  packages.yaml: valid")
        return True

    except yaml.YAMLError as e:
        error(f"  packages.yaml: invalid YAML - {e}")
        return False


def _validate_vars_yaml(cfg) -> bool:
    """Validate vars.yaml for templates."""
    vars_file = cfg.dotfiles_internal / "vars.yaml"

    if not vars_file.exists():
        dim("  vars.yaml: not found (optional)")
        return True

    try:
        with open(vars_file) as f:
            data = yaml.safe_load(f)

        if not data:
            dim("  vars.yaml: empty")
            return True

        # Check vars is a dict
        if "vars" in data and not isinstance(data["vars"], dict):
            error("  vars.yaml: 'vars' must be a dict")
            return False

        # Check profiles
        if "profiles" in data:
            if not isinstance(data["profiles"], dict):
                error("  vars.yaml: 'profiles' must be a dict")
                return False

        success("  vars.yaml: valid")
        return True

    except yaml.YAMLError as e:
        error(f"  vars.yaml: invalid YAML - {e}")
        return False
