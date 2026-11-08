# -*- coding: utf-8 -*-
"""
Ramord Cast Streaming Engine
- Apple AirPlay 2 (Hardware-accelerated 60 FPS, ultra low-latency)
- Google Cast / Chromecast (Standard wireless display)
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
        self.cast_process = None
        self.current_target = None
        self.is_streaming = False
        self.current_protocol = "airplay"

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

    def start_cast(self, target_ip, name="Google Cast"):
        """Starts Google Cast / Chromecast wireless streaming."""
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

    def start_stream(self, target_device, protocol="airplay", mode="clone",
                     fps=30, latency_ms=0, bitrate_kbps=0, codec="auto"):
        target_ip = target_device.ip if hasattr(target_device, 'ip') else str(target_device)
        name = target_device.name if hasattr(target_device, 'name') else "Device"

        if protocol == "cast":
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

    def stop_stream(self):
        self.stop_airplay()
        self.stop_cast()
        self.is_streaming = False
        self.current_target = None
        if self.on_status_change:
            self.on_status_change(False, None)
