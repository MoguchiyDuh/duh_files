#!/usr/bin/env bash
# Build soundbar and deploy the binary to ~/.local/bin.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="$HOME/.local/bin"

cd "$here"
cargo build --release

mkdir -p "$dest"
install -m 0755 target/release/soundbar "$dest/soundbar"
printf 'deployed %s\n' "$dest/soundbar"
