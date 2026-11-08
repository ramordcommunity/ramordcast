# Ramord Cast

Ultra-low latency screen mirroring and dual-display solution for Samsung Tizen Smart TVs and monitors on Linux.

---

## Quick Installation (Single Command)

On any modern Linux distribution (Arch, CachyOS, Ubuntu, Debian, Fedora, Mint), install Ramord Cast along with its system dependencies and desktop launcher using the automated installer:

```bash
git clone https://github.com/ramordcommunity/ramordcast.git
cd ramordcast
bash install.sh
```

After installation completes:
- **Application Menu:** Launch `Ramord Cast` directly from your desktop application launcher.
- **Terminal:** Run `ramordcast` from anywhere.

---

## Features

- **Samsung Tizen Native Integration:** Optimized for Samsung Tizen OS Smart Monitors (e.g., M7 / LS43DM702, M8, Neo QLED, Smart TVs).
- **Multiple Protocols Supported:**
  - **Apple AirPlay 2:** Zero-PIN saved-credentials, hardware-accelerated 60 FPS, sub-25ms latency.
  - **Wi-Fi Direct / Miracast (WFD):** Hardware P2P display transmission with custom PC and Samsung Galaxy identity configurations.
  - **Samsung Workspace (RDP / PC on TV):** Virtual display, keyboard, and mouse integration via TLS RDP.
- **Hardware Acceleration:** Native VA-API / Vulkan hardware encoding (AMD Radeon, Intel QuickSync) for smooth 60 FPS streaming.
- **Flexible Display Modes:**
  - Clone Display (Mirroring)
  - Extend Display (Independent secondary display)
  - Single Window Mirroring
- **Automatic Multi-Monitor Alignment:** Directional placement (Right, Left, Above, Below) dynamically handled via Wayland/KScreen.
- **Multi-Language Interface (6 Languages):**
  - English (`en`) - Default
  - Turkish (`tr`)
  - German (`de`)
  - Spanish (`es`)
  - French (`fr`)
  - Italian (`it`)

---

## Manual Package Installation

If you prefer to install dependencies manually using your distribution package manager:

### Arch Linux / CachyOS / Manjaro:
```bash
sudo pacman -S --needed python python-gobject python-requests gtk4 libadwaita pipewire gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly
```

### Ubuntu / Debian / Linux Mint:
```bash
sudo apt update
sudo apt install -y python3 python3-gi python3-gi-cairo python3-requests gir1.2-gtk-4.0 gir1.2-adw-1 pipewire gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
```

### Fedora:
```bash
sudo dnf install -y python3 python3-gobject python3-requests gtk4 libadwaita pipewire gstreamer1-plugins-base gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-ugly-free
```

---

## License

GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](LICENSE) file for details.
