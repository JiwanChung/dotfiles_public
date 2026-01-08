USER=$(wslpath $(cmd.exe /C "echo %USERPROFILE%" 2>/dev/null | tr -d '\r'))
cp config.toml $USER/AppData/Local/rio/config.toml
