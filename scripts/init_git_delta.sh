#!/bin/sh
set -e

if ! command -v delta >/dev/null 2>&1; then
    echo "[!] delta not found. Please install it first."
    exit 1
fi

git config --global core.pager delta
echo "[*] Git pager set to delta"
