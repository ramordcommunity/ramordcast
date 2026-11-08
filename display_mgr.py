# -*- coding: utf-8 -*-
"""
Ramord Cast Ekran ve Konumlandırma Yönetimi (kscreen-doctor ve KDE Plasma Wayland Entegrasyonu)
"""

import subprocess
import re

class DisplayManager:
    def __init__(self):
        pass

    def get_outputs(self):
        """Mevcut bağlı ve etkin ekranları listeler."""
        outputs = []
        try:
            res = subprocess.run(['kscreen-doctor', '-o'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=2)
            # Output: 1 eDP-1 d8ac840b-02e2-4b08-b085-2ac76fba249b enabled connected ... Geometry: 0,0 1920x1080
            current_output = None
            for line in res.stdout.splitlines():
                line = line.strip()
                if line.startswith("Output:"):
                    parts = line.split()
                    out_id = parts[1]
                    out_name = parts[2]
                    enabled = "enabled" in parts
                    connected = "connected" in parts
                    current_output = {
                        "id": out_id,
                        "name": out_name,
                        "enabled": enabled,
                        "connected": connected,
                        "geometry": (0, 0, 1920, 1080),
                        "width": 1920,
                        "height": 1080,
                        "x": 0,
                        "y": 0
                    }
                    outputs.append(current_output)
                elif current_output and line.startswith("Geometry:"):
                    geom = line.split()[1] # 0,0
                    res_str = line.split()[2] # 1920x1080
                    x, y = map(int, geom.split(","))
                    w, h = map(int, res_str.split("x"))
                    current_output["geometry"] = (x, y, w, h)
                    current_output["x"] = x
                    current_output["y"] = y
                    current_output["width"] = w
                    current_output["height"] = h
        except Exception:
            # Yedek varsayılan ana ekran
            outputs = [{"id": "1", "name": "eDP-1", "enabled": True, "connected": True, "x": 0, "y": 0, "width": 1920, "height": 1080}]

        return outputs

    def get_primary_display(self):
        outputs = self.get_outputs()
        for out in outputs:
            if out.get("enabled"):
                return out
        return outputs[0] if outputs else None

    def arrange_position(self, target_output_name, position="right"):
        """
        kscreen-doctor ile hedef ekranın ana ekrana göre konumunu ayarlar.
        position: 'right', 'left', 'top', 'bottom'
        """
        primary = self.get_primary_display()
        if not primary:
            return False

        pw = primary["width"]
        ph = primary["height"]
        px = primary["x"]
        py = primary["y"]

        # Varsayılan hedef çözünürlük 1920x1080
        tw = 1920
        th = 1080

        if position == "right":
            tx = px + pw
            ty = py
        elif position == "left":
            tx = px - tw
            ty = py
        elif position == "top":
            tx = px
            ty = py - th
        elif position == "bottom":
            tx = px
            ty = py + ph
        else:
            tx = px + pw
            ty = py

        cmd = [
            'kscreen-doctor',
            f'output.{target_output_name}.position.{tx},{ty}',
            f'output.{primary["name"]}.position.{px},{py}'
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            return True
        except Exception:
            return False
