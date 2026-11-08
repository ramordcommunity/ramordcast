# -*- coding: utf-8 -*-
"""
Ramord Cast Cihaz Keşif Modülü (Samsung SmartTV, AirPlay ve Google Cast mDNS Tarayıcı)
Önbellekleme, anında yükleme ve sıfır gecikmeli TXT ayrıştırma desteği.
"""

import subprocess
import urllib.request
import json
import threading
import time
import os
import re

CACHE_FILE = os.path.expanduser("~/.config/ramordcast/known_devices.json")

class DiscoveredDevice:
    def __init__(self, name, ip, port, dev_type="Samsung SmartTV", model="", wifi_mac=None):
        self.name = name
        self.ip = ip
        self.port = port
        self.dev_type = dev_type
        self.model = model
        self.wifi_mac = wifi_mac
        self.last_seen = time.time()

    def __repr__(self):
        return f"<Device {self.name} ({self.ip}:{self.port}) [{self.model}] MAC:{self.wifi_mac}>"


class DeviceScanner:
    def __init__(self, on_device_found=None):
        self.on_device_found = on_device_found
        self.devices = {}
        self.running = False
        self._thread = None
        self._enriched_ips = set()
        self._load_cache()

    def _load_cache(self):
        """Önceki oturumlardan kayıtlı cihazları anında belleğe yükler (0ms açılış)."""
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for item in data:
                    dev = DiscoveredDevice(
                        name=item.get("name", "Device"),
                        ip=item.get("ip"),
                        port=item.get("port", 7000),
                        model=item.get("model", ""),
                        wifi_mac=item.get("wifi_mac")
                    )
                    self.devices[dev.ip] = dev
        except Exception:
            pass

    def _save_cache(self):
        """Bulunan cihazları yerel yapılandırmaya mühürler."""
        try:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            data = []
            for dev in self.devices.values():
                data.append({
                    "name": dev.name,
                    "ip": dev.ip,
                    "port": dev.port,
                    "model": dev.model,
                    "wifi_mac": dev.wifi_mac
                })
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_cached_devices(self):
        return list(self.devices.values())

    def start_scanning(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._scan_loop, daemon=True)
            self._thread.start()

    def stop_scanning(self):
        self.running = False

    def _query_samsung_info(self, ip):
        """Samsung SmartView port 8001'den detaylı cihaz bilgilerini çeker."""
        try:
            url = f"http://{ip}:8001/api/v2/"
            req = urllib.request.Request(url, headers={"User-Agent": "RamordCast/1.0"})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                device = data.get("device", {})
                name = device.get("name", "Samsung Smart TV")
                model = device.get("modelName", device.get("model", "Tizen"))
                wifi_mac = device.get("wifiMac", None)
                return name, model, wifi_mac
        except Exception:
            return None, None, None

    def scan_once(self):
        """Avahi-browse üzerinden AirPlay ve Cast servislerini tek geçişte hızlıca tarar."""
        services = ['_airplay._tcp', '_googlecast._tcp']
        found_any = False
        for svc in services:
            try:
                cmd = ['avahi-browse', '-rpt', svc]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=2)
                for line in res.stdout.splitlines():
                    if line.startswith('='):
                        parts = line.split(';')
                        if len(parts) >= 9:
                            ip = parts[7]
                            port = int(parts[8])
                            if ":" in ip:
                                continue

                            raw_name = parts[3]
                            name = raw_name.replace("\\032", " ").replace("\\047", "'")

                            model_match = re.search(r'\"(?:model|md)=([^\"]+)\"', line)
                            model = model_match.group(1) if model_match else ("AirPlay Device" if "airplay" in svc else "Cast Device")

                            mac_match = re.search(r'\"(?:deviceid|id)=([^\"]+)\"', line)
                            wifi_mac = mac_match.group(1) if mac_match else None

                            dev = DiscoveredDevice(name=name, ip=ip, port=port, model=model, wifi_mac=wifi_mac)
                            self.devices[ip] = dev
                            found_any = True
                            if self.on_device_found:
                                self.on_device_found(dev)

                            # Samsung için port 8001 sorgusu: her IP için sadece BİR kez yapılır
                            if ("samsung" in line.lower() or "samsung" in name.lower()) and ip not in self._enriched_ips:
                                self._enriched_ips.add(ip)
                                threading.Thread(target=self._async_enrich_samsung, args=(ip, dev), daemon=True).start()
            except Exception:
                pass

        if found_any:
            self._save_cache()

        return list(self.devices.values())

    def _async_enrich_samsung(self, ip, dev):
        name, model, wifi_mac = self._query_samsung_info(ip)
        if name and (name != dev.name or model != dev.model):
            dev.name = name
            if model:
                dev.model = model
            if wifi_mac:
                dev.wifi_mac = wifi_mac
            if self.on_device_found:
                self.on_device_found(dev)
            self._save_cache()

    def _scan_loop(self):
        while self.running:
            self.scan_once()
            time.sleep(8)
