function chezmoi_edit
    set -f file $argv[1]
    touch $file
    chezmoi add $file
    chezmoi edit --apply $file
end
