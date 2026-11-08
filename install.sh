#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "          Ramord Cast - Automated Installation Tool      "
echo "   Ultra-Low Latency Samsung & Tizen Screen Mirroring     "
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Distribution detection and dependency installation
echo "[1/4] Checking and installing system dependencies..."

install_packages() {
    if command -v pacman >/dev/null 2>&1; then
        echo "--> Detected Arch Linux / CachyOS / Manjaro."
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
        echo "--> Detected Ubuntu / Debian / Linux Mint."
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
        echo "--> Detected Fedora / RHEL."
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
        echo "[!] Package manager not recognized. Please install Python, GTK4, Libadwaita, and GStreamer packages manually."
    fi
}

install_packages

# 2. System CLI command
echo "[2/4] Setting up system command (/usr/local/bin/ramordcast)..."
LAUNCHER_PATH="/usr/local/bin/ramordcast"
sudo bash -c "cat << 'EOF' > $LAUNCHER_PATH
#!/usr/bin/env bash
python3 \"$SCRIPT_DIR/main.py\" \"\$@\"
EOF"
sudo chmod +x "$LAUNCHER_PATH"

# 3. Desktop Application Shortcut
echo "[3/4] Creating desktop application shortcut..."
APPLICATIONS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPLICATIONS_DIR"

cat << EOF > "$APPLICATIONS_DIR/com.ramord.cast.desktop"
[Desktop Entry]
Name=Ramord Cast
Comment=Ultra Low-Latency Samsung & Tizen Screen Mirror
Comment[en]=Ultra Low-Latency Samsung & Tizen Screen Mirror
Comment[tr]=Ultra Düşük Gecikmeli Samsung & Tizen Ekran Yansıtıcı
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

# 4. Hardware and driver compatibility check
echo "[4/4] Checking hardware compatibility..."
if lspci | grep -qi "RTL8822CE\|RTL8821CE"; then
    echo ""
    echo "[!] Realtek Wi-Fi chipset detected."
    echo "    Linux Wi-Fi Direct (P2P) patch may be required for Miracast."
    echo "    To install: sudo bash $SCRIPT_DIR/driver/install_driver.sh"
fi

echo ""
echo "=========================================================="
echo " INSTALLATION COMPLETED SUCCESSFULLY!                     "
echo "=========================================================="
echo " To start Ramord Cast:"
echo "   1) Launch 'Ramord Cast' from your application menu,"
echo "   2) Or type 'ramordcast' in your terminal."
echo "=========================================================="
