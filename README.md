# Ramord Cast

Ultra-low latency wireless screen mirroring for Smart TVs, monitors, and wireless displays on Linux.

---

## Supported Connection Protocols

1. **Apple AirPlay 2 (Recommended & Default):**
   - Zero-PIN connection with saved credentials.
   - Hardware-accelerated 60 FPS streaming with sub-25ms ultra-low latency.
   - Dynamic bitrate adjustment and color fidelity.
2. **Google Cast / Chromecast (Fallback):**
   - Standard Google Cast protocol for TV and wireless sink devices.

---

## How to Run & Quick Installation

### 1. Automated Installation
Run the installer to set up dependencies, the `ramordcast` command, and application launcher:

```bash
git clone https://github.com/ramordcommunity/ramordcast.git
cd ramordcast
bash install.sh
```

### 2. Launching the App
Launch Ramord Cast in either of two ways:
- **Terminal:** Type `ramordcast` or run `python3 main.py` inside the project folder.
- **Application Launcher:** Open your desktop menu (GNOME, KDE Plasma, etc.) and click **Ramord Cast**.

### 3. How to Mirror Your Screen (Step-by-Step)
1. Make sure your Linux PC and your TV / Monitor are connected to the same Wi-Fi / local network.
2. Open **Ramord Cast**.
3. Select your protocol (Apple AirPlay 2 is selected by default).
4. Choose your target TV or monitor from the automatically scanned list.
5. Click **Start Cast**.
6. To end screen sharing, click **Stop Cast**.

---

## Dependencies (Installed Automatically)

If you prefer to install dependencies manually:

### Arch Linux / CachyOS / Manjaro:
```bash
sudo pacman -S --needed python python-gobject python-requests gtk4 libadwaita pipewire
```

### Ubuntu / Debian / Linux Mint:
```bash
sudo apt update
sudo apt install -y python3 python3-gi python3-requests gir1.2-gtk-4.0 gir1.2-adw-1 pipewire
```

### Fedora:
```bash
sudo dnf install -y python3 python3-gobject python3-requests gtk4 libadwaita pipewire
```

---

## License

GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](LICENSE) file for details. Free and open source software; anyone is free to use, study, modify, and distribute this software.
