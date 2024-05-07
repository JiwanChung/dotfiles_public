#!/bin/bash

echo "Installing Dotfiles"

export DOTFILES=$HOME/.local/share/chezmoi/.dotfiles

export PATH="$PATH:$HOME/.local/bin"
cp $DOTFILES/.dotfiles_key.txt $HOME
cp $DOTFILES/chezmoi.toml $HOME/.config/chezmoi
chezmoi apply -k  # catch error: no encryption key

if [[ $OSTYPE == 'darwin'* ]]; then
   /bin/bash $DOTFILES/mac/init.sh
else
   /bin/bash $DOTFILES/linux/init.sh
fi

/bin/bash $DOTFILES/scripts/install_age.sh
/bin/bash $DOTFILES/scripts/install_croc.sh
/bin/bash $DOTFILES/python/install.sh
/bin/bash $DOTFILES/rust/install.sh
# /bin/bash $DOTFILES/scripts/install_space_vim.sh

fish $DOTFILES/scripts/install_fisher.fish
