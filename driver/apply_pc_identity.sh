#!/usr/bin/env bash
set -e

echo "=== RamordCast wpa_supplicant PC Kimliği ve WFD Miracast Yapılandırıcısı ==="

if [ "$EUID" -ne 0 ]; then
    echo "Lütfen bu betiği sudo ile çalıştırın:"
    echo "  sudo bash $0"
    exit 1
fi

echo "[1/4] /etc/wpa_supplicant/wpa_supplicant.conf PC + WFD Source olarak yapılandırılıyor..."
mkdir -p /etc/wpa_supplicant
mkdir -p /run/wpa_supplicant
chmod 775 /run/wpa_supplicant
chgrp wheel /run/wpa_supplicant 2>/dev/null || true

cat << 'EOF' > /etc/wpa_supplicant/wpa_supplicant.conf
ctrl_interface=/run/wpa_supplicant
ctrl_interface_group=wheel
update_config=1
device_name=Ramord-PC
device_type=1-0050F204-1
wifi_display=1
config_methods=virtual_display virtual_push_button keypad push_button
p2p_listen_reg_class=81
p2p_listen_channel=1
p2p_oper_reg_class=115
p2p_oper_channel=36
p2p_go_intent=1
EOF

echo "[2/4] systemd wpa_supplicant override ayarlanıyor..."
mkdir -p /etc/systemd/system/wpa_supplicant.service.d
cat << 'EOF' > /etc/systemd/system/wpa_supplicant.service.d/override.conf
[Service]
ExecStart=
ExecStartPre=/usr/bin/mkdir -p /run/wpa_supplicant
ExecStartPre=/usr/bin/chmod 775 /run/wpa_supplicant
ExecStart=/usr/bin/wpa_supplicant -u -s -c /etc/wpa_supplicant/wpa_supplicant.conf -O /run/wpa_supplicant
EOF

echo "[3/4] wpa_supplicant servisi yeniden başlatılıyor..."
systemctl daemon-reload
systemctl restart wpa_supplicant
sleep 2

mkdir -p /run/wpa_supplicant
chmod 775 /run/wpa_supplicant || true
chgrp wheel /run/wpa_supplicant 2>/dev/null || true
chmod 775 /run/wpa_supplicant/* 2>/dev/null || true
chgrp wheel /run/wpa_supplicant/* 2>/dev/null || true

echo "[4/4] WFD Subelement ve PC Kimliği uygulanıyor..."
wpa_cli -p /run/wpa_supplicant -i wlan0 p2p_set wfd_subelem 0 000600101c440032 2>/dev/null || true
wpa_cli -p /run/wpa_supplicant -i wlan0 set wfd_device_type 1-0050F204-1 2>/dev/null || true

echo "=========================================================="
echo " BAŞARILI! Cihaz türü: 1-0050F204-1 (Category 1: Computer / PC)"
echo " WFD Modu: wifi_display=1 (Wi-Fi Display Miracast Source)"
echo " Cihaz adı: Ramord-PC"
echo "=========================================================="
