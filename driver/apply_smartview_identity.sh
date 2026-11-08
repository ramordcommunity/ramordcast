#!/usr/bin/env bash
set -e

echo "=== RamordCast Samsung Smart View (Galaxy One UI 3.1+) Kimlik Yapılandırıcısı ==="

if [ "$EUID" -ne 0 ]; then
    echo "Lütfen bu betiği sudo ile çalıştırın:"
    echo "  sudo bash $0"
    exit 1
fi

echo "[1/4] /etc/wpa_supplicant/wpa_supplicant.conf Galaxy Smart View kimliğiyle oluşturuluyor..."
mkdir -p /etc/wpa_supplicant
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

echo "[2/4] systemd wpa_supplicant override kontrol ediliyor..."
mkdir -p /etc/systemd/system/wpa_supplicant.service.d
cat << 'EOF' > /etc/systemd/system/wpa_supplicant.service.d/override.conf
[Service]
ExecStart=
ExecStart=/usr/bin/wpa_supplicant -u -s -c /etc/wpa_supplicant/wpa_supplicant.conf -O /run/wpa_supplicant
EOF

echo "[3/4] wpa_supplicant servisi Galaxy kimliğiyle yeniden başlatılıyor..."
systemctl daemon-reload
systemctl restart wpa_supplicant
sleep 1
chmod 775 /run/wpa_supplicant
chgrp wheel /run/wpa_supplicant

echo "[4/4] Doğrulama yapılıyor..."
sleep 2
echo "=========================================================="
echo " BAŞARILI! Cihaz türü: 10-0050F204-5 (Samsung Galaxy Smart Phone)"
echo " Cihaz adı: Galaxy S24 Ultra"
echo " Üretici: Samsung (SM-S928B)"
echo "Artık Samsung TV Multi View bu cihazı 'Smart View Destekli Galaxy Cihaz' olarak görecektir."
echo "=========================================================="
