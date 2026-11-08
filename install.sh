#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "          🖥️  Ramord Cast - Otomatik Kurulum Aracı         "
echo "   Ultra-Low Latency Samsung & Tizen Screen Mirroring     "
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Dağıtım tespiti ve paket kurulumu
echo "[1/4] Sistem bağımlılıkları kontrol ediliyor ve kuruluyor..."

install_packages() {
    if command -v pacman >/dev/null 2>&1; then
        echo "--> Arch / CachyOS / Manjaro tespit edildi."
        sudo pacman -S --needed --noconfirm \
            python \
            python-gobject \
            python-requests \
            gtk4 \
            libadwaita \
            pipewire \
            gstreamer \
            gst-plugins-base \
            gst-plugins-good \
            gst-plugins-bad \
            gst-plugins-ugly \
            dkms
    elif command -v apt-get >/dev/null 2>&1; then
        echo "--> Ubuntu / Debian / Mint tespit edildi."
        sudo apt-get update
        sudo apt-get install -y \
            python3 \
            python3-gi \
            python3-gi-cairo \
            python3-requests \
            gir1.2-gtk-4.0 \
            gir1.2-adw-1 \
            pipewire \
            gstreamer1.0-tools \
            gstreamer1.0-plugins-base \
            gstreamer1.0-plugins-good \
            gstreamer1.0-plugins-bad \
            gstreamer1.0-plugins-ugly \
            dkms
    elif command -v dnf >/dev/null 2>&1; then
        echo "--> Fedora / RHEL tespit edildi."
        sudo dnf install -y \
            python3 \
            python3-gobject \
            python3-requests \
            gtk4 \
            libadwaita \
            pipewire \
            gstreamer1-plugins-base \
            gstreamer1-plugins-good \
            gstreamer1-plugins-bad-free \
            gstreamer1-plugins-ugly-free \
            dkms
    else
        echo "⚠️  Paket yöneticisi otomatik algılanamadı. Lütfen Python, GTK4 ve GStreamer paketlerini manuel kurun."
    fi
}

install_packages

# 2. Sistem komutu (CLI Launcher)
echo "[2/4] Sistem komutu (ramordcast) yapılandırılıyor..."
LAUNCHER_PATH="/usr/local/bin/ramordcast"
sudo bash -c "cat << 'EOF' > $LAUNCHER_PATH
#!/usr/bin/env bash
python3 \"$SCRIPT_DIR/main.py\" \"\$@\"
EOF"
sudo chmod +x "$LAUNCHER_PATH"

# 3. Masaüstü Başlatıcı (Desktop Shortcut)
echo "[3/4] Masaüstü kısayolu oluşturuluyor..."
APPLICATIONS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPLICATIONS_DIR"

cat << EOF > "$APPLICATIONS_DIR/com.ramord.cast.desktop"
[Desktop Entry]
Name=Ramord Cast
Comment=Ultra Low-Latency Samsung & Tizen Screen Mirror
Comment[tr]=Ultra Düşük Gecikmeli Samsung & Tizen Ekran Yansıtıcı
Comment[en]=Ultra Low-Latency Samsung & Tizen Screen Mirror
Comment[de]=Ultra-Low-Latency Samsung & Tizen Bildschirmspiegelung
Comment[es]=Espejo de Pantalla Samsung & Tizen de Ultra Baja Latencia
Comment[fr]=Miroir d'Écran Samsung & Tizen à Ultra Faible Latence
Comment[it]=Duplicazione Schermo Samsung & Tizen ad Ultra Bassa Latenza
Exec=ramordcast
Icon=video-display
Terminal=false
Type=Application
Categories=AudioVideo;Video;Network;Utility;
Keywords=cast;mirror;samsung;tizen;display;screen;
StartupNotify=true
EOF

chmod +x "$APPLICATIONS_DIR/com.ramord.cast.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
fi

# 4. Donanım / Sürücü Kontrolü (Realtek Wi-Fi Direct)
echo "[4/4] Donanım uyumluluğu kontrol ediliyor..."
if lspci | grep -qi "RTL8822CE\|RTL8821CE"; then
    echo ""
    echo "⚠️  Sisteminizde Realtek Wi-Fi yongası tespit edildi."
    echo "   Linux'ta Wi-Fi Direct (P2P) için sürücü yaması gerekebilir."
    echo "   Kurmak için: sudo bash $SCRIPT_DIR/driver/install_driver.sh"
fi

echo ""
echo "=========================================================="
echo " 🎉 KURULUM BAŞARIYLA TAMAMLANDI!                         "
echo "=========================================================="
echo " Ramord Cast uygulamasını başlatmak için:"
echo "   1) Başlat menüsünden 'Ramord Cast' simgesine tıklayın,"
echo "   2) Veya terminalde doğrudan 'ramordcast' yazın."
echo "=========================================================="
