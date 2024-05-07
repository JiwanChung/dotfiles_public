export DOTFILES=$HOME/.local/share/chezmoi/.dotfiles

rm -rf $HOME/.mackup
rm -rf $HOME/.mackup.cfg

ln -s $DOTFILES/mac/mackup/.mackup $HOME/.mackup
ln -s $DOTFILES/mac/mackup/.mackup.cfg $HOME/.mackup.cfg

bash $DOTFILES/mac/mackup/remove.sh

# set cfg
mackup restore -f
