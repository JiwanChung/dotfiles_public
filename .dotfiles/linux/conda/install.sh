#!/bin/bash

ROOT=$DOTFILES/linux/conda
PATH="$PATH:$HOME/.local/bin"

eval "$(micromamba shell hook --shell bash)"
micromamba activate
micromamba install --yes --file $ROOT/requirements.txt --channel conda-forge --channel dnachun
