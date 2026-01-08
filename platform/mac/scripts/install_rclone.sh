#!/bin/bash
# rclone with mount support


cd $HOME/.cache
curl -O https://downloads.rclone.org/rclone-current-osx-amd64.zip
unzip -a rclone-current-osx-amd64.zip && cd rclone-*-osx-amd64
mv rclone $HOME/.local/bin
rm -rf rclone-*-osx-amd64 rclone-current-osx-amd64.zip
rclone config
