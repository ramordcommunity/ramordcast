#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ramord Cast - Ultra-Low-Latency Display Mirroring & Wireless Casting for Samsung Tizen & Linux
(Apple AirPlay 2 & Google Cast / Chromecast, GTK4 + Libadwaita, Multi-Language Support)
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
from streamer import CastStreamer

class RamordCastWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Ramord Cast")
        self.set_default_size(720, 720)

        self.current_lang = "en"
        self.scanner = DeviceScanner(on_device_found=self._on_device_found_bg)
        self.streamer = CastStreamer(on_status_change=self._on_stream_status_bg)

        self.discovered_devices = {}
        self.selected_device_ip = None

        self._build_ui()
        self._refresh_texts()

        # Start auto scanning
        self.scanner.start_scanning()

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header Bar
        self.header_bar = Adw.HeaderBar()
        main_box.append(self.header_bar)

        # Language Menu
        lang_menu_btn = Gtk.MenuButton()
        lang_menu_btn.set_icon_name("preferences-desktop-locale-symbolic")
        lang_popover = Gtk.Popover()
        lang_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lang_box.set_margin_top(6)
        lang_box.set_margin_bottom(6)
        lang_box.set_margin_start(6)
        lang_box.set_margin_end(6)

        for code, label in LANGUAGES.items():
            btn = Gtk.Button(label=label)
            btn.connect("clicked", self._on_change_language, code, lang_popover)
            lang_box.append(btn)

        lang_popover.set_child(lang_box)
        lang_menu_btn.set_popover(lang_popover)
        self.header_bar.pack_start(lang_menu_btn)

        # Refresh Button
        self.refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        self.refresh_btn.connect("clicked", self._on_manual_refresh)
        self.header_bar.pack_end(self.refresh_btn)

        # Scrolled Window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        main_box.append(scrolled)

        # Clamp Container
        clamp = Adw.Clamp()
        clamp.set_maximum_size(680)
        clamp.set_tightening_threshold(520)
        scrolled.set_child(clamp)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(28)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)
        clamp.set_child(content_box)

        # 1. Status Banner
        self.status_banner = Adw.StatusPage()
        self.status_banner.set_icon_name("video-display-symbolic")
        content_box.append(self.status_banner)

        # 2. Connection Protocol Selection (AirPlay vs Chromecast)
        self.proto_group = Adw.PreferencesGroup()
        content_box.append(self.proto_group)

        self.proto_combo_row = Adw.ComboRow()
        self.proto_model = Gtk.StringList()
        self.proto_combo_row.set_model(self.proto_model)
        self.proto_combo_row.connect("notify::selected", self._on_proto_changed)
        self.proto_group.add(self.proto_combo_row)

        # 3. Performance & Quality Settings
        self.perf_group = Adw.PreferencesGroup()
        content_box.append(self.perf_group)

        # FPS
        self.fps_row = Adw.ComboRow()
        self.fps_model = Gtk.StringList()
        self.fps_row.set_model(self.fps_model)
        self.perf_group.add(self.fps_row)

        # Bitrate / Color Quality
        self.quality_row = Adw.ComboRow()
        self.quality_model = Gtk.StringList()
        self.quality_row.set_model(self.quality_model)
        self.perf_group.add(self.quality_row)

        # Latency Target
        self.latency_row = Adw.ComboRow()
        self.latency_model = Gtk.StringList()
        self.latency_row.set_model(self.latency_model)
        self.perf_group.add(self.latency_row)

        # Codec
        self.codec_row = Adw.ComboRow()
        self.codec_model = Gtk.StringList()
        self.codec_row.set_model(self.codec_model)
        self.perf_group.add(self.codec_row)

        # Hardware Acceleration
        self.vaapi_switch_row = Adw.SwitchRow()
        self.vaapi_switch_row.set_active(True)
        self.perf_group.add(self.vaapi_switch_row)

        # 4. Target Devices List
        self.device_group = Adw.PreferencesGroup()
        content_box.append(self.device_group)

        self.device_list_box = Gtk.ListBox()
        self.device_list_box.add_css_class("boxed-list")
        self.device_list_box.connect("row-selected", self._on_device_selected)
        self.device_group.add(self.device_list_box)

        self.no_dev_row = Adw.ActionRow()
        self.device_list_box.append(self.no_dev_row)

        # 5. Action Button
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        content_box.append(btn_box)

        self.action_btn = Gtk.Button()
        self.action_btn.add_css_class("suggested-action")
        self.action_btn.add_css_class("pill")
        self.action_btn.set_size_request(260, 56)
        self.action_btn.connect("clicked", self._on_toggle_streaming)
        btn_box.append(self.action_btn)

    def _refresh_texts(self):
        """Refreshes all texts across 6 languages."""
        lang = self.current_lang

        self.set_title(t("app_title", lang))
        self.status_banner.set_title(t("app_title", lang))

        curr_proto_idx = self.proto_combo_row.get_selected()
        is_airplay = (curr_proto_idx == 0)

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

        # Protocols
        self.proto_group.set_title(t("section_connection_type", lang))
        self.proto_combo_row.set_title(t("section_connection_type", lang))
        while self.proto_model.get_n_items() > 0:
            self.proto_model.remove(0)
        self.proto_model.append(t("proto_airplay", lang))
        self.proto_model.append(t("proto_cast", lang))
        self.proto_combo_row.set_selected(curr_proto_idx if curr_proto_idx < 2 else 0)

        # Performance Settings
        self.perf_group.set_title(t("section_performance", lang))
        self.perf_group.set_visible(is_airplay)

        curr_fps = self.fps_row.get_selected()
        self.fps_row.set_title(t("fps_label", lang))
        while self.fps_model.get_n_items() > 0:
            self.fps_model.remove(0)
        self.fps_model.append(t("fps_30", lang))
        self.fps_model.append(t("fps_60", lang))
        self.fps_row.set_selected(curr_fps if curr_fps < 2 else 0)

        curr_q = self.quality_row.get_selected()
        self.quality_row.set_title(t("quality_label", lang))
        while self.quality_model.get_n_items() > 0:
            self.quality_model.remove(0)
        self.quality_model.append(t("quality_auto", lang))
        self.quality_model.append(t("quality_high", lang))
        self.quality_model.append(t("quality_standard", lang))
        self.quality_row.set_selected(curr_q if curr_q < 3 else 0)

        curr_lat = self.latency_row.get_selected()
        self.latency_row.set_title(t("latency_target_label", lang))
        while self.latency_model.get_n_items() > 0:
            self.latency_model.remove(0)
        self.latency_model.append(t("latency_auto", lang))
        self.latency_model.append(t("latency_20ms", lang))
        self.latency_model.append(t("latency_40ms", lang))
        self.latency_row.set_selected(curr_lat if curr_lat < 3 else 0)

        curr_codec = self.codec_row.get_selected()
        self.codec_row.set_title(t("codec_label", lang))
        while self.codec_model.get_n_items() > 0:
            self.codec_model.remove(0)
        self.codec_model.append(t("codec_auto", lang))
        self.codec_model.append(t("codec_h264", lang))
        self.codec_model.append(t("codec_hevc", lang))
        self.codec_row.set_selected(curr_codec if curr_codec < 3 else 0)

        self.vaapi_switch_row.set_title(t("hardware_acceleration", lang))

        # Target Devices
        self.device_group.set_title(t("section_targets", lang))
        self.no_dev_row.set_title(t("no_devices", lang))

    def _on_proto_changed(self, combo_row, pspec):
        idx = combo_row.get_selected()
        is_airplay = (idx == 0)
        self.perf_group.set_visible(is_airplay)

    def _on_change_language(self, button, code, popover):
        self.current_lang = code
        popover.popdown()
        self._refresh_texts()

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
        self.no_dev_row.set_visible(False)

        row = Adw.ActionRow()
        row.set_title(device.name)
        subtitle = f"{device.ip} ({device.model})"
        row.set_subtitle(subtitle)

        icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
        row.add_prefix(icon)

        self.device_list_box.append(row)

        if not self.selected_device_ip:
            self.device_list_box.select_row(row)
            self.selected_device_ip = device.ip

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
        chosen_proto = "airplay" if proto_idx == 0 else "cast"

        target_ip = self.selected_device_ip or "192.168.1.204"
        target_dev = self.discovered_devices.get(target_ip)
        if not target_dev:
            target_dev = DiscoveredDevice(name="Target Display", ip=target_ip, port=7000, model="SmartTV")

        self.status_banner.set_description(t("status_connecting", self.current_lang))

        fps_val = 30 if self.fps_row.get_selected() == 0 else 60

        q_idx = self.quality_row.get_selected()
        bitrate_map = [0, 20000, 12000]
        bitrate_val = bitrate_map[q_idx] if q_idx < len(bitrate_map) else 0

        lat_idx = self.latency_row.get_selected()
        lat_map = [0, 20, 40]
        lat_val = lat_map[lat_idx] if lat_idx < len(lat_map) else 0

        codec_idx = self.codec_row.get_selected()
        codec_map = ["auto", "h264", "hevc"]
        codec_val = codec_map[codec_idx] if codec_idx < len(codec_map) else "auto"

        success = self.streamer.start_stream(
            target_dev,
            protocol=chosen_proto,
            fps=fps_val,
            latency_ms=lat_val,
            bitrate_kbps=bitrate_val,
            codec=codec_val
        )

        if success:
            self._refresh_texts()
        else:
            self.status_banner.set_description(t("status_ready", self.current_lang))

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
