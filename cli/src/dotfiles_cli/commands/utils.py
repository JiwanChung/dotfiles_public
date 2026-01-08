"""Utility commands: get_ip, serve, init_ghostty."""

import shutil
from typing import Optional

from ..utils.console import success, error, info, header
from ..utils.run import run, run_quiet, has_command


def get_ip(all_info: bool = False):
    """Get public IP address.

    Args:
        all_info: Show all info (JSON) instead of just IP
    """
    if all_info:
        run(["curl", "-s", "https://ipinfo.io/json"], check=False)
    else:
        run(["curl", "-s", "https://ipinfo.io/ip"], check=False)
        print()  # Add newline after IP


def serve(port: int = 8080, bind: Optional[str] = None):
    """Start HTTP server in current directory.

    Args:
        port: Port to serve on (default: 8080)
        bind: Address to bind to (optional)
    """
    header(f"Serving on port {port}")

    if has_command("miniserve"):
        # Prefer miniserve if available
        args = ["miniserve", "-u", "-H", "--readme", "-p", str(port), "-W", "./"]
        if bind:
            args.extend(["-i", bind])
        run(args, check=False)
    elif has_command("python3") or has_command("python"):
        # Fall back to Python
        python = "python3" if has_command("python3") else "python"
        args = [python, "-m", "http.server", str(port)]
        if bind:
            args.extend(["-b", bind])
        run(args, check=False)
    else:
        error("No HTTP server available")
        info("Install miniserve or python")


def init_ghostty(host: str):
    """Setup ghostty terminfo on remote host.

    Args:
        host: SSH host to setup
    """
    if not has_command("infocmp"):
        error("infocmp not found")
        return False

    header(f"Setting up ghostty terminfo on {host}")

    # infocmp -x xterm-ghostty | ssh host -- tic -x -
    import subprocess

    try:
        infocmp = subprocess.Popen(
            ["infocmp", "-x", "xterm-ghostty"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        ssh = subprocess.Popen(
            ["ssh", host, "--", "tic", "-x", "-"],
            stdin=infocmp.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        infocmp.stdout.close()
        _, stderr = ssh.communicate()

        if ssh.returncode == 0:
            success(f"Ghostty terminfo installed on {host}")
            return True
        else:
            error(f"Failed: {stderr.decode()}")
            return False
    except Exception as e:
        error(f"Failed: {e}")
        return False


def ssh_init(host: str, user: Optional[str] = None, hostname: Optional[str] = None, port: int = 22):
    """Initialize SSH key, copy to remote, and update SSH config.

    Args:
        host: SSH host alias (used for key filename and config entry)
        user: Remote username (will prompt if not provided)
        hostname: Remote hostname/IP (defaults to host if not provided)
        port: SSH port (default: 22)
    """
    from pathlib import Path

    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)

    key_path = ssh_dir / host
    config_path = ssh_dir / "config"

    # Check if key already exists
    if key_path.exists():
        error(f"Key already exists: {key_path}")
        return False

    # Resolve hostname and user
    actual_hostname = hostname or host
    if not user:
        import subprocess
        result = subprocess.run(
            ["bash", "-c", f"read -p 'Username for {actual_hostname}: ' u && echo $u"],
            capture_output=True, text=True
        )
        user = result.stdout.strip()
        if not user:
            error("Username is required")
            return False

    header(f"Setting up SSH for {host}")

    # 1. Generate key
    info("Generating SSH key...")
    result = run_quiet(["ssh-keygen", "-N", "", "-t", "ed25519", "-f", str(key_path)])
    if result.returncode != 0:
        error("Failed to generate key")
        return False
    success(f"Key generated: {key_path}")

    # 2. Copy to remote
    info(f"Copying key to {user}@{actual_hostname}...")
    target = f"{user}@{actual_hostname}"
    if port != 22:
        result = run(["ssh-copy-id", "-i", str(key_path), "-p", str(port), target], check=False)
    else:
        result = run(["ssh-copy-id", "-i", str(key_path), target], check=False)

    if result.returncode != 0:
        error("Failed to copy key to remote")
        info("You may need to copy manually:")
        info(f"  ssh-copy-id -i {key_path} {target}")
        return False
    success("Key copied to remote")

    # 3. Update SSH config
    info("Updating SSH config...")
    config_entry = f"""
Host {host}
    HostName {actual_hostname}
    User {user}
    Port {port}
    IdentityFile {key_path}
"""

    # Check if host already in config
    if config_path.exists():
        existing = config_path.read_text()
        if f"Host {host}" in existing or f"Host {host}\n" in existing:
            error(f"Host '{host}' already exists in SSH config")
            info("Config entry not added, but key was created and copied")
            return True
        # Append to existing config
        with open(config_path, "a") as f:
            f.write(config_entry)
    else:
        # Create new config
        config_path.write_text(config_entry.lstrip())
        config_path.chmod(0o600)

    success(f"SSH config updated")

    # 4. Test connection
    info("Testing connection...")
    result = run_quiet(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", host, "echo ok"])
    if result.returncode == 0:
        success(f"SSH setup complete! Use: ssh {host}")
    else:
        info(f"Setup complete. Test with: ssh {host}")

    return True
