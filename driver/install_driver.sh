#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/rtw88"

echo "=== RamordCast Realtek P2P Sürücü Yükleyici (DKMS) ==="

if [ "$EUID" -ne 0 ]; then
    echo "Lütfen bu betiği sudo yetkisiyle çalıştırın:"
    echo "  sudo bash $0"
    exit 1
fi

echo "[1/5] Çakışmayı önleyici modprobe yapılandırması uygulanıyor..."
cp "$SOURCE_DIR/rtw88.conf" /etc/modprobe.d/rtw88.conf

echo "[2/5] Eski çekirdek modülleri bellekten boşaltılıyor..."
modprobe -r rtw88_8822ce rtw88_8822c rtw88_pci rtw88_core 2>/dev/null || true
modprobe -r rtw_8822ce rtw_8822c rtw_pci rtw_core 2>/dev/null || true

echo "[3/5] DKMS kontrolü ve kurulumu..."
if ! dkms status | grep -q "rtw88/0.6"; then
    mkdir -p /usr/src/rtw88-0.6
    cp -r "$SOURCE_DIR"/* /usr/src/rtw88-0.6/
    dkms add -m rtw88 -v 0.6
    dkms build -m rtw88 -v 0.6
    dkms install -m rtw88 -v 0.6 --force
else
    echo "  DKMS modülü zaten derlenmiş ve kurulu."
fi

echo "[4/5] Yeni P2P destekli modül yükleniyor..."
depmod -a
modprobe rtw_8822ce

echo "[5/5] Doğrulama yapılıyor..."
sleep 1
if iw list 2>/dev/null | grep -q "P2P-client"; then
    echo "=========================================================="
    echo " BAŞARILI! Wi-Fi Direct (P2P-client & P2P-GO) AKTİF EDİLDİ!"
    echo "=========================================================="
    echo "Artık RamordCast televizyona doğrudan Windows PC gibi bağlanabilir."
else
    echo " Modül yüklendi ancak arayüz henüz listelenmediyse bilgisayarı yeniden başlatabilirsiniz."
fi
