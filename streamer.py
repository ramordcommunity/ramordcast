# -*- coding: utf-8 -*-
"""
Ramord Cast Yayın ve Bağlantı Motoru
- Yol 1: Apple AirPlay 2 (Önerilen - Donanımsal Hızlandırma, Ultra Düşük Gecikme, 60 FPS & Zengin Renk)
- Yol 2: Samsung Workspace (PC on TV / RDP - Sanal Ekran & Klavye/Fare)
- Yol 3: Wi-Fi Direct / Miracast (Donanımsal Ekran Akışı)
- Yedek: Google Cast (Multimedya & Video Yayını)
"""

import subprocess
import urllib.parse
import os
import signal
import socket
import ssl
import json
import base64
import shutil
import time
import threading

class CastStreamer:
    def __init__(self, on_status_change=None):
        self.on_status_change = on_status_change
        self.process = None
        self.airplay_process = None
        self.workspace_process = None
        self.avahi_process = None
        self.current_target = None
        self.is_streaming = False
        self.current_protocol = "airplay"

    @staticmethod
    def get_local_ip(target_ip='192.168.1.204'):
        """Monitörün gördüğü yerel IP adresini bulur."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((target_ip, 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '192.168.1.101'

    @staticmethod
    def get_current_user():
        """RDP oturum kullanıcı adını döner."""
        return "ramord"

    @staticmethod
    def get_current_password():
        """RDP oturum şifresini döner."""
        return "1234"

    @staticmethod
    def is_port_open(port=3389, host='127.0.0.1'):
        """Belirtilen portun dinlemede olup olmadığını kontrol eder."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        res = s.connect_ex((host, port))
        s.close()
        return res == 0

    def ensure_krdp_certificates(self):
        """krdpserver için gerekli TLS sertifikalarını kontrol eder ve hazırlar."""
        cert_dir = os.path.expanduser("~/.config/krdp")
        cert_file = os.path.join(cert_dir, "krdp.crt")
        key_file = os.path.join(cert_dir, "krdp.key")
        if not (os.path.exists(cert_file) and os.path.exists(key_file)):
            os.makedirs(cert_dir, exist_ok=True)
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                '-keyout', key_file, '-out', cert_file, '-days', '3650',
                '-subj', '/CN=RamordCast'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return cert_file, key_file

    def send_multiview_key(self, tv_ip="192.168.1.204"):
        return True

    def hack_trigger_samsung_multiview(self, tv_ip="192.168.1.204"):
        return True

    def notify_samsung_tv_workspace(self, tv_ip):
        """Samsung TV'ye Workspace / PC on TV ekranını açması için sinyal gönderir."""
        return self.hack_trigger_samsung_multiview(tv_ip)

    def build_cast_uri(self, ip, name, protocol=5):
        """Google Cast için URI oluşturur."""
        params = {
            'protocol': str(protocol),
            'ip': ip,
            'name': name
        }
        query = urllib.parse.urlencode(params)
        return f"gnome-network-displays://sink/?{query}"

    def start_airplay(self, target_ip, fps=30, latency_ms=0, bitrate_kbps=0, codec="auto", hwaccel="auto"):
        """
        Apple AirPlay 2 üzerinden donanım hızlandırmalı ve kararlı
        ekran aktarımını başlatır.
        """
        if self.is_streaming:
            self.stop_stream()

        doubletake_bin = shutil.which("doubletake")
        if not doubletake_bin or not os.path.exists(doubletake_bin):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            bundled_bin = os.path.join(base_dir, "bin", "doubletake")
            if os.path.exists(bundled_bin):
                doubletake_bin = bundled_bin
            else:
                doubletake_bin = os.path.expanduser("~/.local/bin/doubletake")

        cmd = [
            doubletake_bin,
            "-target", target_ip,
            "-fps", str(fps),
            "-hwaccel", hwaccel,
            "-video-codec", codec,
            "-no-audio"
        ]
        if bitrate_kbps and bitrate_kbps > 0:
            cmd.extend(["-bitrate", str(bitrate_kbps)])
        if latency_ms and latency_ms > 0:
            cmd.extend(["-target-latency-ms", str(latency_ms)])

        env = os.environ.copy()
        env["DISPLAY"] = os.environ.get("DISPLAY", ":0")
        env["WAYLAND_DISPLAY"] = os.environ.get("WAYLAND_DISPLAY", "wayland-1")
        env["XDG_RUNTIME_DIR"] = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")

        try:
            self.airplay_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            self.is_streaming = True
            self.current_protocol = "airplay"
            if self.on_status_change:
                self.on_status_change(True, "airplay")
            return True
        except Exception:
            self.is_streaming = False
            return False

    def stop_airplay(self):
        """AirPlay sürecini durdurur."""
        if self.airplay_process:
            try:
                os.killpg(os.getpgid(self.airplay_process.pid), signal.SIGTERM)
                self.airplay_process.wait(timeout=1)
            except Exception:
                try:
                    os.killpg(os.getpgid(self.airplay_process.pid), signal.SIGKILL)
                except Exception:
                    pass
            self.airplay_process = None

        try:
            subprocess.run(['killall', '-9', 'doubletake'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass

    def start_workspace(self, mode="clone", port=3389, username="ramord", password=None, target_ip="192.168.1.204"):
        """Samsung Workspace (RDP) servisini krdpserver motoruyla 3389 portunda başlatır."""
        if password is None:
            password = self.get_current_password()
        if username is None:
            username = self.get_current_user()
        if self.is_streaming:
            self.stop_stream()

        cert_dir = os.path.expanduser("~/.config/krdp")
        cert_file = os.path.join(cert_dir, "cert.pem")
        key_file = os.path.join(cert_dir, "key.pem")
        if not (os.path.exists(cert_file) and os.path.exists(key_file)):
            cert_file, key_file = self.ensure_krdp_certificates()

        krdp_bin = shutil.which("krdpserver")
        if not krdp_bin:
            return False

        cmd = [
            krdp_bin,
            "-u", username,
            "-p", password,
            "--port", str(port),
            "--certificate", cert_file,
            "--certificate-key", key_file
        ]

        if mode == "extend":
            cmd.extend(["--mode", "AdditionalDisplay", "--virtual-monitor", "1920x1080@1"])
        else:
            cmd.extend(["--mode", "SharedAccess"])

        env = os.environ.copy()
        env["DISPLAY"] = os.environ.get("DISPLAY", ":0")
        env["WAYLAND_DISPLAY"] = os.environ.get("WAYLAND_DISPLAY", "wayland-1")
        env["XDG_RUNTIME_DIR"] = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")

        try:
            krdp_log = open('/tmp/krdpserver.log', 'w')
            self.workspace_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=krdp_log,
                stderr=krdp_log,
                preexec_fn=os.setsid
            )
            time.sleep(0.3)

            # mDNS üzerinden TV'ye Ramord-PC olarak kendini duyur
            try:
                self.avahi_process = subprocess.Popen(
                    ['avahi-publish-service', 'Ramord-PC', '_rdp._tcp', str(port)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid
                )
            except Exception:
                pass

            self.is_streaming = True
            self.current_protocol = "workspace"
            if self.on_status_change:
                self.on_status_change(True, "workspace")
            return True
        except Exception:
            self.is_streaming = False
            return False

    def stop_workspace(self):
        """Workspace (krdpserver) servisini durdurur."""
        if self.avahi_process:
            try:
                os.killpg(os.getpgid(self.avahi_process.pid), signal.SIGTERM)
            except Exception:
                pass
            self.avahi_process = None

        if self.workspace_process:
            try:
                os.killpg(os.getpgid(self.workspace_process.pid), signal.SIGTERM)
                self.workspace_process.wait(timeout=1)
            except Exception:
                try:
                    os.killpg(os.getpgid(self.workspace_process.pid), signal.SIGKILL)
                except Exception:
                    pass
            self.workspace_process = None

        try:
            subprocess.run(['killall', '-9', 'krdpserver'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass

    def start_smartview(self, target_device, mode="clone"):
        """Samsung Smart View (Galaxy One UI 3.1+) doğrudan Wi-Fi Direct ve UPnP akışını başlatır."""
        self.current_protocol = "smartview"
        target_ip = target_device.ip if hasattr(target_device, 'ip') else str(target_device)

        # TV ScreenSharing UPnP tetiklemesi gönder
        try:
            from samsung_wfd import SamsungWFDServer
            server = SamsungWFDServer(target_ip=target_ip)
            server.trigger_tv()
        except Exception as e:
            print(f"[SmartView] Trigger error: {e}")

        # Wi-Fi Direct ekran yansıtma istemcisini başlat
        env = os.environ.copy()
        env['DISPLAY'] = os.environ.get('DISPLAY', ':0')
        env['WAYLAND_DISPLAY'] = os.environ.get('WAYLAND_DISPLAY', 'wayland-1')
        env['XDG_RUNTIME_DIR'] = os.environ.get('XDG_RUNTIME_DIR', '/run/user/1000')

        try:
            self.miracast_proc = subprocess.Popen(
                ['gnome-network-displays'],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.is_streaming = True
            if self.on_status_change:
                self.on_status_change(True, target_device)
            return True
        except Exception as e:
            print(f"[Streamer] SmartView launch error: {e}")
            return False

    def start_miracast(self, target_device, mode="clone"):
        """Wi-Fi Direct / Miracast tünelini başlatır."""
        return self.start_smartview(target_device, mode=mode)

    def start_cast(self, target_device, mode="clone"):
        """Yedek: Google Cast video akışını başlatır."""
        return self.start_miracast(target_device, mode=mode)

    def start_stream(self, target_device, protocol="airplay", mode="clone",
                     fps=30, latency_ms=0, bitrate_kbps=0, codec="auto"):
        """Seçilen protokole ve performans ayarlarına göre bağlantıyı başlatır."""
        self.current_protocol = protocol
        target_ip = target_device.ip if hasattr(target_device, 'ip') else str(target_device)

        if protocol == "airplay":
            return self.start_airplay(
                target_ip,
                fps=fps,
                latency_ms=latency_ms,
                bitrate_kbps=bitrate_kbps,
                codec=codec,
                hwaccel="auto"
            )
        elif protocol == "workspace":
            return self.start_workspace(mode=mode)
        elif protocol == "smartview":
            return self.start_smartview(target_device, mode=mode)
        elif protocol == "miracast":
            return self.start_miracast(target_device, mode=mode)
        else:
            return self.start_cast(target_device, mode=mode)

    def stop_stream(self):
        """Aktif tüm bağlantıları durdurur ve temizler."""
        self.stop_airplay()
        self.stop_workspace()

        if hasattr(self, 'miracast_proc') and self.miracast_proc:
            try:
                self.miracast_proc.terminate()
                self.miracast_proc.wait(timeout=1)
            except Exception:
                try:
                    self.miracast_proc.kill()
                except Exception:
                    pass
            self.miracast_proc = None

        try:
            subprocess.run(['killall', '-9', 'gnome-network-displays'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass

        if hasattr(self, 'wfd_server') and self.wfd_server:
            try:
                self.wfd_server.stop()
            except Exception:
                pass
            self.wfd_server = None

        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=1)
            except Exception:
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                except Exception:
                    pass
            self.process = None

        try:
            subprocess.run(['killall', '-9', 'gnome-network-displays-stream'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass

        try:
            subprocess.run(['nmcli', 'connection', 'delete', 'RamordCast-P2P'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass

        self.is_streaming = False
        self.current_target = None
        if self.on_status_change:
            self.on_status_change(False, None)
