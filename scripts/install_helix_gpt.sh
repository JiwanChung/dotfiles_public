#!/bin/bash
set -euo pipefail

VERSION="0.31"
INSTALL_DIR="$HOME/.local/bin"
TMP_DIR=$(mktemp -d)

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# Detect OS
case "$(uname -s)" in
    Linux*)  OS="linux" ;;
    Darwin*) OS="macos" ;;
    *)       echo "[!] Unsupported OS: $(uname -s)"; exit 1 ;;
esac

# Detect architecture
case "$(uname -m)" in
    x86_64)  ARCH="x86_64" ;;
    aarch64) ARCH="aarch64" ;;
    arm64)   ARCH="aarch64" ;;
    *)       echo "[!] Unsupported architecture: $(uname -m)"; exit 1 ;;
esac

FILENAME="helix-gpt-${VERSION}-${ARCH}-${OS}.tar.gz"
URL="https://github.com/leona/helix-gpt/releases/download/${VERSION}/${FILENAME}"

echo "[*] Downloading helix-gpt ${VERSION} for ${OS}/${ARCH}..."

if ! curl -fsSL "$URL" -o "$TMP_DIR/helix-gpt.tar.gz"; then
    echo "[!] Failed to download helix-gpt"
    echo "[!] URL: $URL"
    exit 1
fi

echo "[*] Extracting..."
tar -xzf "$TMP_DIR/helix-gpt.tar.gz" -C "$TMP_DIR"

# Find the extracted binary (naming varies by platform)
BINARY=$(find "$TMP_DIR" -name 'helix-gpt*' -type f ! -name '*.tar.gz' | head -1)

if [[ -z "$BINARY" ]]; then
    echo "[!] Could not find helix-gpt binary in archive"
    exit 1
fi

mkdir -p "$INSTALL_DIR"
mv "$BINARY" "$INSTALL_DIR/helix-gpt"
chmod +x "$INSTALL_DIR/helix-gpt"

echo "[*] Installed helix-gpt to $INSTALL_DIR/helix-gpt"
