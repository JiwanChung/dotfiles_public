export DOTFILES=$HOME/.local/share/chezmoi/.dotfiles

rm ~/.mackup.cfg
cp ./.mackup.cfg ~/

# set cfg
mackup backup -f
# mackup restore uses symlinks, which does not work with iterm2
# hence we convert it back to hard-copies
mackup uninstall -f
