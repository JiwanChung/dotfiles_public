#!/bin/sh

# assume npm is already installed

ROOT=$DOTFILES/node

npm install -g npx

cat $ROOT/requirements.txt | xargs npx
