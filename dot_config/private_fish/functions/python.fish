function pip_show_package
  pip list | rg $argv
end
