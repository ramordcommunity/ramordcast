#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/rtw88"

echo "=== RamordCast Realtek P2P Driver Installer (DKMS) ==="

if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo privileges:"
    echo "  sudo bash $0"
    exit 1
fi

echo "[1/5] Applying modprobe configuration..."
cp "$SOURCE_DIR/rtw88.conf" /etc/modprobe.d/rtw88.conf

echo "[2/5] Unloading legacy kernel modules..."
modprobe -r rtw88_8822ce rtw88_8822c rtw88_pci rtw88_core 2>/dev/null || true
modprobe -r rtw_8822ce rtw_8822c rtw_pci rtw_core 2>/dev/null || true

echo "[3/5] Checking and compiling DKMS module..."
if ! dkms status 2>/dev/null | grep -q "rtw88/0.6"; then
    mkdir -p /usr/src/rtw88-0.6
    cp -r "$SOURCE_DIR"/* /usr/src/rtw88-0.6/
    dkms add -m rtw88 -v 0.6
    dkms build -m rtw88 -v 0.6
    dkms install -m rtw88 -v 0.6 --force
else
    echo "  DKMS module is already compiled and installed."
fi

echo "[4/5] Loading Wi-Fi Direct capable kernel module..."
depmod -a
modprobe rtw_8822ce

echo "[5/5] Verifying P2P mode support..."
sleep 1
if iw list 2>/dev/null | grep -q "P2P-client"; then
    echo "=========================================================="
    echo " SUCCESS: Wi-Fi Direct (P2P-client & P2P-GO) is ACTIVE!"
    echo "=========================================================="
    echo "RamordCast can now establish direct P2P connections."
else
    echo " Module loaded. If interface modes are not refreshed yet, please reboot."
fi
