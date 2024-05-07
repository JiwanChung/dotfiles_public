#!/bin/bash

echo "Updating Dotfiles"

export DOTFILES=$HOME/.local/share/chezmoi/.dotfiles

cd $DOTFILES
git stash
git pull

chezmoi apply

if [[ $OSTYPE == 'darwin'* ]]; then
   /bin/bash $DOTFILES/mac/update.sh
else
   /bin/bash $DOTFILES/linux/update.sh
fi

echo "done"
