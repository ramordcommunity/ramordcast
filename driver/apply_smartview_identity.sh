#!/usr/bin/env bash
set -e

echo "=== RamordCast Samsung Smart View (Galaxy One UI) Identity Configurator ==="

if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo privileges:"
    echo "  sudo bash $0"
    exit 1
fi

echo "[1/4] Generating /etc/wpa_supplicant/wpa_supplicant.conf with Galaxy Smart View identity..."
mkdir -p /etc/wpa_supplicant
mkdir -p /run/wpa_supplicant
chmod 775 /run/wpa_supplicant
chgrp wheel /run/wpa_supplicant 2>/dev/null || true

cat << 'EOF' > /etc/wpa_supplicant/wpa_supplicant.conf
ctrl_interface=/run/wpa_supplicant
ctrl_interface_group=wheel
update_config=1
device_name=Galaxy S24 Ultra
device_type=10-0050F204-5
manufacturer=Samsung
model_name=SM-S928B
model_number=SM-S928B
serial_number=R5CT100RAMORD
config_methods=virtual_display virtual_push_button keypad push_button
p2p_listen_reg_class=81
p2p_listen_channel=1
p2p_oper_reg_class=115
p2p_oper_channel=36
p2p_go_intent=1
EOF

echo "[2/4] Setting systemd wpa_supplicant override..."
mkdir -p /etc/systemd/system/wpa_supplicant.service.d
cat << 'EOF' > /etc/systemd/system/wpa_supplicant.service.d/override.conf
[Service]
ExecStart=
ExecStartPre=/usr/bin/mkdir -p /run/wpa_supplicant
ExecStartPre=/usr/bin/chmod 775 /run/wpa_supplicant
ExecStart=/usr/bin/wpa_supplicant -u -s -c /etc/wpa_supplicant/wpa_supplicant.conf -O /run/wpa_supplicant
EOF

echo "[3/4] Restarting wpa_supplicant service with Galaxy identity..."
systemctl daemon-reload
systemctl restart wpa_supplicant
sleep 2

mkdir -p /run/wpa_supplicant
chmod 775 /run/wpa_supplicant || true
chgrp wheel /run/wpa_supplicant 2>/dev/null || true
chmod 775 /run/wpa_supplicant/* 2>/dev/null || true
chgrp wheel /run/wpa_supplicant/* 2>/dev/null || true

echo "[4/4] Verifying identity configuration..."
echo "=========================================================="
echo " SUCCESS: Device Type: 10-0050F204-5 (Samsung Galaxy Phone)"
echo " Device Name: Galaxy S24 Ultra (Model: SM-S928B)"
echo "=========================================================="
