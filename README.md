## Installation

One-liner:

```bash
export USERNAME=JiwanChung
curl -fsSL https://gist.github.com/JiwanChung/9e45e238dd4ccebd2bc1cc30fae64f0d/raw/0079ae23bae1dc6bac63d528e6d392b2243fc6bc/bootstrap_dotfiles.sh | bash -s -- $USERNAME 
```

- `$PUBLIC_REPO` should be a public github repository built with `publish.sh`, while your `dotfiles` repository can be private.

Manual clone & install

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply $GITHUB_USERNAME -k

cd ~/.local/share/chezmoi/.dotfiles
bash ./init.sh
```

For encrypted ssh keys, prepare the `.dotfiles_key.txt` file.


## Usage

- `zoxider`:
    - `z`
- `fzf.fish`:
    - Alt + [(f)iles, (l)og-git, (s)tatus-git, (h)istory-command, (p)rocesses, (v)ariables]
    - [fzf.fish](https://github.com/PatrickF1/fzf.fish)
- `croc`:
    - Send+Receive files quick
    - [croc](https://github.com/schollz/croc)
