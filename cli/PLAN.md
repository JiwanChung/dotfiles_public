# dotfiles-cli Implementation Plan

## Overview

A Python CLI for managing dotfiles across machines. Replaces chezmoi with a simpler built-in file manager. Works with a private GitHub repo and a public bootstrap gist.

**Key Design Decisions:**
- No chezmoi dependency - built-in symlink/copy manager
- git-crypt for transparent encryption (files auto-decrypt on clone)
- Manifest-based file tracking (`files.yaml`)
- Symlinks by default, copy for special cases

---

## Part 1: Public Bootstrap Gist

**Location:** GitHub Gist (public)
**URL:** `https://gist.githubusercontent.com/jiwanchung/<id>/raw/bootstrap.sh`

```bash
#!/bin/bash
set -euo pipefail

REPO="jiwanchung/dotfiles"
DOTFILES="$HOME/dotfiles"
KEY_URL="<your-secure-key-location>"  # See note below

echo "==> Dotfiles Bootstrap"

# 1. Install micromamba if not present
if ! command -v micromamba &>/dev/null; then
    echo "[1/6] Installing micromamba..."
    curl -sSfL https://micro.mamba.pm/install.sh | bash -s -- -b -y -p "$HOME/.local/micromamba"
    export PATH="$HOME/.local/micromamba/bin:$PATH"
else
    echo "[1/6] micromamba already installed"
fi

# Source micromamba
eval "$(micromamba shell hook -s bash)"

# 2. Install minimal tooling
echo "[2/6] Installing base packages..."
micromamba install -y -n base python uv gh git git-crypt

# 3. GitHub auth (required for private repo)
if ! gh auth status &>/dev/null 2>&1; then
    echo "[3/6] Authenticate with GitHub..."
    gh auth login --hostname github.com --git-protocol https
else
    echo "[3/6] Already authenticated with GitHub"
fi

# 4. Clone repo if not present
if [ ! -d "$DOTFILES/.git" ]; then
    echo "[4/6] Cloning dotfiles repo..."
    gh repo clone "$REPO" "$DOTFILES"
else
    echo "[4/6] Dotfiles repo already exists"
fi

# 5. Unlock git-crypt (decrypt secrets)
echo "[5/6] Unlocking secrets..."
if [ ! -f ~/.dotfiles-key ]; then
    echo "    Enter git-crypt key (base64), or paste path to key file:"
    read -r KEY_INPUT
    if [ -f "$KEY_INPUT" ]; then
        cp "$KEY_INPUT" ~/.dotfiles-key
    else
        echo "$KEY_INPUT" | base64 -d > ~/.dotfiles-key
    fi
fi
cd "$DOTFILES" && git-crypt unlock ~/.dotfiles-key

# 6. Install dotfiles-cli and run bootstrap
echo "[6/6] Installing dotfiles-cli..."
uv tool install "$DOTFILES/.dotfiles/dotfiles-cli" --force

echo ""
echo "==> Running: dotfiles bootstrap"
dotfiles bootstrap
```

**Note on key distribution:** The git-crypt key must be transferred securely to new machines. Options:
1. **Manual copy** - USB drive, secure file transfer (croc, magic-wormhole)
2. **Password manager** - Store base64-encoded key in Bitwarden/1Password
3. **Secure paste** - Prompt user to paste base64 key during bootstrap

---

## Part 2: File Management (Replaces Chezmoi)

### Manifest: `files.yaml`

```yaml
# File mapping manifest
# Supports: symlink (default), copy
# Encryption handled by git-crypt (transparent)

# Simple symlinks (most common)
symlinks:
  # source (relative to dotfiles/) -> destination (relative to $HOME)
  config/fish: .config/fish
  config/helix: .config/helix
  config/starship.toml: .config/starship.toml
  home/.gitconfig: .gitconfig

  # Secrets - just normal symlinks, git-crypt handles encryption in repo
  secrets/api_keys: .secrets/api_keys
  secrets/id_ed25519: .ssh/id_ed25519

# Files that must be copied (not symlinked)
copies:
  # Some apps don't follow symlinks, or need specific permissions
  secrets/ssh_config: .ssh/config  # SSH is picky about symlinks

# Platform-specific (only applied on matching OS)
platform:
  darwin:
    symlinks:
      config/karabiner: .config/karabiner
  linux:
    symlinks:
      config/i3: .config/i3
```

### git-crypt Setup

```bash
# .gitattributes - define what gets encrypted
secrets/** filter=git-crypt diff=git-crypt
*.secret filter=git-crypt diff=git-crypt
```

Files matching these patterns are:
- **Encrypted** when pushed to GitHub
- **Decrypted** automatically after `git-crypt unlock`
- **Normal files** locally - just symlink them like anything else

### File Operations

| Operation | Description |
|-----------|-------------|
| **symlink** | Create symlink: `$HOME/dest -> $DOTFILES/source` |
| **copy** | Copy file with permissions: `$DOTFILES/source -> $HOME/dest` |

### Directory Structure Changes

**Current (chezmoi style):**
```
dotfiles/
├── dot_config/
│   └── private_fish/
├── dot_gitconfig
└── .dotfiles/
```

**New (simpler):**
```
dotfiles/
├── config/              # Maps to ~/.config/
│   ├── fish/
│   ├── helix/
│   └── starship.toml
├── home/                # Maps to ~/
│   ├── .gitconfig
│   └── .ssh/
├── secrets/             # Encrypted files
│   └── api_keys.age
└── .dotfiles/
    ├── files.yaml       # File manifest
    ├── dotfiles-cli/
    └── ...
```

Or keep current structure - manifest is flexible.

---

## Part 3: Package Structure

```
.dotfiles/dotfiles-cli/
├── pyproject.toml
├── README.md
└── src/
    └── dotfiles_cli/
        ├── __init__.py
        ├── cli.py                 # Main entry point
        ├── config.py              # Configuration & paths
        ├── commands/
        │   ├── __init__.py
        │   ├── sync.py            # pull, push, apply, diff, add
        │   ├── bootstrap.py       # bootstrap, doctor
        │   ├── pkg.py             # pkg subcommands (wraps pkgmanager)
        │   ├── platform.py        # mac, linux subcommands
        │   ├── secrets.py         # git-crypt operations
        │   └── scripts.py         # run scripts
        ├── files/                 # File manager (replaces chezmoi)
        │   ├── __init__.py
        │   ├── manifest.py        # Load/parse/modify files.yaml
        │   ├── linker.py          # Symlink operations
        │   └── copier.py          # Copy operations
        └── utils/
            ├── __init__.py
            ├── run.py             # Shell command execution
            ├── git.py             # Git operations
            └── console.py         # Rich console output
```

Note: No `crypto.py` needed - git-crypt handles encryption transparently at the git level.

### pyproject.toml

```toml
[project]
name = "dotfiles-cli"
version = "0.1.0"
description = "Personal dotfiles management CLI"
requires-python = ">=3.9"
dependencies = [
    "cyclopts>=3.0",
    "PyYAML>=6",
    "rich>=13",
]

[project.scripts]
dotfiles = "dotfiles_cli.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/dotfiles_cli"]
```

---

## Part 4: Commands Specification

### 4.1 Sync Commands

#### `dotfiles apply [--force]`
```
Apply dotfiles to system.

Options:
  --force     Overwrite existing files without prompting
  --dry-run   Show what would be done

Steps:
1. Load files.yaml manifest
2. For each symlink entry:
   - Check if dest exists
   - If exists and not our symlink: prompt or skip (--force overwrites)
   - Create parent dirs if needed
   - Create symlink
3. For each copy entry:
   - Copy file (overwrite if --force)
4. For each encrypted entry:
   - Decrypt with AGE
   - Copy to destination
   - Set permissions (600 for keys)
5. Apply platform-specific entries if OS matches
```

#### `dotfiles pull`
```
Pull latest changes and apply.

Steps:
1. cd $DOTFILES && git pull --rebase
2. dotfiles apply
```

#### `dotfiles push [-m MESSAGE]`
```
Commit and push changes.

Options:
  -m, --message TEXT  Commit message [default: "minor fix"]

Steps:
1. cd $DOTFILES
2. git add .
3. git commit -m MESSAGE
4. git push
```

#### `dotfiles diff`
```
Show pending changes.

Output:
1. Git status (uncommitted changes)
2. File status:
   - [missing]  symlink not created
   - [modified] copy differs from source
   - [orphan]   dest exists but not in manifest
```

#### `dotfiles add FILE`
```
Add a file to dotfiles tracking.

Steps:
1. Determine relative path from $HOME
2. Copy/move file to appropriate location in repo
3. Add entry to files.yaml
4. Create symlink back
```

#### `dotfiles status`
```
Show overall status.

Output:
  - Git branch & sync status
  - Files: X symlinks, Y copies, Z encrypted
  - Missing/broken links
  - Package counts
```

---

### 4.2 Bootstrap Commands

#### `dotfiles bootstrap [--stage STAGE]`
```
Complete system setup.

Options:
  --stage TEXT  Run specific stage only

Stages:
  1. files     - Apply dotfiles (symlinks, copies, decrypt)
  2. rust      - Install Rust toolchain
  3. packages  - Run pkgmanager init
  4. platform  - Platform-specific setup
  5. shell     - Shell setup (fish plugins, etc.)

Stage 1 (files):
  - Ensure ~/.dotfiles_key.txt exists (prompt if not)
  - dotfiles apply --force

Stage 2 (rust):
  - bash scripts/install_rust.sh
  - source ~/.cargo/env

Stage 3 (packages):
  - pkgmanager init

Stage 4 (platform):
  - macOS: brew bundle, mackup restore
  - Linux: (placeholder)

Stage 5 (shell):
  - bash scripts/install_helix.sh
  - bash scripts/init_git_delta.sh
```

#### `dotfiles doctor`
```
Verify system health.

Checks:
  [ ] Git repo exists
  [ ] files.yaml valid
  [ ] All symlinks valid
  [ ] All copies in sync
  [ ] Encryption key present
  [ ] Required tools installed (git, age, fish...)
  [ ] GitHub auth valid
```

---

### 4.3 File Management Commands

#### `dotfiles files list`
```
List all tracked files.

Output:
TYPE       SOURCE                    DEST
symlink    config/fish               ~/.config/fish
symlink    config/helix              ~/.config/helix
copy       home/.ssh/config          ~/.ssh/config
encrypted  secrets/id_ed25519.age    ~/.ssh/id_ed25519
```

#### `dotfiles files check`
```
Verify file status.

Output:
STATUS     TYPE       DEST
✓ ok       symlink    ~/.config/fish
✓ ok       symlink    ~/.config/helix
✗ missing  symlink    ~/.config/starship.toml
✗ changed  copy       ~/.ssh/config
```

#### `dotfiles files link SOURCE DEST`
```
Add a new symlink entry.

Example:
  dotfiles files link config/nvim .config/nvim
```

#### `dotfiles files unlink DEST`
```
Remove a file from tracking.

Steps:
1. Remove symlink/copy from system
2. Remove entry from files.yaml
```

---

### 4.4 Secrets Commands

#### `dotfiles secrets init`
```
Initialize git-crypt in the repo.

Steps:
1. git-crypt init
2. Export key: git-crypt export-key ~/.dotfiles-key
3. Create .gitattributes with default patterns
4. Print instructions for key backup
```

#### `dotfiles secrets unlock`
```
Unlock secrets on a new machine.

Options:
  --key PATH   Path to key file (default: ~/.dotfiles-key)

Steps:
1. git-crypt unlock <key-file>
```

#### `dotfiles secrets lock`
```
Lock secrets (re-encrypt locally).

Steps:
1. git-crypt lock
```

#### `dotfiles secrets status`
```
Show git-crypt status.

Output:
- Locked/unlocked state
- List of encrypted file patterns from .gitattributes
- Count of encrypted files
```

#### `dotfiles secrets add-pattern PATTERN`
```
Add a pattern to .gitattributes for encryption.

Example:
  dotfiles secrets add-pattern "*.secret"
  dotfiles secrets add-pattern "private/**"

Steps:
1. Add line to .gitattributes: PATTERN filter=git-crypt diff=git-crypt
```

#### `dotfiles secrets export-key [PATH]`
```
Export the git-crypt key for backup.

Options:
  PATH   Output path (default: prints base64 to stdout)

Usage:
  dotfiles secrets export-key > key.b64           # For password manager
  dotfiles secrets export-key ~/.dotfiles-key    # For file backup
```

---

### 4.5 Package Commands (wraps pkgmanager)

#### `dotfiles pkg init`
```
Install all packages.
Wraps: pkgmanager init
```

#### `dotfiles pkg install TYPE NAME`
```
Install and track package.
Wraps: pkgmanager install TYPE NAME
```

#### `dotfiles pkg remove TYPE NAME`
```
Remove and untrack package.
Wraps: pkgmanager remove TYPE NAME
```

#### `dotfiles pkg update`
```
Update all packages.
Wraps: pkgmanager update
```

#### `dotfiles pkg list`
```
List packages.
Wraps: pkgmanager list
```

---

### 4.6 Platform Commands

#### `dotfiles platform setup`
```
Run platform-specific setup.

macOS:
  1. Install Homebrew if missing
  2. brew bundle --file=mac/Brewfile
  3. mackup restore

Linux:
  1. (placeholder)
```

#### `dotfiles platform update`
```
Update platform packages.

macOS:
  1. brew update && brew upgrade && brew cleanup
```

#### `dotfiles mac backup`
```
Backup app settings via Mackup.
```

#### `dotfiles mac restore`
```
Restore app settings via Mackup.
```

#### `dotfiles mac brewfile`
```
Regenerate Brewfile from installed.
```

---

### 4.7 Utility Commands

#### `dotfiles cd`
```
Print $DOTFILES path.
Usage: cd $(dotfiles cd)
```

#### `dotfiles edit`
```
Open dotfiles in editor.
```

#### `dotfiles run SCRIPT`
```
Run script from scripts/ directory.
```

#### `dotfiles run --list`
```
List available scripts.
```

---

## Part 5: Implementation Details

### files/manifest.py

```python
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import yaml

@dataclass
class FileEntry:
    source: Path      # Relative to dotfiles repo
    dest: Path        # Relative to $HOME
    type: str         # symlink or copy
    platform: Optional[str] = None  # darwin, linux, or None for all

@dataclass
class Manifest:
    entries: list[FileEntry]
    path: Path  # Path to manifest file (for saving)

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        with open(path) as f:
            data = yaml.safe_load(f) or {}

        entries = []

        # Parse symlinks
        for src, dest in data.get("symlinks", {}).items():
            entries.append(FileEntry(Path(src), Path(dest), "symlink"))

        # Parse copies
        for src, dest in data.get("copies", {}).items():
            entries.append(FileEntry(Path(src), Path(dest), "copy"))

        # Parse platform-specific
        for platform, sections in data.get("platform", {}).items():
            for src, dest in sections.get("symlinks", {}).items():
                entries.append(FileEntry(Path(src), Path(dest), "symlink", platform))
            for src, dest in sections.get("copies", {}).items():
                entries.append(FileEntry(Path(src), Path(dest), "copy", platform))

        return cls(entries, path)

    def save(self):
        """Save manifest back to YAML."""
        data = {"symlinks": {}, "copies": {}, "platform": {}}

        for entry in self.entries:
            section = "symlinks" if entry.type == "symlink" else "copies"
            if entry.platform:
                if entry.platform not in data["platform"]:
                    data["platform"][entry.platform] = {"symlinks": {}, "copies": {}}
                data["platform"][entry.platform][section][str(entry.source)] = str(entry.dest)
            else:
                data[section][str(entry.source)] = str(entry.dest)

        # Clean empty sections
        if not data["copies"]:
            del data["copies"]
        if not data["platform"]:
            del data["platform"]

        with open(self.path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def add(self, source: Path, dest: Path, type: str = "symlink", platform: str = None):
        """Add a new entry to the manifest."""
        self.entries.append(FileEntry(source, dest, type, platform))
        self.save()

    def remove(self, dest: Path) -> bool:
        """Remove an entry by destination path."""
        for i, entry in enumerate(self.entries):
            if entry.dest == dest:
                self.entries.pop(i)
                self.save()
                return True
        return False

    def for_platform(self, platform: str) -> list[FileEntry]:
        """Filter entries for current platform."""
        return [e for e in self.entries if e.platform is None or e.platform == platform]
```

### files/linker.py

```python
from pathlib import Path
import os
import shutil

def create_symlink(source: Path, dest: Path, force: bool = False) -> bool:
    """Create a symlink from dest -> source."""
    dest = Path.home() / dest
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() or dest.is_symlink():
        if dest.is_symlink() and dest.resolve() == source.resolve():
            return True  # Already correct
        if not force:
            return False  # Would overwrite, need confirmation
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()

    dest.symlink_to(source)
    return True

def remove_symlink(dest: Path) -> bool:
    """Remove a symlink."""
    dest = Path.home() / dest
    if dest.is_symlink():
        dest.unlink()
        return True
    return False

def check_symlink(source: Path, dest: Path) -> str:
    """Check symlink status: ok, missing, wrong, conflict."""
    dest = Path.home() / dest

    if not dest.exists() and not dest.is_symlink():
        return "missing"
    if not dest.is_symlink():
        return "conflict"  # Regular file exists
    if dest.resolve() != source.resolve():
        return "wrong"  # Points elsewhere
    return "ok"
```

### files/copier.py

```python
from pathlib import Path
import shutil
import filecmp
import os

def copy_file(source: Path, dest: Path, force: bool = False) -> bool:
    """Copy a file from source to dest."""
    dest = Path.home() / dest
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        if filecmp.cmp(source, dest, shallow=False):
            return True  # Already identical
        if not force:
            return False  # Would overwrite

    shutil.copy2(source, dest)

    # Set restrictive permissions for sensitive files
    if "ssh" in str(dest) or "secret" in str(dest).lower():
        os.chmod(dest, 0o600)

    return True

def check_copy(source: Path, dest: Path) -> str:
    """Check copy status: ok, missing, changed."""
    dest = Path.home() / dest

    if not dest.exists():
        return "missing"
    if not filecmp.cmp(source, dest, shallow=False):
        return "changed"
    return "ok"
```

### commands/secrets.py (git-crypt operations)

```python
import subprocess
from pathlib import Path
import base64

def is_unlocked(repo_path: Path) -> bool:
    """Check if git-crypt is unlocked."""
    result = subprocess.run(
        ["git-crypt", "status"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return "encrypted:" not in result.stdout.lower()

def unlock(repo_path: Path, key_path: Path) -> bool:
    """Unlock git-crypt with key."""
    result = subprocess.run(
        ["git-crypt", "unlock", str(key_path)],
        cwd=repo_path
    )
    return result.returncode == 0

def lock(repo_path: Path) -> bool:
    """Lock git-crypt (re-encrypt files)."""
    result = subprocess.run(
        ["git-crypt", "lock"],
        cwd=repo_path
    )
    return result.returncode == 0

def init(repo_path: Path, key_output: Path) -> bool:
    """Initialize git-crypt and export key."""
    subprocess.run(["git-crypt", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git-crypt", "export-key", str(key_output)],
        cwd=repo_path,
        check=True
    )
    return True

def export_key_base64(repo_path: Path) -> str:
    """Export key as base64 string (for password manager storage)."""
    result = subprocess.run(
        ["git-crypt", "export-key", "/dev/stdout"],
        cwd=repo_path,
        capture_output=True
    )
    return base64.b64encode(result.stdout).decode()
```

---

## Part 6: Migration Plan

### Step 1: Initialize git-crypt

```bash
cd ~/dotfiles
git-crypt init
git-crypt export-key ~/.dotfiles-key

# Create .gitattributes
echo "secrets/** filter=git-crypt diff=git-crypt" >> .gitattributes
git add .gitattributes
git commit -m "setup git-crypt"
```

### Step 2: Create files.yaml from current chezmoi setup

Map current `dot_*` files to new manifest:

```yaml
symlinks:
  config/fish: .config/fish
  config/helix: .config/helix
  home/.gitconfig: .gitconfig
  secrets/id_ed25519: .ssh/id_ed25519  # git-crypt encrypted
```

### Step 3: Reorganize directory structure (optional)

```bash
# Rename dot_ prefixed dirs to cleaner names
mv dot_config config
mv dot_gitconfig home/.gitconfig

# Move sensitive files to secrets/
mkdir secrets
mv encrypted_files/* secrets/
```

### Step 4: Files to Remove

| File | Replaced By |
|------|-------------|
| `bootstrap.sh` | Public gist |
| `chezmoi.toml` | `files.yaml` + git-crypt |
| `dot_config/private_fish/functions/dotfiles.fish` | `dotfiles` CLI |
| `mac/update.sh` | `dotfiles platform update` |
| `.age` encrypted files | Plain files in `secrets/` (git-crypt handles encryption) |

### Step 5: Update packages.yaml

```yaml
conda:
  # - chezmoi  # REMOVE
  # - age      # REMOVE (unless used elsewhere)
  - git-crypt  # ADD (or install via brew on mac)
```

### Step 6: Backup git-crypt key

```bash
# Option 1: Store in password manager (Bitwarden)
dotfiles secrets export-key | pbcopy  # Copy base64 to clipboard
# Paste into Bitwarden secure note

# Option 2: Store on USB drive
dotfiles secrets export-key /Volumes/USB/.dotfiles-key

# Option 3: Print and store physically
dotfiles secrets export-key | qrencode -t UTF8  # QR code
```

### Step 7: Update README

Document new workflow:
```bash
# New machine setup
curl -sSL https://gist.githubusercontent.com/jiwanchung/.../bootstrap.sh | bash
# When prompted, paste your git-crypt key from password manager

# Daily usage
dotfiles pull          # Get latest
dotfiles push -m "..."  # Save changes
dotfiles status        # Check state
```

---

## Part 7: Comparison

| Feature | Chezmoi | dotfiles-cli |
|---------|---------|--------------|
| Symlinks | Via template | Native |
| Copy files | Yes | Yes |
| Encryption | AGE (built-in) | git-crypt (transparent) |
| Templates | Go templates | No (not needed) |
| Per-machine config | `.chezmoi.toml.tmpl` | Platform sections in `files.yaml` |
| State tracking | SQLite DB | Git + manifest |
| Complexity | High | Low |
| Dependencies | chezmoi binary | Python + git-crypt |
| Encrypted file workflow | Manual decrypt on apply | Automatic on git clone |

---

## Part 8: Example Session

```bash
# New machine
$ curl -sSL https://gist.github.com/.../bootstrap.sh | bash
==> Installing micromamba...
==> Installing base packages...
==> Authenticate with GitHub...
==> Cloning dotfiles...
==> Unlocking secrets...
    Enter git-crypt key (base64), or paste path to key file:
    <paste from password manager>
==> Installing dotfiles-cli...
==> Running: dotfiles bootstrap

[1/5] Applying files...
  ✓ symlink config/fish -> ~/.config/fish
  ✓ symlink config/helix -> ~/.config/helix
  ✓ symlink secrets/id_ed25519 -> ~/.ssh/id_ed25519
[2/5] Installing Rust...
[3/5] Installing packages...
[4/5] Platform setup (darwin)...
[5/5] Shell setup...

✓ Bootstrap complete!

# Daily use
$ dotfiles status
Branch: main (up to date)
Files: 12 symlinks, 2 copies
Secrets: unlocked ✓
All files in sync ✓

$ dotfiles add ~/.config/new-app/config.yaml
Added: config/new-app/config.yaml -> ~/.config/new-app/config.yaml

$ dotfiles push -m "add new-app config"
[main abc123] add new-app config
 2 files changed
✓ Pushed to origin/main

# Adding a secret
$ dotfiles add ~/.ssh/new_key --secret
Moving to secrets/new_key (will be encrypted by git-crypt)
Added: secrets/new_key -> ~/.ssh/new_key

$ dotfiles push -m "add new ssh key"
✓ Pushed (secrets/new_key encrypted on remote)
```

---

## Summary

| Component | Purpose |
|-----------|---------|
| **Public gist** | Bootstrap on new machines |
| **dotfiles-cli** | Main CLI, file manager, orchestration |
| **files.yaml** | Manifest of tracked files |
| **git-crypt** | Transparent encryption for secrets |
| **pkgmanager** | Package management (existing) |

**Lines of code estimate:** ~700-900 (simpler without manual crypto)

**Dependencies removed:** chezmoi, age
**Dependencies added:** git-crypt

**Key benefit of git-crypt:** Files in `secrets/` are just normal files locally. No manual encrypt/decrypt step. Git handles it transparently on push/pull.
