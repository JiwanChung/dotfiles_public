if status is-interactive
    # Commands to run in interactive sessions can go here
end

starship init fish | source

fish_add_path /opt/homebrew/bin
fish_add_path $HOME/micromamba/bin
fish_add_path $HOME/.local/bin

set -gx DOT_HOME "$HOME/.local/share/chezmoi/.dotfiles"
set -gx DOTFILES "$HOME/.local/share/chezmoi/.dotfiles"
# set -gx SHELL $(which fish)
set -gx FISH_HOME "$HOME/.config/fish"
if type -q ssh-agent
    set -gx SSH_AUTH_SOCK $(ssh-agent | awk -F'[=;]' '/^SSH_AUTH_SOCK/{print $2}')
end

source $FISH_HOME/functions/mine.fish
source $FISH_HOME/alias.fish

set -g fish_key_bindings fish_vi_key_bindings

# for fzf.fish

set -g fzf_fd_opts --hidden --exclude=.git
# use default ctrl + alt
# fzf_configure_bindings --directory=\ef --git_status=\es --variables=\ev --processes=\ep --history=\eh

# >>> mamba initialize >>>
# !! Contents within this block are managed by 'mamba init' !!
set -gx MAMBA_EXE "$(command which micromamba)"
set -gx MAMBA_ROOT_PREFIX "$HOME/micromamba"
$MAMBA_EXE shell hook --shell fish --root-prefix $MAMBA_ROOT_PREFIX | source
# <<< mamba initialize <<<

zoxide init fish | source
