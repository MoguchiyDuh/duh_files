#!/usr/bin/env bash
# Build netbar and deploy the binary to ~/.local/bin.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="$HOME/.local/bin"

cd "$here"
cargo build --release

mkdir -p "$dest"
install -m 0755 target/release/netbar "$dest/netbar"
printf 'deployed %s\n' "$dest/netbar"
