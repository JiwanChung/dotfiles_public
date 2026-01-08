local wezterm = require 'wezterm'
local config = wezterm.config_builder()

config.default_domain = 'WSL:Ubuntu'
config.color_scheme = 'Tomorrow Night Bright (Gogh)'
config.font_size = 10.0
config.font = wezterm.font 'CaskaydiaCove Nerd Font'
config.ssh_backend = "Ssh2"
config.window_close_confirmation = 'NeverPrompt'
config.skip_close_confirmation_for_processes_named = {
  'bash',
  'sh',
  'zsh',
  'fish',
  'tmux',
  'nu',
  'cmd.exe',
  'wsl.exe',
  'pwsh.exe',
  'powershell.exe',
}

return config
