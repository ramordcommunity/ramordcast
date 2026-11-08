# Ramord Cast

Ultra-low latency wireless screen mirroring and wireless virtual second-display tool for Smart TVs, monitors, and Linux.

---

## Supported Connection Protocols

1. **Apple AirPlay 2 (Recommended & Default):**
   - Zero-PIN connection with saved credentials.
   - Hardware-accelerated 60 FPS streaming with sub-25ms ultra-low latency.
   - Dynamic bitrate adjustment and color fidelity.
2. **Samsung Workspace (PC on TV / Independent 2nd Display):**
   - Virtual second screen (`1920x1080`) created independently over network RDP.
   - Directional placement: Place your 2nd screen to the **Right**, **Left**, **Above**, or **Below** your main monitor.
   - Direct mouse and keyboard control on Samsung Smart TV / Monitor without cables.
   - Real-time connection details displayed (IP, Username, Password, Port: 3389).
3. **Google Cast / Chromecast (Fallback):**
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

### 3. How to Use (Step-by-Step)

#### Option A: Apple AirPlay 2 (Instant Mirroring)
1. Ensure your PC and TV are connected to the same Wi-Fi / local network.
2. Select **Apple AirPlay 2**.
3. Choose your TV from the scanned list and click **Start Cast**.

#### Option B: Samsung Workspace (Independent 2nd Screen with Credentials)
1. Select **Samsung Workspace (PC on TV / 2nd Display)**.
2. Choose **Extend (Independent 2nd Display)** and choose its position (**Right**, **Left**, **Above**, or **Below**).
3. Click **Start Cast**.
4. On your Samsung TV / Monitor: Go to **Menu > Connected Devices > Workspace > Windows PC**.
5. Enter the **IP Address**, **Username**, and **Password** shown on the Ramord Cast screen and connect!

---

## Dependencies (Installed Automatically)

If you prefer to install dependencies manually:

### Arch Linux / CachyOS / Manjaro:
```bash
sudo pacman -S --needed python python-gobject python-requests gtk4 libadwaita pipewire krdp
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
