# Ramord Cast 🖥️📡

**Ultra-Low Latency Screen Mirroring & Dual-Display Solution for Samsung Tizen Smart TVs & Monitors on Linux.**

*Linux için Ultra Düşük Gecikmeli Samsung ve Tizen OS Ekran Yansıtma ve İkinci Ekran Aracı.*

---

## 🚀 Features / Özellikler

- **Samsung Tizen Native Integration:** Designed and optimized specifically for Samsung Tizen OS Smart Monitors (e.g., M7 / LS43DM702, M8, Neo QLED, Smart TVs).
- **Multiple Protocols Supported:**
  - 🍏 **Apple AirPlay 2:** Zero-PIN saved-credentials, hardware-accelerated 60 FPS, sub-25ms latency.
  - 📶 **Wi-Fi Direct / Miracast (WFD):** Hardware P2P display transmission with custom PC and Samsung Galaxy identity configurations.
  - 🖥️ **Samsung Workspace (RDP / PC on TV):** Virtual screen, keyboard, and mouse integration via TLS RDP.
- **Hardware Acceleration:** Native VA-API / Vulkan hardware encoding support (AMD Radeon, Intel QuickSync) for buttery-smooth 60 FPS uncompressed streaming.
- **Flexible Display Modes:**
  - Clone Display (Yansıtma / Aynalama)
  - Extend Display (Bağımsız İkinci Ekran)
  - Single Window Mirroring (Tek Pencere)
- **Automatic Multi-Monitor Alignment:** Directional placement (Right, Left, Above, Below) dynamically handled by Wayland/KScreen.
- **Realtek Wi-Fi Direct (P2P) DKMS Drivers:** Includes patched and DKMS-automated `rtw88` drivers for Realtek RTL8822CE/RTL8821CE Linux chipsets.
- **6 Languages Built-in (Çoklu Dil Desteği):**
  - 🇹🇷 Türkçe (`tr`)
  - 🇬🇧 English (`en`)
  - 🇩🇪 Deutsch (`de`)
  - 🇪🇸 Español (`es`)
  - 🇫🇷 Français (`fr`)
  - 🇮🇹 Italiano (`it`)

---

## 📦 Installation & Requirements / Kurulum

### Prerequisites (Arch / CachyOS / Fedora / Ubuntu):
```bash
# Arch / CachyOS
sudo pacman -S python-gobject gtk4 libadwaita pipewire gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly dkms
```

### Running Ramord Cast:
```bash
python3 main.py
```

### Realtek RTL8822CE P2P Driver Installation (DKMS):
If you have a Realtek wireless card without Wi-Fi Direct support on Linux:
```bash
sudo bash driver/install_driver.sh
```

---

## 📄 License

GPL-3.0 License.
