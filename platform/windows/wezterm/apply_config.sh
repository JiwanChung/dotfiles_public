#!/bin/bash

USER=$(wslpath $(cmd.exe /C "echo %USERPROFILE%" 2>/dev/null | tr -d '\r'))
DIST=$(wsl.exe -l --running -q | tr -d '\r' | tr -d '\0')
cat wezterm.lua | sed -E "s/WSL:Ubuntu/WSL:$DIST/g" > $USER/.wezterm.lua
