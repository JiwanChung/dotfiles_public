#!/bin/sh

GITHUB_USERNAME=$1

sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply $GITHUB_USERNAME -k
cd ~/.local/share/chezmoi/.dotfiles
bash ./init.sh
