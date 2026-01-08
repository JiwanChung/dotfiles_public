# Dotfiles

Personal dotfiles managed by `dotfiles-cli`.

## Quick Setup (New Machine)

```bash
curl -fsSL https://gist.githubusercontent.com/JiwanChung/9c8e97f8ad5000f2ad4ef3f5ed123795/raw/bootstrap.sh | bash
```

## Manual Setup

```bash
# Clone
git clone git@github.com:JiwanChung/dotfiles.git ~/dotfiles
cd ~/dotfiles

# Install CLI
uv tool install cli

# Unlock secrets (if encrypted)
dotfiles secrets unlock -k ~/.dotfiles-key

# Bootstrap
dotfiles bootstrap
```

## Environment

```bash
# fish (add to config.fish)
set -gx DOTFILES ~/dotfiles

# bash/zsh
export DOTFILES=~/dotfiles
```

## Commands

### Core

```bash
dotfiles status              # Show overall status
dotfiles diff                # Show pending changes
dotfiles diff --full         # Show file content diffs
dotfiles diff --full -f FILE # Diff specific file
dotfiles apply [-f] [-n]     # Apply dotfiles (create symlinks)
dotfiles collect [-n]        # Collect changes from ~ back to repo
dotfiles pull                # Pull latest and apply
dotfiles push [-m "msg"]     # Commit and push changes
```

### File Management

```bash
dotfiles add <file>          # Add file to tracking (symlink)
dotfiles add <file> -t copy  # Add as copy instead of symlink
dotfiles add <file> -s       # Add as encrypted secret
dotfiles add <file> -p mac   # Platform-specific (mac/linux/windows)
dotfiles remove <path>       # Remove from tracking
dotfiles files list          # List tracked files
dotfiles files check         # Verify file status
dotfiles import              # Scan ~ for common dotfiles
dotfiles import --dry-run    # Preview what would be imported
```

### Backup & Restore

```bash
dotfiles backup create [-n NAME]  # Create timestamped backup
dotfiles backup list              # List available backups
dotfiles backup restore NAME      # Restore from backup
```

### Secrets (git-crypt)

```bash
dotfiles secrets init             # Initialize git-crypt
dotfiles secrets unlock [-k KEY]  # Unlock secrets
dotfiles secrets lock             # Lock secrets
dotfiles secrets status           # Show git-crypt status
dotfiles secrets list             # List encrypted files
dotfiles secrets export-key [OUT] # Export key (base64 if no output)
dotfiles secrets add-pattern PAT  # Add encryption pattern
```

### Remote Deployment

```bash
dotfiles remote deploy HOST [-p PATH] [-b]  # Deploy via SSH
dotfiles remote sync-from HOST [-p PATH]    # Sync from remote
```

### Publishing

```bash
# Publish sanitized copy to public repo
dotfiles publish local [-m "msg"]
dotfiles publish local --no-push

# Publish bootstrap script to GitHub gist
dotfiles publish gist [-g GIST_ID]
```

Config: `config/publish.yaml`
```yaml
public_repo: https://github.com/USER/dotfiles-public.git
exclude:
  - "test/"
```

### Hooks

```bash
dotfiles hooks list              # List available hooks
dotfiles hooks create NAME [-p pre|post]  # Create hook script
```

Hooks run before/after operations (pre-apply, post-pull, etc.)

### Shell Completions

```bash
dotfiles completion generate [-s fish|bash|zsh]
dotfiles completion install [-s fish|bash|zsh]
```

### Utilities

```bash
dotfiles util ip [-a]        # Get public IP
dotfiles util serve [-p 8080] # Start HTTP server
dotfiles util ssh-init HOST [-u USER] [-H HOSTNAME] [-p PORT]
dotfiles util ghostty HOST   # Setup ghostty terminfo
```

### Git Helpers

```bash
dotfiles git init NAME [-p]  # Create GitHub repo (private default)
dotfiles git quick [-m "msg"] # Quick commit & push (any repo)
```

### Bootstrap & System

```bash
dotfiles bootstrap [-s stage]  # Full system setup
dotfiles doctor                # Verify system health
dotfiles update                # Update dotfiles-cli
dotfiles validate              # Validate config files
dotfiles run-script [-l]       # Run/list scripts
dotfiles cd                    # Print dotfiles path
dotfiles edit                  # Open in editor
```

### Packages (pkgmanager)

```bash
dotfiles pkg init [-t TYPES]
dotfiles pkg install TYPE NAME
dotfiles pkg remove TYPE NAME
dotfiles pkg update
dotfiles pkg list
```

### macOS

```bash
dotfiles mac backup    # Mackup backup
dotfiles mac restore   # Mackup restore
dotfiles mac brewfile  # Regenerate Brewfile
```

## Structure

```
~/dotfiles/
├── cli/                 # dotfiles-cli source
├── config/              # Configuration files
│   ├── files.yaml       # File manifest
│   ├── packages.yaml    # Package manifest
│   ├── publish.yaml     # Publish config
│   └── vars.yaml        # Template variables
├── scripts/             # Setup scripts
├── platform/            # Platform-specific (mac/, linux/)
│   └── mac/             # Brewfile, Mackup
├── files/
│   ├── home/            # Home directory dotfiles
│   ├── config/          # ~/.config files
│   └── secrets/         # Encrypted files
└── hooks/               # Pre/post hook scripts
```
