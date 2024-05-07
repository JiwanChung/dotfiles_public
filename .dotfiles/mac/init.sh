#!/bin/bash

export DOTFILES=$HOME/.local/share/chezmoi/.dotfiles

# install brew

if test ! $(which brew); then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
fi

brew update

# install packages

brew tap homebrew/bundle
brew tap homebrew/cask-fonts
brew bundle --file $DOTFILES/mac/Brewfile
brew bundle --file $DOTFILES/mac/UI_Brewfile
bash $DOTFILES/mac/scripts/install_rclone.sh

# restore mac setups

bash $DOTFILES/mac/mackup/restore.sh
cp -r $DOTFILES/mac/preferences/* $HOME/Downloads/
