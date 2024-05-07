#!/bin/bash

ROOT=$DOTFILES/python

cat $ROOT/x_requirements.txt | xargs pipx install

# thefuck fix for python3.12
pipx inject thefuck setuptools
