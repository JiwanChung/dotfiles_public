#!/bin/bash
set -euo pipefail

BINPATH="$HOME/.local/share"
CONFIG="$HOME/.config/helix"
RUNTIME_SRC="$BINPATH/helix/runtime"
RUNTIME_DEST="$CONFIG/runtime"

# Check helix is installed
if ! command -v hx >/dev/null 2>&1; then
    echo "[!] helix (hx) not found. Please install it first."
    exit 1
fi

echo "[*] Fetching helix grammars..."
hx --grammar fetch

# Setup runtime symlink
if [[ -d "$RUNTIME_SRC" ]]; then
    mkdir -p "$CONFIG"
    rm -rf "$RUNTIME_DEST"
    ln -s "$RUNTIME_SRC" "$RUNTIME_DEST"
    echo "[*] Linked runtime: $RUNTIME_SRC -> $RUNTIME_DEST"
else
    echo "[!] Runtime source not found: $RUNTIME_SRC (skipping symlink)"
fi

# Install simple-completion-language-server if not present
if ! command -v simple-completion-language-server >/dev/null 2>&1; then
    if ! command -v cargo >/dev/null 2>&1; then
        echo "[!] cargo not found. Cannot install simple-completion-language-server."
        exit 1
    fi
    echo "[*] Installing simple-completion-language-server..."
    cargo install --git https://github.com/estin/simple-completion-language-server.git
else
    echo "[*] simple-completion-language-server already installed"
fi

echo "[*] Helix setup complete"
