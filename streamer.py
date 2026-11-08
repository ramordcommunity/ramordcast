# -*- coding: utf-8 -*-
"""
Ramord Cast Streaming & Display Engine
- Apple AirPlay 2 (Zero-latency hardware mirror)
- Samsung Workspace / PC on TV (Virtual Second Display over RDP, credentials & mouse/keyboard)
- Google Cast / Chromecast (Fallback)
"""

import subprocess
import urllib.parse
import os
import signal
import socket
import shutil
import time

class CastStreamer:
    def __init__(self, on_status_change=None):
        self.on_status_change = on_status_change
        self.airplay_process = None
        self.workspace_process = None
        self.cast_process = None
        self.current_target = None
        self.is_streaming = False
        self.current_protocol = "airplay"

    @staticmethod
    def get_local_ip(target_ip='192.168.1.204'):
        """Finds local IP seen by the network/monitor."""
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
        return os.environ.get("USER", "ramord")

    @staticmethod
    def get_current_password():
        return "1234"

    def ensure_krdp_certificates(self):
        """Generates self-signed TLS certificates for krdpserver if missing."""
        cert_dir = os.path.expanduser("~/.config/krdp")
        cert_file = os.path.join(cert_dir, "cert.pem")
        key_file = os.path.join(cert_dir, "key.pem")
        if not (os.path.exists(cert_file) and os.path.exists(key_file)):
            os.makedirs(cert_dir, exist_ok=True)
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                '-keyout', key_file, '-out', cert_file, '-days', '3650',
                '-subj', '/CN=RamordCast'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return cert_file, key_file

    def start_workspace(self, mode="extend", port=3389, username=None, password=None):
        """Starts Samsung Workspace / PC on TV (krdpserver) supporting independent virtual display."""
        if password is None:
            password = self.get_current_password()
        if username is None:
            username = self.get_current_user()
        if self.is_streaming:
            self.stop_stream()

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
            self.workspace_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            self.is_streaming = True
            self.current_protocol = "workspace"
            if self.on_status_change:
                self.on_status_change(True, "workspace")
            return True
        except Exception:
            self.is_streaming = False
            return False

    def stop_workspace(self):
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

    def start_airplay(self, target_ip, fps=30, latency_ms=0, bitrate_kbps=0, codec="auto", hwaccel="auto"):
        """Starts high-performance Apple AirPlay 2 stream."""
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

    def start_cast(self, target_ip, name="Google Cast"):
        if self.is_streaming:
            self.stop_stream()

        env = os.environ.copy()
        env['DISPLAY'] = os.environ.get('DISPLAY', ':0')
        env['WAYLAND_DISPLAY'] = os.environ.get('WAYLAND_DISPLAY', 'wayland-1')
        env['XDG_RUNTIME_DIR'] = os.environ.get('XDG_RUNTIME_DIR', f"/run/user/{os.getuid()}")

        try:
            self.cast_process = subprocess.Popen(
                ['gnome-network-displays'],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.is_streaming = True
            self.current_protocol = "cast"
            if self.on_status_change:
                self.on_status_change(True, "cast")
            return True
        except Exception:
            self.is_streaming = False
            return False

    def stop_cast(self):
        if self.cast_process:
            try:
                self.cast_process.terminate()
                self.cast_process.wait(timeout=1)
            except Exception:
                try:
                    self.cast_process.kill()
                except Exception:
                    pass
            self.cast_process = None

        try:
            subprocess.run(['killall', '-9', 'gnome-network-displays'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass

    def start_stream(self, target_device, protocol="airplay", mode="clone",
                     fps=30, latency_ms=0, bitrate_kbps=0, codec="auto"):
        target_ip = target_device.ip if hasattr(target_device, 'ip') else str(target_device)
        name = target_device.name if hasattr(target_device, 'name') else "Device"

        if protocol == "workspace":
            return self.start_workspace(mode=mode)
        elif protocol == "cast":
            return self.start_cast(target_ip, name=name)
        else:
            return self.start_airplay(
                target_ip,
                fps=fps,
                latency_ms=latency_ms,
                bitrate_kbps=bitrate_kbps,
                codec=codec,
                hwaccel="auto"
            )

    def stop_stream(self):
        self.stop_airplay()
        self.stop_workspace()
        self.stop_cast()
        self.is_streaming = False
        self.current_target = None
        if self.on_status_change:
            self.on_status_change(False, None)
