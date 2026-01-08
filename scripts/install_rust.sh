#!/bin/bash

set -euo pipefail

if ! command -v cargo >/dev/null 2>&1; then
    echo "[*] cargo not found. Installing Rust toolchain..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
else
    echo "[*] cargo is already available. Skipping Rust install."
    source "$HOME/.cargo/env"  # ensures cargo is in path for the rest of the script
fi


if command -v rustup >/dev/null 2>&1; then
  echo "[*] Updating Rust toolchain..."
  cargo install --list >/dev/null  # force .cargo/bin to initialize
  rustup update
fi

if ! cargo install --list | grep -q '^cargo-update '; then
    echo "[*] Installing cargo-update..."
    cargo install cargo-update
else
    echo "[*] cargo-update is already installed."
fi
