# Ramord Cast 🖥️📡

**Ultra-Low Latency Screen Mirroring & Dual-Display Solution for Samsung Tizen Smart TVs & Monitors on Linux.**

*Linux için Ultra Düşük Gecikmeli Samsung ve Tizen OS Ekran Yansıtma ve İkinci Ekran Aracı.*

---

## ⚡ Hızlı Kurulum / Quick Installation (Tek Komut)

Herhangi bir Linux dağıtımında (Arch, CachyOS, Ubuntu, Debian, Fedora, Mint) Ramord Cast'i tüm bağımlılıkları ve masaüstü kısayoluyla birlikte tek komutla kurabilirsiniz:

```bash
git clone https://github.com/ramordcommunity/RamordCast.git
cd RamordCast
bash install.sh
```

Kurulum tamamlandıktan sonra:
- **Başlat Menüsünden:** `Ramord Cast` simgesine tıklayarak açabilirsiniz.
- **Terminalden:** Doğrudan `ramordcast` yazarak başlatabilirsiniz.

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

## 🛠️ Manuel Paket Kurulumu / Manual Package Requirements

Eğer paketleri kendi paket yöneticinizle manuel kurmak isterseniz:

### Arch Linux / CachyOS / Manjaro:
```bash
sudo pacman -S --needed python python-gobject python-requests gtk4 libadwaita pipewire gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugins-ugly dkms
```

### Ubuntu / Debian / Linux Mint:
```bash
sudo apt update
sudo apt install -y python3 python3-gi python3-gi-cairo python3-requests gir1.2-gtk-4.0 gir1.2-adw-1 pipewire gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly dkms
```

### Fedora:
```bash
sudo dnf install -y python3 python3-gobject python3-requests gtk4 libadwaita pipewire gstreamer1-plugins-base gstreamer1-plugins-good gstreamer1-plugins-bad-free gstreamer1-plugins-ugly-free dkms
```

---

## 📶 Realtek Wi-Fi Direct Sürücü Yaması (İsteğe Bağlı)

Eğer bilgisayarınızda Realtek RTL8822CE veya RTL8821CE kablosuz kartı varsa ve Linux çekirdeği Wi-Fi Direct (P2P) özelliğini açmıyorsa, paket içindeki otomatik DKMS yükleyicisini çalıştırabilirsiniz:

```bash
sudo bash driver/install_driver.sh
```

---

## 📄 License

GPL-3.0 License.
