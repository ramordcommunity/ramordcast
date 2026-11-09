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
        sudo -A pacman -S --needed --noconfirm \
            python \
            python-gobject \
            python-requests \
            gtk4 \
            libadwaita \
            pipewire
    elif command -v apt-get >/dev/null 2>&1; then
        echo "--> Detected Ubuntu / Debian / Linux Mint."
        sudo -A apt-get update
        sudo -A apt-get install -y \
            python3 \
            python3-gi \
            python3-requests \
            gir1.2-gtk-4.0 \
            gir1.2-adw-1 \
            pipewire
    elif command -v dnf >/dev/null 2>&1; then
        echo "--> Detected Fedora / RHEL."
        sudo -A dnf install -y \
            python3 \
            python3-gobject \
            python3-requests \
            gtk4 \
            libadwaita \
            pipewire
    else
        echo "[!] Package manager not recognized. Please install Python, GTK4, Libadwaita, and PipeWire manually."
    fi
}

install_packages

# 2. System CLI command
echo "[2/4] Setting up system command (ramordcast)..."
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
cat << EOF > "$BIN_DIR/ramordcast"
#!/usr/bin/env bash
exec python3 "$SCRIPT_DIR/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/ramordcast"

# Try installing to /usr/local/bin if running as root or sudo available
if [ "$EUID" -eq 0 ]; then
    cp "$BIN_DIR/ramordcast" /usr/local/bin/ramordcast
elif sudo -n true 2>/dev/null; then
    sudo cp "$BIN_DIR/ramordcast" /usr/local/bin/ramordcast 2>/dev/null || true
fi

# 3. Universal Icon Deployment across all themes & resolutions
echo "[3/4] Installing application icon to all user themes..."
ICON_DIR="$HOME/.local/share/icons"
CAST_ICON="$SCRIPT_DIR/assets/ramordcast.png"

# Standard hicolor scalable & pngs
mkdir -p "$ICON_DIR/hicolor/scalable/apps" "$ICON_DIR/hicolor/256x256/apps"
cp -f "$CAST_ICON" "$ICON_DIR/hicolor/scalable/apps/ramordcast.png"
cp -f "$CAST_ICON" "$ICON_DIR/hicolor/256x256/apps/ramordcast.png"

# Deploy to all theme trees
if [ -d "$ICON_DIR" ]; then
    for tdir in "$ICON_DIR"/*; do
        if [ -d "$tdir" ]; then
            for app_dir in $(find "$tdir" -type d -name "apps" 2>/dev/null); do
                cp -f "$CAST_ICON" "$app_dir/ramordcast.png" 2>/dev/null || true
            done
            if command -v gtk-update-icon-cache >/dev/null 2>&1; then
                gtk-update-icon-cache -f -t "$tdir" >/dev/null 2>&1 || true
            fi
        fi
    done
fi

mkdir -p "$HOME/.local/share/pixmaps"
cp -f "$CAST_ICON" "$HOME/.local/share/pixmaps/ramordcast.png"

# 4. Desktop Application Shortcut
echo "[4/4] Creating desktop application shortcut..."
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
Icon=ramordcast
Terminal=false
Type=Application
Categories=AudioVideo;Video;Network;Utility;
Keywords=cast;mirror;samsung;tizen;display;screen;
StartupNotify=true
StartupWMClass=com.ramord.cast
EOF

chmod +x "$APPLICATIONS_DIR/com.ramord.cast.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
fi

if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo ""
echo "=========================================================="
echo " INSTALLATION COMPLETED SUCCESSFULLY!                     "
echo "=========================================================="
echo " To start Ramord Cast:"
echo "   1) Launch 'Ramord Cast' from your application menu,"
echo "   2) Or type 'ramordcast' in your terminal."
echo "=========================================================="
