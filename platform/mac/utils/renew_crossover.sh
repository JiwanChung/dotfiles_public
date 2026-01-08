ppath="$HOME/Library/Preferences/com.codeweavers.CrossOver.plist"
opath="$HOME/Library/Application Support/CrossOver/Bottles/Steam/system.reg"
opathb="$HOME/Library/Application Support/CrossOver/Bottles/Steam/system.reg.backup"
cp "$opath" "$opathb"
awk -v pat="Software\\\\\\\\CodeWeavers\\\\\\\\CrossOver" -v n=5 '
  skip == 0 && index($0, pat) { skip = n }
  skip > 0 { skip--; next }
  { print }
' "$opath" > tmp && mv tmp "$opath"
ydate=$(date -v-1d +"%Y-%m-%d")
# open $path
defaults write $ppath FirstRunDate "$ydate 00:10:25"
