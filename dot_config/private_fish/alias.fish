switch (uname)
    case Darwin
        # brew does not map python to python3
        alias python="python3"
        alias pip="pip3"
end

# vi
alias vim=nvim
alias vi=vim

# python
alias pi="pip install"
alias piu="pip uninstall"
alias pis="pip_show_package"

# chezmoi
alias cha="chezmoi add"
alias chae="chezmoi add --encrypt"
alias che="chezmoi_edit"
alias chd="chezmoi diff"
alias chra="chezmoi re-add"
alias chr="chezmoi remove --force"
alias chp="chezmoi apply -k --force"
alias chc="cd $CHEZMOI_SOURCE_DIR"
alias cdd="cd $DOT_HOME"
alias cdf="cd ~/.config/fish"

# ls 
alias ls="eza"
alias la="ls -al --icons"

# conda
alias conda="micromamba"
 
alias ca="conda activate"
alias cad="conda deactivate"
alias cl="conda list"

# tmux
alias tl="tmuxp load -y"

# command alternatives
alias which="type"
alias ps="procs"
alias du="dust"
alias jless="fx"
alias fd="fd -H"
alias find="fd"
alias df="duf"
alias monitor="btm"
alias gputop="nvitop"
alias cat="bat"
alias mcd="mkdir_cd"
alias rsync="rsync -z --info=progress2"
alias ghc="gh repo create --private"
alias rg="rg --hidden"
if command -q viddy
    alias watch="viddy"
end

if command -q tiptop
    alias top="tiptop"
end

if command -q imgcatr
    alias imgcat="imgcatr"
end

if command -q whalespotter
    alias whos_big="whalespotter"
    alias wb="whalespotter"
end

# rclone
alias rcm="rclone_mount"
alias rcu="rclone_unmount"
alias mount="rclone_mount"
alias unmount="rclone_unmount"
alias rcr="rclone_run"
alias rcc="rclone_cd"
alias rck="rclone_kill"
alias rcl="rclone_list"

# cuda
alias C="cuda_set"

# dotfiles
alias doti="dotfiles_install"
alias dotu="dotfiles_update"

# compression
alias zip="ouch compress"
alias unzip="ouch decompress"

# custom
alias st="open_ssh_tunnel"
if command -q trex
    alias x="trex"
end
