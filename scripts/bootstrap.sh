#!/usr/bin/env bash
# Bootstrap script for dotfiles
# Used by: dotfiles publish gist
# Placeholder {repo} is replaced at publish time
set -e

REPO="{repo}"
DOTFILES_DIR="$HOME/dotfiles"

echo "==> Bootstrapping dotfiles"

# Check git is available
if ! command -v git &>/dev/null; then
    echo "Error: git is not installed"
    exit 1
fi

# Install uv and micromamba
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &>/dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || eval "$(/usr/local/bin/brew shellenv)"
    fi
    brew install uv micromamba
else
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    echo "Installing micromamba..."
    mkdir -p "$HOME/.local/bin"
    curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj -C "$HOME/.local/bin" --strip-components=1 bin/micromamba
fi

# Ensure local bin is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Clone dotfiles
if [[ ! -d "$DOTFILES_DIR" ]]; then
    echo "Cloning dotfiles..."
    git clone "$REPO" "$DOTFILES_DIR"
else
    echo "Dotfiles already cloned, pulling latest..."
    git -C "$DOTFILES_DIR" pull
fi

# Install dotfiles-cli
echo "Installing dotfiles-cli..."
uv tool install "$DOTFILES_DIR/cli"

# Unlock secrets if key exists
if [[ -f "$HOME/.dotfiles-key" ]]; then
    echo "Unlocking secrets..."
    dotfiles secrets unlock -k "$HOME/.dotfiles-key"
fi

# Run bootstrap
echo "Running bootstrap..."
export DOTFILES="$DOTFILES_DIR"
dotfiles bootstrap

echo ""
echo "==> Bootstrap complete!"
echo "    Restart your shell or run: exec $SHELL"
