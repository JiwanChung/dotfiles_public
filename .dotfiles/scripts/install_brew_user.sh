mkdir -p ~/.local/Homebrew &&
curl -L https://github.com/Homebrew/brew/tarball/master |
tar xz --strip 1 -C ~/.local/Homebrew

mkdir -p ~/.local/bin &&
ln -s ~/.local/Homebrew/bin/brew ~/.local/bin

exec bash
