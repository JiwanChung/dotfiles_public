function mkdir_cd
    mkdir -p $argv
    cd $argv
end

function cuda_set
    set -lx CUDA_VISIBLE_DEVICES $argv[1]; $argv[2..-1]
end

function get_ip
  set --local options 'a/all'
  argparse $options -- $argv

  if set --query _flag_all
    curl https://ipinfo.io/json
  else
    curl https://ipinfo.io/ip
  end
end

function open_ssh_tunnel
  # set --local options --min-args 2 's/server' 'p/port' 
  # argparse $options -- $argv
  argparse 'h/help' -- $argv
  if set --query _flag_help
    echo 'open_ssh_tunnel $SERVER $PORT'
  else
    ssh -L "$argv[2]:0.0.0.0:$argv[2]" -N -f "$argv[1]"
  end
end

function string_contains
  set --local flag $(string match "*"$argv[2]"*" $argv[1] | string trim)
  if test -n "$flag"
    echo true
  end
end

function get_os
  set --local name $(uname -a | string lower)
  if test -n "$(string_contains $name darwin)"
    echo mac
  else
    if test -n "$(string_contains $name wsl)"
      echo wsl
    else
      echo linux
    end
  end
end

function clip
  switch $(get_os)
    case mac
      pbcopy
    case wsl
      clip.exe
    case '*'
      xcopy
  end
end

function kill_all
  command ps -ef | grep $argv[1] | grep -v grep | awk '{print $2}' | xargs -r kill -9
end

function yy
    set tmp (mktemp -t "yazi-cwd.XXXXXX")
    yazi $argv --cwd-file="$tmp"
    if set cwd (cat -- "$tmp"); and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
        cd -- "$cwd"
    end
    rm -f -- "$tmp"
end
