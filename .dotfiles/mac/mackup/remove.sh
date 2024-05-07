#!/bin/bash

ROOT=$DOTFILES/mac/mackup/cfgs

PATH1=Library/Preferences
PATH2='Library/Application Support'

ls -d "$ROOT/$PATH1/"* | rev | cut -d'/' -f 1-3 | rev | xargs -I {} rm -rfv "$HOME"/{}
ls -d "$ROOT/$PATH2/"* | rev | cut -d'/' -f 1-3 | rev | xargs -I {} rm -rfv "$HOME"/{}
