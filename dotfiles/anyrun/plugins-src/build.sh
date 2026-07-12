#!/usr/bin/env bash
# Build all custom anyrun plugins and deploy the .so files to the plugins dir.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="${XDG_CONFIG_HOME:-$HOME/.config}/anyrun/plugins"

cd "$here"
cargo build --release

mkdir -p "$dest"
for so in target/release/lib{clipboard,windows,sysctl,binds,transform}.so; do
    [ -f "$so" ] && install -m 0755 "$so" "$dest/" && printf 'deployed %s\n' "$(basename "$so")"
done

echo "Done. Restart the daemon:  anyrun quit; anyrun daemon &"
