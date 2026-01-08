#!/bin/bash


for f in utils/*.sh; do alias "$(basename "${f%.sh}")"="bash $(realpath "$f")"; done
