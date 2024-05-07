function _rclone_sync_ssh_config
    # Check if the input file is provided
    if test (count $argv) -ne 1
        echo "Usage: $argv[0] inputfile"
        exit 1
    end

    set -f inputfile $argv[1]

    # Initialize variables
    set -f _host ""
    set -f _hostname ""
    set -f _user ""
    set -f _identityfile ""

    # Process the input file line-by-line
    for line in (cat $inputfile)
        switch $line
            case 'Host *'
                if test -n "$_host"
                    echo "[$_host]"
                    echo "type = sftp"
                    echo "host = $_hostname"
                    echo "port = 22"
                    echo "user = $_user"
                    echo "key_file = $_identityfile"
                    echo "shell_type = unix"
                    echo ""
                end
                set -f _host (string sub -s 6 $line)
            case '*HostName *'
                set -f _hostname (string sub -s 10 $line)
            case '*User *'
                set -f _user (string sub -s 6 $line)
            case '*IdentityFile *'
                set -f _identityfile (string replace 'IdentityFile' '' $line | string trim)
        end
    end

    # Output the last host
    if test -n "$_host"
        echo "[$_host]"
        echo "type = sftp"
        echo "host = $_hostname"
        echo "port = 22"
        echo "user = $_user"
        echo "key_file = $_identityfile"
        echo "shell_type = unix"
    end
end

function rclone_sync_ssh_config
    if test -f "$HOME/.ssh/config"
        mkdir -p $HOME/.config/rclone
        _rclone_sync_ssh_config $HOME/.ssh/config > $HOME/.config/rclone/rclone.conf
    end
end

function rclone_mount
    rclone_sync_ssh_config
    set -f path $HOME/mnt/$argv[1]
    mkdir -p $path
    switch $(get_os)
      case mac
        if test -n $(brew list | rg macfuse)
            rclone mount $argv[1]":" $HOME/mnt/$argv[1] --daemon
            echo "connected"
        else
            echo "macfuse is required for rclone mounting"
        end
      case '*'
        # linux
        if type -q fusermount3
            rclone mount $argv[1]":" $HOME/mnt/$argv[1] --daemon
            echo "connected"
        else
            echo "fuse3 is required for rclone mounting"
        end
    end
end

function rclone_unmount
    # TODO: mac
    rclone_sync_ssh_config
    switch $(get_os)
      case mac
        if test -n $(brew list | rg macfuse)
            umount $HOME/mnt/$argv[1]
            echo "disconnected"
        else
            echo "macfuse is required for rclone unmounting"
        end
      case '*'
        # linux
        if type -q fusermount3
            fusermount3 -u -z $HOME/mnt/$argv[1]
            # mac: umount -u $HOME/mnt/$argv[1]
            echo "disconnected"
        else
            echo "fuse3 is required for rclone unmounting"
        end
    end
end


function rclone_run
    # run in the remote environment
    # get mnt name
    set -f local_path $(echo $PWD | sed 's@'"$HOME"'/mnt/@@')
    set -f name $(echo $local_path | cut -d/ -f1-1)
    set -f local_path $(echo $local_path | cut -d/ -f2-)
    set -f path $HOME/.config/rclone/temp.sh
    echo "cd $local_path" > $path
    echo "$argv" >> $path
    scp $path $name:~/.remote_command.sh > /dev/null 2>&1
    # ssh -t $name 'bash -s' < $path
    ssh -t $name "bash ~/.remote_command.sh"
end

function rclone_cd
    # ssh to the remote environment at $PWD
    set -f local_path $(echo $PWD | sed 's@'"$HOME"'/mnt/@@')
    set -f name $(echo $local_path | cut -d/ -f1-1)
    set -f local_path $(echo $local_path | cut -d/ -f2-)
    ssh -t $name "cd $local_path; bash --login"
end

function rclone_kill
    kill_all rclone
end

function rclone_list
    command mount -l | awk '/rclone/' | cut -d: -f1
end
