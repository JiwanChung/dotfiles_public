#!/bin/bash

ROOT=$DOTFILES/linux

# we manage pacakges via conda (micromamba for speed)
/bin/bash $ROOT/scripts/install_mamba.sh

/bin/bash $ROOT/conda/install.sh

/bin/bash $ROOT/scripts/install_font.sh

/bin/bash $ROOT/scripts/install_neovim.sh

/bin/bash $ROOT/scripts/install_chezmoi.sh

/bin/bash $ROOT/scripts/install_viddy.sh

/bin/bash $ROOT/scripts/install_yazi.sh
