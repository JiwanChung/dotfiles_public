"""Template support for dotfiles with variable substitution."""

import os
import re
import socket
from pathlib import Path
from typing import Optional

from ..config import get_config
from ..utils.console import success, error, warning, info, header, dim


def get_template_vars() -> dict:
    """Get default template variables."""
    cfg = get_config()

    return {
        "hostname": socket.gethostname(),
        "user": os.environ.get("USER", ""),
        "home": str(Path.home()),
        "dotfiles": str(cfg.dotfiles_path),
        "platform": cfg.platform,
        "shell": os.environ.get("SHELL", "/bin/bash"),
        "editor": os.environ.get("EDITOR", "vim"),
    }


def load_custom_vars() -> dict:
    """Load custom variables from .dotfiles/vars.yaml."""
    import yaml

    cfg = get_config()
    vars_file = cfg.dotfiles_internal / "vars.yaml"

    if not vars_file.exists():
        return {}

    with open(vars_file) as f:
        data = yaml.safe_load(f) or {}

    # Support profile-specific vars
    profile = os.environ.get("DOTFILES_PROFILE", "default")
    if "profiles" in data and profile in data["profiles"]:
        vars_dict = data.get("vars", {}).copy()
        vars_dict.update(data["profiles"][profile])
        return vars_dict

    return data.get("vars", {})


def render_template(content: str, vars_dict: Optional[dict] = None) -> str:
    """Render template with variable substitution.

    Supports:
    - {{variable}} - simple substitution
    - {{variable|default}} - with default value
    - {{ENV:VAR}} - environment variable
    """
    if vars_dict is None:
        vars_dict = {}

    # Merge default vars with custom vars
    all_vars = get_template_vars()
    all_vars.update(load_custom_vars())
    all_vars.update(vars_dict)

    def replace_var(match):
        expr = match.group(1).strip()

        # Environment variable
        if expr.startswith("ENV:"):
            env_var = expr[4:]
            return os.environ.get(env_var, "")

        # Variable with default
        if "|" in expr:
            var_name, default = expr.split("|", 1)
            return all_vars.get(var_name.strip(), default.strip())

        # Simple variable
        return all_vars.get(expr, match.group(0))

    return re.sub(r"\{\{(.+?)\}\}", replace_var, content)


def render_file(source: Path, dest: Path, vars_dict: Optional[dict] = None) -> bool:
    """Render a template file to destination.

    Args:
        source: Source template file
        dest: Destination file path
        vars_dict: Additional variables
    """
    if not source.exists():
        error(f"Template not found: {source}")
        return False

    content = source.read_text()
    rendered = render_template(content, vars_dict)

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered)

    return True


def list_vars():
    """List all available template variables."""
    header("Template Variables")

    # Default vars
    info("Built-in:")
    for key, value in get_template_vars().items():
        dim(f"  {key}: {value}")

    # Custom vars
    custom = load_custom_vars()
    if custom:
        print()
        info("Custom (from vars.yaml):")
        for key, value in custom.items():
            dim(f"  {key}: {value}")

    print()
    info("Usage in files: {{variable}} or {{variable|default}}")
    info("Environment vars: {{ENV:VAR_NAME}}")
