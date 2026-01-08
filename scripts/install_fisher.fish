#!/usr/bin/env fish

# Fisher plugin manager for fish shell
# Pinned to version 4.4.4 for stability
set -l fisher_version "4.4.4"
set -l fisher_url "https://raw.githubusercontent.com/jorgebucaran/fisher/$fisher_version/functions/fisher.fish"

echo "[*] Installing Fisher $fisher_version..."

if not curl -sL "$fisher_url" | source
    echo "[!] Failed to download Fisher"
    exit 1
end

if not fisher install jorgebucaran/fisher
    echo "[!] Failed to install Fisher"
    exit 1
end

echo "[*] Fisher installed successfully"
