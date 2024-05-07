set paths = [/opt/homebrew/bin $E:HOME/.local/bin $@paths]
eval (starship init elvish)

# eval (slurp < $pwd/alias.elv)

use github.com/iandol/elvish-modules/mamba

# alias

fn python {|@a| python3 $@a}
fn pip {|@a| pip3 $@a}

fn pi {|@a| pip3 install $@a}
fn piu {|@a| pip3 uninstall $@a}

# chezmoi
fn cha {|@a| chezmoi add $@a }
fn che {|@a| chezmoi edit --apply $@a }
fn chc { chezmoi cd }

# ls 
fn ls { |@a| eza $@a }
fn la { |@a| ls -a $@a }

# conda
fn conda { |@a| micromamba $@a }

fn ca { |@a| mamba:activate $@a }
fn cad { mamba:deactivate }
fn cl { mamba:list }
