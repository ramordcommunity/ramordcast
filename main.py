#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ramord Cast - Ultra-Low-Latency Display Mirroring & Wireless Casting for Samsung Tizen & Linux
(AirPlay 2, Samsung Workspace RDP, Miracast WFD, Google Cast, GTK4 + Libadwaita, Multi-Language Support)
"""

import sys
import os
import threading
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio, Gdk

from i18n import t, LANGUAGES
from discovery import DeviceScanner, DiscoveredDevice
from display_mgr import DisplayManager
from streamer import CastStreamer

class RamordCastWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Ramord Cast")
        self.set_default_size(760, 780)

        self.current_lang = "en"
        self.scanner = DeviceScanner(on_device_found=self._on_device_found_bg)
        self.display_mgr = DisplayManager()
        self.streamer = CastStreamer(on_status_change=self._on_stream_status_bg)

        self.discovered_devices = {}
        self.selected_device_ip = None

        self._build_ui()
        self._refresh_texts()

        # Otomatik cihaz taramasını başlat
        self.scanner.start_scanning()

    def _build_ui(self):
        # Ana dikey kutu
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header Bar
        self.header_bar = Adw.HeaderBar()
        main_box.append(self.header_bar)

        # Dil Menüsü
        lang_button = Gtk.MenuButton()
        lang_button.set_icon_name("preferences-desktop-locale-symbolic")
        lang_popover = Gtk.Popover()
        lang_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lang_box.set_margin_top(6)
        lang_box.set_margin_bottom(6)
        lang_box.set_margin_start(6)
        lang_box.set_margin_end(6)

        for code, name in LANGUAGES.items():
            btn = Gtk.Button(label=f"{name} ({code.upper()})")
            btn.connect("clicked", self._on_change_language, code, lang_popover)
            lang_box.append(btn)

        lang_popover.set_child(lang_box)
        lang_button.set_popover(lang_popover)
        self.header_bar.pack_end(lang_button)

        # Yenileme Butonu
        self.refresh_btn = Gtk.Button()
        self.refresh_btn.set_icon_name("view-refresh-symbolic")
        self.refresh_btn.connect("clicked", self._on_manual_refresh)
        self.header_bar.pack_start(self.refresh_btn)

        # Scrollable Sayfa
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        main_box.append(scrolled)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(720)
        clamp.set_tightening_threshold(580)
        scrolled.set_child(clamp)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content_box.set_margin_top(16)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)
        clamp.set_child(content_box)

        # 1. Durum Kartı
        self.status_banner = Adw.StatusPage()
        self.status_banner.set_icon_name("video-display-symbolic")
        content_box.append(self.status_banner)

        # 2. Bağlantı Teknolojisi Seçimi (AirPlay vs Workspace vs Miracast vs Cast)
        self.proto_group = Adw.PreferencesGroup()
        content_box.append(self.proto_group)

        self.proto_combo_row = Adw.ComboRow()
        self.proto_model = Gtk.StringList()
        self.proto_combo_row.set_model(self.proto_model)
        self.proto_combo_row.connect("notify::selected", self._on_proto_changed)
        self.proto_group.add(self.proto_combo_row)

        # 3. Performans, Renk ve Gecikme Ayarları Kartı
        self.perf_group = Adw.PreferencesGroup()
        content_box.append(self.perf_group)

        # FPS Seçimi (60 FPS vs 30 FPS)
        self.fps_row = Adw.ComboRow()
        self.fps_model = Gtk.StringList()
        self.fps_row.set_model(self.fps_model)
        self.perf_group.add(self.fps_row)

        # Renk ve Görüntü Kalitesi (Bitrate: 35 Mbps vs 25 Mbps vs 15 Mbps)
        self.quality_row = Adw.ComboRow()
        self.quality_model = Gtk.StringList()
        self.quality_row.set_model(self.quality_model)
        self.perf_group.add(self.quality_row)

        # Tepki Süresi Hedefi (15ms vs 30ms vs 50ms)
        self.latency_row = Adw.ComboRow()
        self.latency_model = Gtk.StringList()
        self.latency_row.set_model(self.latency_model)
        self.perf_group.add(self.latency_row)

        # Video & Renk Kodlayıcı (Auto vs H.264 vs HEVC)
        self.codec_row = Adw.ComboRow()
        self.codec_model = Gtk.StringList()
        self.codec_row.set_model(self.codec_model)
        self.perf_group.add(self.codec_row)

        # Donanım Hızlandırma Switch
        self.vaapi_switch_row = Adw.SwitchRow()
        self.vaapi_switch_row.set_active(True)
        self.perf_group.add(self.vaapi_switch_row)

        # 4. Samsung Workspace (PC on TV) Kartı
        self.workspace_group = Adw.PreferencesGroup()
        content_box.append(self.workspace_group)

        self.ws_guide_row = Adw.ActionRow()
        self.ws_guide_row.set_subtitle_lines(0)
        self.workspace_group.add(self.ws_guide_row)

        self.ws_ip_row = Adw.ActionRow()
        copy_ip_btn = Gtk.Button.new_from_icon_name("edit-copy-symbolic")
        copy_ip_btn.set_valign(Gtk.Align.CENTER)
        copy_ip_btn.connect("clicked", self._on_copy_ip)
        self.ws_ip_row.add_suffix(copy_ip_btn)
        self.workspace_group.add(self.ws_ip_row)

        self.ws_user_row = Adw.ActionRow()
        self.workspace_group.add(self.ws_user_row)

        self.ws_pass_row = Adw.ActionRow()
        self.workspace_group.add(self.ws_pass_row)

        self.ws_port_row = Adw.ActionRow()
        self.workspace_group.add(self.ws_port_row)

        self.notify_tv_btn = Gtk.Button()
        self.notify_tv_btn.add_css_class("pill")
        self.notify_tv_btn.set_halign(Gtk.Align.CENTER)
        self.notify_tv_btn.connect("clicked", self._on_notify_tv)
        self.workspace_group.add(self.notify_tv_btn)

        # 5. Yansıtma Modu (Klon vs İkinci Ekran)
        self.mode_group = Adw.PreferencesGroup()
        content_box.append(self.mode_group)

        self.mode_combo_row = Adw.ComboRow()
        self.mode_model = Gtk.StringList()
        self.mode_combo_row.set_model(self.mode_model)
        self.mode_combo_row.connect("notify::selected", self._on_mode_changed)
        self.mode_group.add(self.mode_combo_row)

        # 6. İkinci Ekran Konumu Grubu
        self.pos_group = Adw.PreferencesGroup()
        content_box.append(self.pos_group)

        self.pos_combo_row = Adw.ComboRow()
        self.pos_model = Gtk.StringList()
        self.pos_combo_row.set_model(self.pos_model)
        self.pos_combo_row.connect("notify::selected", self._on_position_changed)
        self.pos_group.add(self.pos_combo_row)

        # 7. Cihaz Seçim Grubu
        self.device_group = Adw.PreferencesGroup()
        content_box.append(self.device_group)

        self.device_list_box = Gtk.ListBox()
        self.device_list_box.add_css_class("boxed-list")
        self.device_list_box.connect("row-selected", self._on_device_selected)
        self.device_group.add(self.device_list_box)

        self.no_dev_row = Adw.ActionRow()
        self.device_list_box.append(self.no_dev_row)

        # 8. Eylem Butonu
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        content_box.append(btn_box)

        self.action_btn = Gtk.Button()
        self.action_btn.add_css_class("suggested-action")
        self.action_btn.add_css_class("pill")
        self.action_btn.set_size_request(240, 56)
        self.action_btn.connect("clicked", self._on_toggle_streaming)
        btn_box.append(self.action_btn)

        self.multiview_btn = Gtk.Button()
        self.multiview_btn.add_css_class("pill")
        self.multiview_btn.set_size_request(200, 56)
        self.multiview_btn.connect("clicked", self._on_toggle_multiview)
        btn_box.append(self.multiview_btn)

    def _refresh_texts(self):
        """Tüm arayüz metinlerini seçili 6 dilde eksiksiz yeniler."""
        lang = self.current_lang

        self.set_title(t("app_title", lang))
        self.status_banner.set_title(t("app_title", lang))

        # 0: Workspace (Önerilen), 1: Smart View (Galaxy), 2: Miracast (PC), 3: AirPlay
        curr_proto_idx = self.proto_combo_row.get_selected()
        is_workspace = (curr_proto_idx == 0)
        is_airplay = (curr_proto_idx == 3)

        if self.streamer.is_streaming:
            self.status_banner.set_description(t("status_connected", lang))
            self.action_btn.set_label(t("btn_stop", lang))
            self.action_btn.remove_css_class("suggested-action")
            self.action_btn.add_css_class("destructive-action")
        else:
            self.status_banner.set_description(t("status_ready", lang))
            self.action_btn.set_label(t("btn_start", lang))
            self.action_btn.remove_css_class("destructive-action")
            self.action_btn.add_css_class("suggested-action")

        self.refresh_btn.set_tooltip_text(t("btn_refresh", lang))
        self.multiview_btn.set_label(t("btn_multiview", lang))
        self.multiview_btn.set_tooltip_text(t("btn_multiview", lang))

        # Protokoller
        self.proto_group.set_title(t("section_connection_type", lang))
        self.proto_combo_row.set_title(t("section_connection_type", lang))
        while self.proto_model.get_n_items() > 0:
            self.proto_model.remove(0)
        self.proto_model.append(t("proto_workspace", lang))
        self.proto_model.append(t("proto_smartview", lang))
        self.proto_model.append(t("proto_miracast", lang))
        self.proto_model.append(t("proto_airplay", lang))
        self.proto_combo_row.set_selected(curr_proto_idx if curr_proto_idx < 4 else 0)

        # Performans & Renk Ayarları
        self.perf_group.set_title(t("section_performance", lang))

        self.fps_row.set_title(t("fps_label", lang))
        curr_fps = self.fps_row.get_selected()
        while self.fps_model.get_n_items() > 0:
            self.fps_model.remove(0)
        self.fps_model.append(t("fps_30", lang))
        self.fps_model.append(t("fps_60", lang))
        self.fps_row.set_selected(curr_fps if curr_fps < 2 else 0)

        self.quality_row.set_title(t("quality_label", lang))
        curr_q = self.quality_row.get_selected()
        while self.quality_model.get_n_items() > 0:
            self.quality_model.remove(0)
        self.quality_model.append(t("quality_auto", lang))
        self.quality_model.append(t("quality_high", lang))
        self.quality_model.append(t("quality_standard", lang))
        self.quality_row.set_selected(curr_q if curr_q < 3 else 0)

        self.latency_row.set_title(t("latency_target_label", lang))
        curr_lat = self.latency_row.get_selected()
        while self.latency_model.get_n_items() > 0:
            self.latency_model.remove(0)
        self.latency_model.append(t("latency_auto", lang))
        self.latency_model.append(t("latency_20ms", lang))
        self.latency_model.append(t("latency_40ms", lang))
        self.latency_row.set_selected(curr_lat if curr_lat < 3 else 0)

        self.codec_row.set_title(t("codec_label", lang))
        curr_codec = self.codec_row.get_selected()
        while self.codec_model.get_n_items() > 0:
            self.codec_model.remove(0)
        self.codec_model.append(t("codec_auto", lang))
        self.codec_model.append(t("codec_h264", lang))
        self.codec_model.append(t("codec_hevc", lang))
        self.codec_row.set_selected(curr_codec if curr_codec < 3 else 0)

        self.vaapi_switch_row.set_title(t("hardware_acceleration", lang))

        # Workspace Grubu
        self.workspace_group.set_title(t("workspace_info_title", lang))
        self.ws_guide_row.set_title(t("workspace_guide", lang))
        local_ip = self.streamer.get_local_ip()
        self.ws_ip_row.set_title(t("workspace_ip", lang))
        self.ws_ip_row.set_subtitle(local_ip)

        self.ws_user_row.set_title(t("workspace_user", lang))
        self.ws_user_row.set_subtitle(self.streamer.get_current_user())

        self.ws_pass_row.set_title(t("workspace_password", lang))
        self.ws_pass_row.set_subtitle(self.streamer.get_current_password())

        self.ws_port_row.set_title(t("workspace_port", lang))
        self.ws_port_row.set_subtitle("3389")

        self.notify_tv_btn.set_label(t("btn_notify_tv", lang))

        # Cihazlar
        self.device_group.set_title(t("section_targets", lang))
        self.no_dev_row.set_title(t("no_devices", lang))

        # Modlar
        self.mode_group.set_title(t("section_display_mode", lang))
        self.mode_combo_row.set_title(t("section_display_mode", lang))
        curr_mode = self.mode_combo_row.get_selected()
        while self.mode_model.get_n_items() > 0:
            self.mode_model.remove(0)
        self.mode_model.append(t("mode_clone", lang))
        self.mode_model.append(t("mode_extend", lang))
        self.mode_model.append(t("mode_window", lang))
        self.mode_combo_row.set_selected(curr_mode if curr_mode < 3 else 0)

        # Konumlar
        self.pos_group.set_title(t("section_position", lang))
        self.pos_combo_row.set_title(t("section_position", lang))
        curr_pos = self.pos_combo_row.get_selected()
        while self.pos_model.get_n_items() > 0:
            self.pos_model.remove(0)
        self.pos_model.append(t("pos_right", lang))
        self.pos_model.append(t("pos_left", lang))
        self.pos_model.append(t("pos_top", lang))
        self.pos_model.append(t("pos_bottom", lang))
        self.pos_combo_row.set_selected(curr_pos if curr_pos < 4 else 0)

        # Görünürlük
        self.workspace_group.set_visible(is_workspace)
        self.device_group.set_visible(not is_workspace)
        self.perf_group.set_visible(is_airplay)

        is_extend = (self.mode_combo_row.get_selected() == 1)
        self.pos_group.set_visible(is_extend and (not is_workspace))

    def _on_proto_changed(self, combo_row, pspec):
        idx = combo_row.get_selected()
        is_workspace = (idx == 0)
        is_airplay = (idx == 3)
        self.workspace_group.set_visible(is_workspace)
        self.device_group.set_visible(not is_workspace)
        self.perf_group.set_visible(is_airplay)
        is_extend = (self.mode_combo_row.get_selected() == 1)
        self.pos_group.set_visible(is_extend and (not is_workspace))

    def _on_copy_ip(self, button):
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(self.ws_ip_row.get_subtitle())

    def _on_notify_tv(self, button):
        target_ip = self.selected_device_ip or "192.168.1.204"
        success = self.streamer.notify_samsung_tv_workspace(target_ip)
        if success:
            self.status_banner.set_description(t("notify_tv_success", self.current_lang))

    def _on_change_language(self, button, code, popover):
        self.current_lang = code
        popover.popdown()
        self._refresh_texts()

    def _on_mode_changed(self, combo_row, pspec):
        idx = self.proto_combo_row.get_selected()
        is_workspace = (idx == 1)
        is_extend = (combo_row.get_selected() == 1)
        self.pos_group.set_visible(is_extend and (not is_workspace))

    def _on_position_changed(self, combo_row, pspec):
        pos_idx = combo_row.get_selected()
        pos_keys = ["right", "left", "top", "bottom"]
        chosen_pos = pos_keys[pos_idx] if pos_idx < len(pos_keys) else "right"
        self.display_mgr.arrange_position("Virtual-1", chosen_pos)

    def _on_manual_refresh(self, button):
        self.status_banner.set_description(t("status_scanning", self.current_lang))
        GLib.idle_add(self._scan_and_update)

    def _scan_and_update(self):
        devs = self.scanner.scan_once()
        for d in devs:
            self._add_device_row(d)
        if not self.streamer.is_streaming:
            self.status_banner.set_description(t("status_ready", self.current_lang))

    def _on_device_found_bg(self, device):
        GLib.idle_add(self._add_device_row, device)

    def _add_device_row(self, device):
        if device.ip in self.discovered_devices:
            return

        self.discovered_devices[device.ip] = device

        if self.no_dev_row.get_parent():
            self.device_list_box.remove(self.no_dev_row)

        row = Adw.ActionRow()
        row.set_title(device.name)
        mac_str = f" • MAC: {device.wifi_mac}" if device.wifi_mac else ""
        row.set_subtitle(f"{device.ip} • {device.model}{mac_str}")
        row.set_activatable(True)

        icon = Gtk.Image.new_from_icon_name("tv-symbolic")
        row.add_prefix(icon)

        self.device_list_box.append(row)

        if self.selected_device_ip is None or self.selected_device_ip == "192.168.1.204":
            self.selected_device_ip = device.ip
            self.device_list_box.select_row(row)

    def _on_device_selected(self, list_box, row):
        if not row or row == self.no_dev_row:
            return
        subtitle = row.get_subtitle()
        if subtitle:
            ip = subtitle.split()[0]
            self.selected_device_ip = ip

    def _on_toggle_streaming(self, button):
        if self.streamer.is_streaming:
            self.streamer.stop_stream()
            self._refresh_texts()
            return

        proto_idx = self.proto_combo_row.get_selected()
        proto_map = ["workspace", "smartview", "miracast", "airplay"]
        chosen_proto = proto_map[proto_idx] if proto_idx < len(proto_map) else "workspace"

        mode_idx = self.mode_combo_row.get_selected()
        modes = ["clone", "extend", "window"]
        chosen_mode = modes[mode_idx] if mode_idx < len(modes) else "clone"

        target_ip = self.selected_device_ip or "192.168.1.204"

        # Workspace modu: krdpserver + Samsung Multi View Hack Tetikleyici
        if chosen_proto == "workspace":
            self.status_banner.set_description(t("workspace_status_active", self.current_lang))
            success = self.streamer.start_workspace(mode=chosen_mode, target_ip=target_ip)
            if success:
                self._refresh_texts()
            return

        # Hedef IP
        target_ip = self.selected_device_ip or "192.168.1.204"
        target_dev = self.discovered_devices.get(target_ip)
        if not target_dev:
            target_dev = DiscoveredDevice(name="Samsung M7", ip=target_ip, port=7000, model="M70DO")

        self.status_banner.set_description(t("status_connecting", self.current_lang))

        # Performans Ayarları
        # FPS (0: 30 FPS Önerilen, 1: 60 FPS)
        fps_val = 30 if self.fps_row.get_selected() == 0 else 60

        # Bitrate / Renk Kalitesi (0: Otomatik Dinamik, 1: 20 Mbps, 2: 12 Mbps)
        q_idx = self.quality_row.get_selected()
        bitrate_map = [0, 20000, 12000]
        bitrate_val = bitrate_map[q_idx] if q_idx < len(bitrate_map) else 0

        # Latency (0: Otomatik NTP Senkron, 1: 20 ms, 2: 40 ms)
        lat_idx = self.latency_row.get_selected()
        lat_map = [0, 20, 40]
        lat_val = lat_map[lat_idx] if lat_idx < len(lat_map) else 0

        # Codec
        codec_idx = self.codec_row.get_selected()
        codec_map = ["auto", "h264", "hevc"]
        codec_val = codec_map[codec_idx] if codec_idx < len(codec_map) else "auto"

        # İkinci ekran konumu
        if chosen_mode == "extend":
            pos_idx = self.pos_combo_row.get_selected()
            pos_keys = ["right", "left", "top", "bottom"]
            chosen_pos = pos_keys[pos_idx] if pos_idx < len(pos_keys) else "right"
            self.display_mgr.arrange_position("Virtual-1", chosen_pos)

        success = self.streamer.start_stream(
            target_dev,
            protocol=chosen_proto,
            mode=chosen_mode,
            fps=fps_val,
            latency_ms=lat_val,
            bitrate_kbps=bitrate_val,
            codec=codec_val
        )

        if success:
            self._refresh_texts()
        else:
            self.status_banner.set_description(t("status_ready", self.current_lang))

    def _on_toggle_multiview(self, _button):
        """TV'ye doğrudan KEY_MULTIVIEW fırlatarak ekranı Multi View'a böler veya tam ekrana alır."""
        target_ip = self.selected_device_ip or "192.168.1.204"
        threading.Thread(target=self.streamer.send_multiview_key, args=(target_ip,), daemon=True).start()

    def _on_stream_status_bg(self, is_streaming, target_dev):
        GLib.idle_add(self._refresh_texts)


class RamordCastApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.ramord.cast",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = RamordCastWindow(self)
        win.present()


def main():
    app = RamordCastApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
