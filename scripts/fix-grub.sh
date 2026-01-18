#!/bin/bash
# Fix GRUB to detect Windows/other OS in dual-boot setup

set -e

echo "=== GRUB Dual-Boot Fixer ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Usage: sudo ./fix-grub.sh"
    exit 1
fi

# Backup current GRUB config
echo "[1/4] Backing up current GRUB config..."
cp /etc/default/grub /etc/default/grub.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ Backup created"
echo

# Enable os-prober
echo "[2/4] Enabling os-prober in GRUB config..."
if grep -q "^GRUB_DISABLE_OS_PROBER=false" /etc/default/grub; then
    echo "✓ os-prober already enabled"
else
    if grep -q "^#GRUB_DISABLE_OS_PROBER" /etc/default/grub; then
        sed -i 's/^#GRUB_DISABLE_OS_PROBER=true/GRUB_DISABLE_OS_PROBER=false/' /etc/default/grub
    elif grep -q "^GRUB_DISABLE_OS_PROBER" /etc/default/grub; then
        sed -i 's/^GRUB_DISABLE_OS_PROBER=true/GRUB_DISABLE_OS_PROBER=false/' /etc/default/grub
    else
        echo "GRUB_DISABLE_OS_PROBER=false" >> /etc/default/grub
    fi
    echo "✓ os-prober enabled"
fi
echo

# Run os-prober to detect other operating systems
echo "[3/4] Running os-prober to detect other OS..."
if command -v os-prober &> /dev/null; then
    os-prober
    echo "✓ os-prober scan complete"
else
    echo "⚠ Warning: os-prober not installed"
    echo "Install with: pacman -S os-prober"
fi
echo

# Regenerate GRUB configuration
echo "[4/4] Regenerating GRUB configuration..."
grub-mkconfig -o /boot/grub/grub.cfg
echo "✓ GRUB config regenerated"
echo

echo "=== Done! ==="
echo "Reboot to see changes in GRUB menu"
