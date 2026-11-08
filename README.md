# Ramord Cast

Ultra-low latency wireless screen mirroring and second-monitor tool for Samsung Tizen Smart TVs, Smart Monitors, and AirPlay displays on Linux.

---

## How to Run & Quick Installation

### 1. Automated Installation
Run the installer to set up all system dependencies, the `ramordcast` command, and application launcher:

```bash
git clone https://github.com/ramordcommunity/ramordcast.git
cd ramordcast
bash install.sh
```

### 2. Launching the App
After installation, you can launch Ramord Cast in either of two ways:
- **Terminal:** Type `ramordcast` or run `python3 main.py` inside the project folder.
- **Application Launcher:** Open your desktop menu (GNOME, KDE Plasma, etc.) and click **Ramord Cast**.

### 3. How to Mirror Your Screen (Step-by-Step)
1. Make sure your Linux PC and your Samsung TV / Monitor are on the same Wi-Fi / LAN network.
2. Launch **Ramord Cast**.
3. **Apple AirPlay 2** is selected as the default protocol (providing 60 FPS hardware-accelerated streaming and sub-25ms latency).
4. Select your target TV or monitor from the discovered devices list (or let the auto-discovery select it).
5. Click **Start Cast**.
6. To stop sharing at any time, click **Stop Cast**.

---

## Features

- **Apple AirPlay 2 (Default):** Zero-PIN hardware-accelerated 60 FPS streaming with sub-25ms latency.
- **Samsung Workspace (PC on TV / RDP):** Virtual display and keyboard/mouse integration over TLS RDP.
- **Wi-Fi Direct / Miracast (WFD):** Hardware P2P display transmission.
- **Hardware Acceleration:** Native VA-API / Vulkan hardware encoding (AMD Radeon, Intel QuickSync, NVIDIA NVENC) for smooth 60 FPS playback.
- **Flexible Display Modes:**
  - Clone Display (Mirroring)
  - Extend Display (Independent secondary display)
  - Single Window Mirroring
- **Multi-Monitor Alignment:** Directional placement (Right, Left, Above, Below) dynamically handled via Wayland/KScreen.
- **Multi-Language Interface (6 Languages):**
  - English (`en`) - Default
  - Turkish (`tr`)
  - German (`de`)
  - Spanish (`es`)
  - French (`fr`)
  - Italian (`it`)

---

## Manual Package Installation

If you prefer to install dependencies manually:

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

GNU General Public License v3.0 (GPL-3.0). See the [LICENSE](LICENSE) file for details. Free and open source software; anyone is free to use, modify, study, and distribute this software.
