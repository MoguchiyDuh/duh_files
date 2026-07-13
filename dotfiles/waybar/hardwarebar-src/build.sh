#!/usr/bin/env bash
# Build hardwarebar and deploy the binary to ~/.local/bin.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="$HOME/.local/bin"

cd "$here"
cargo build --release

mkdir -p "$dest"
install -m 0755 target/release/hardwarebar "$dest/hardwarebar"
printf 'deployed %s\n' "$dest/hardwarebar"

# intel-rapl energy_uj is root-only by default (0400 root:root); grant the
# binary read capability so CPU power draw works without running as root.
# Skip if the node doesn't exist (no RAPL support) or is already readable
# (some kernels/configs relax this) -- setcap only when actually needed.
rapl="/sys/class/powercap/intel-rapl:0/energy_uj"
if [[ -e "$rapl" && ! -r "$rapl" ]]; then
    sudo setcap cap_dac_read_search=ep "$dest/hardwarebar"
    printf 'granted cap_dac_read_search for RAPL power reads\n'
fi

echo "Done."
