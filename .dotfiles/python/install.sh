#!/bin/bash

ROOT=$DOTFILES/python

pip install -r $ROOT/requirements.txt
/bin/bash $ROOT/install_pipx_packages.sh
