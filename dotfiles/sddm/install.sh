#!/usr/bin/env bash
set -Eeuo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install -Dm0755 "$here/dyntheme-sddm-sync" /usr/local/bin/dyntheme-sddm-sync
install -Dm0755 "$here/sddm-theme" /usr/local/bin/sddm-theme
install -Dm0644 "$here/systemd/dyntheme-sddm-sync.service" /etc/systemd/system/dyntheme-sddm-sync.service
install -Dm0644 "$here/systemd/dyntheme-sddm-sync.path" /etc/systemd/system/dyntheme-sddm-sync.path
install -Dm0644 "$here/polkit/49-sddm-power.rules" /etc/polkit-1/rules.d/49-sddm-power.rules

install -d /etc/sddm.conf.d
printf '[Theme]\nCurrent=dyntheme\n' >/etc/sddm.conf.d/10-dyntheme.conf

systemctl daemon-reload
systemctl enable --now dyntheme-sddm-sync.path
/usr/local/bin/dyntheme-sddm-sync
printf 'dyntheme SDDM theme installed.\n'
