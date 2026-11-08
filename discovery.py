# -*- coding: utf-8 -*-
"""
Ramord Cast Cihaz Keşif Modülü (Samsung SmartTV, AirPlay ve Google Cast mDNS Tarayıcı)
"""

import subprocess
import urllib.request
import json
import threading
import time

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

    def start_scanning(self):
        self.running = True
        self._thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._thread.start()

    def stop_scanning(self):
        self.running = False

    def _query_samsung_info(self, ip):
        """Samsung SmartView port 8001'den cihaz modelini ve detaylarını çeker."""
        try:
            url = f"http://{ip}:8001/api/v2/"
            req = urllib.request.Request(url, headers={"User-Agent": "RamordCast/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                device = data.get("device", {})
                name = device.get("name", "Samsung Smart TV")
                model = device.get("modelName", device.get("model", "Tizen"))
                wifi_mac = device.get("wifiMac", None)
                return name, model, wifi_mac
        except Exception:
            return None, None, None

    def scan_once(self):
        """Avahi-browse üzerinden Google Cast ve AirPlay servislerini tarar."""
        # 1. Google Cast & AirPlay servislerini tara
        services = ['_googlecast._tcp', '_airplay._tcp']
        for svc in services:
            try:
                cmd = ['avahi-browse', '-rpt', svc]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=3)
                for line in res.stdout.splitlines():
                    if line.startswith('='):
                        parts = line.split(';')
                        if len(parts) >= 9:
                            ip = parts[7]
                            port = int(parts[8])
                            if ":" in ip: # IPv6 adreslerini atla
                                continue
                            
                            # Cihaz bilgilerini zenginleştir
                            name, model, wifi_mac = self._query_samsung_info(ip)
                            if not name:
                                raw_name = parts[3]
                                name = raw_name.replace("\\032", " ").replace("\\047", "'")
                                model = "AirPlay Device" if "airplay" in svc else "Chromecast / Cast"
                                wifi_mac = None

                            dev = DiscoveredDevice(name=name, ip=ip, port=port, model=model, wifi_mac=wifi_mac)
                            self.devices[ip] = dev
                            if self.on_device_found:
                                self.on_device_found(dev)
            except Exception:
                pass

        return list(self.devices.values())

    def _scan_loop(self):
        while self.running:
            self.scan_once()
            time.sleep(5)
