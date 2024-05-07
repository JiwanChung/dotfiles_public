#!/bin/bash

FONT_NAME="Caskaydia Cove"
FONT_NAME_URL="Caskaydia%20Cove"
FONT_PATH="CascadiaCode"

FONT_DIR="$HOME/.local/share/fonts"

mkdir -p $FONT_DIR
curl -fLo "$FONT_DIR/$FONT_NAME Nerd Font Complete.ttf" \
	https://github.com/ryanoasis/nerd-fonts/raw/2.1.0/patched-fonts/$FONT_PATH/complete/$FONT_NAME_URL%20Nerd%20Font%20Complete.ttf
fc-cache $FONT_DIR
