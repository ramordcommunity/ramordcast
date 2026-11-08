#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ramord Cast - Display Mirroring & Wireless Virtual Second Monitor for Samsung Tizen & Linux
(Apple AirPlay 2, Samsung Workspace RDP 2nd Screen, Google Cast, GTK4 + Libadwaita, 6 Languages)
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
from display_mgr import DisplayManager

def detect_system_language():
    """Detects system language from environment (LANG/LC_ALL) falling back to 'en'."""
    raw = os.environ.get('LC_ALL') or os.environ.get('LC_MESSAGES') or os.environ.get('LANG') or 'en'
    code = raw.split('.')[0].split('_')[0].lower()
    return code if code in LANGUAGES else 'en'

class RamordCastWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Ramord Cast")
        self.set_default_size(740, 820)

        # Detect PC system language, fallback to English if unknown
        self.current_lang = detect_system_language()

        # Customizable Workspace Credentials
        self.ws_username = "ramordcommunity"
        self.ws_password = "1234"
        self.ws_port = 3389

        self.scanner = DeviceScanner(on_device_found=self._on_device_found_bg)
        self.display_mgr = DisplayManager()
        self.streamer = CastStreamer(on_status_change=self._on_stream_status_bg)

        self.discovered_devices = {}
        self.selected_device_ip = None

        self._apply_theme()
        self._build_ui()
        self._refresh_texts()

        # Start auto scanning
        self.scanner.start_scanning()

    def _apply_theme(self):
        """Applies RamordCommunity Dark Turquoise & Obsidian Luxury theme styling."""
        css = b"""
        window, .background {
            background: radial-gradient(circle at 50% 25%, #102127 0%, #0b171b 45%, #071013 85%);
            color: #f3f8f8;
        }

        headerbar {
            background: rgba(7, 16, 19, 0.88);
            border-bottom: 1px solid rgba(20, 200, 178, 0.18);
            color: #f3f8f8;
        }

        preferencesgroup > box {
            background: rgba(11, 23, 27, 0.65);
            border: 1px solid rgba(20, 200, 178, 0.14);
            border-radius: 14px;
            padding: 4px;
        }

        .boxed-list {
            background: rgba(11, 23, 27, 0.65);
            border: 1px solid rgba(20, 200, 178, 0.14);
            border-radius: 14px;
        }

        .boxed-list row {
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .suggested-action {
            background: linear-gradient(135deg, #14c8b2 0%, #005a48 100%);
            color: #071013;
            font-weight: 700;
            border: none;
            box-shadow: 0 4px 15px rgba(20, 200, 178, 0.25);
        }

        .suggested-action:hover {
            background: linear-gradient(135deg, #18e0c8 0%, #006e58 100%);
            box-shadow: 0 4px 20px rgba(20, 200, 178, 0.4);
        }

        .destructive-action {
            background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%);
            color: #ffffff;
            font-weight: 700;
            border: none;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.25);
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _build_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        # Header Bar
        self.header_bar = Adw.HeaderBar()
        main_box.append(self.header_bar)

        # Prominent Language Selector (Pill button with Flag/Language Icon and current language name)
        self.lang_btn = Gtk.MenuButton()
        self.lang_btn.add_css_class("flat")
        self.lang_btn.set_tooltip_text("Language / Dil")

        lang_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lang_icon = Gtk.Image.new_from_icon_name("preferences-desktop-locale-symbolic")
        self.lang_btn_label = Gtk.Label(label=LANGUAGES.get(self.current_lang, "English"))
        self.lang_btn_label.add_css_class("heading")
        lang_btn_box.append(lang_icon)
        lang_btn_box.append(self.lang_btn_label)
        self.lang_btn.set_child(lang_btn_box)

        lang_popover = Gtk.Popover()
        lang_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        lang_box.set_margin_top(8)
        lang_box.set_margin_bottom(8)
        lang_box.set_margin_start(8)
        lang_box.set_margin_end(8)

        for code, label in LANGUAGES.items():
            btn = Gtk.Button(label=label)
            btn.add_css_class("flat")
            btn.connect("clicked", self._on_change_language, code, lang_popover)
            lang_box.append(btn)

        lang_popover.set_child(lang_box)
        self.lang_btn.set_popover(lang_popover)
        self.header_bar.pack_start(self.lang_btn)

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
        clamp.set_maximum_size(700)
        clamp.set_tightening_threshold(540)
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

        # 2. Connection Protocol Selection (AirPlay vs Workspace vs Cast)
        self.proto_group = Adw.PreferencesGroup()
        content_box.append(self.proto_group)

        self.proto_combo_row = Adw.ComboRow()
        self.proto_model = Gtk.StringList()
        self.proto_combo_row.set_model(self.proto_model)
        self.proto_combo_row.connect("notify::selected", self._on_proto_changed)
        self.proto_group.add(self.proto_combo_row)

        # 3. Samsung Workspace Connection Details Card (IP, User, Pass, Port, Edit button)
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

        # Edit Credentials Row with Button
        self.ws_edit_row = Adw.ActionRow()
        self.edit_btn = Gtk.Button()
        self.edit_btn.add_css_class("pill")
        self.edit_btn.set_valign(Gtk.Align.CENTER)
        self.edit_btn.connect("clicked", self._on_open_edit_dialog)
        self.ws_edit_row.add_suffix(self.edit_btn)
        self.workspace_group.add(self.ws_edit_row)

        # 4. Display Mode & 2nd Screen Position (Extend vs Clone, Right vs Left)
        self.mode_group = Adw.PreferencesGroup()
        content_box.append(self.mode_group)

        self.mode_combo_row = Adw.ComboRow()
        self.mode_model = Gtk.StringList()
        self.mode_combo_row.set_model(self.mode_model)
        self.mode_combo_row.connect("notify::selected", self._on_mode_changed)
        self.mode_group.add(self.mode_combo_row)

        self.pos_group = Adw.PreferencesGroup()
        content_box.append(self.pos_group)

        self.pos_combo_row = Adw.ComboRow()
        self.pos_model = Gtk.StringList()
        self.pos_combo_row.set_model(self.pos_model)
        self.pos_combo_row.connect("notify::selected", self._on_position_changed)
        self.pos_group.add(self.pos_combo_row)

        # 5. Performance & Quality Settings (AirPlay)
        self.perf_group = Adw.PreferencesGroup()
        content_box.append(self.perf_group)

        self.fps_row = Adw.ComboRow()
        self.fps_model = Gtk.StringList()
        self.fps_row.set_model(self.fps_model)
        self.perf_group.add(self.fps_row)

        self.quality_row = Adw.ComboRow()
        self.quality_model = Gtk.StringList()
        self.quality_row.set_model(self.quality_model)
        self.perf_group.add(self.quality_row)

        self.latency_row = Adw.ComboRow()
        self.latency_model = Gtk.StringList()
        self.latency_row.set_model(self.latency_model)
        self.perf_group.add(self.latency_row)

        self.codec_row = Adw.ComboRow()
        self.codec_model = Gtk.StringList()
        self.codec_row.set_model(self.codec_model)
        self.perf_group.add(self.codec_row)

        self.vaapi_switch_row = Adw.SwitchRow()
        self.vaapi_switch_row.set_active(True)
        self.perf_group.add(self.vaapi_switch_row)

        # 6. Target Devices List
        self.device_group = Adw.PreferencesGroup()
        content_box.append(self.device_group)

        self.device_list_box = Gtk.ListBox()
        self.device_list_box.add_css_class("boxed-list")
        self.device_list_box.connect("row-selected", self._on_device_selected)
        self.device_group.add(self.device_list_box)

        self.no_dev_row = Adw.ActionRow()
        self.device_list_box.append(self.no_dev_row)

        # 7. Action Button
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

        self.lang_btn_label.set_label(LANGUAGES.get(lang, "English"))

        curr_proto_idx = self.proto_combo_row.get_selected()
        is_airplay = (curr_proto_idx == 0)
        is_workspace = (curr_proto_idx == 1)

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
        self.proto_model.append(t("proto_workspace", lang))
        self.proto_model.append(t("proto_cast", lang))
        self.proto_combo_row.set_selected(curr_proto_idx if curr_proto_idx < 3 else 0)

        # Samsung Workspace Card
        self.workspace_group.set_title(t("workspace_info_title", lang))
        self.ws_guide_row.set_title(t("workspace_guide", lang))
        self.ws_ip_row.set_title(t("workspace_ip", lang))
        self.ws_ip_row.set_subtitle(self.streamer.get_local_ip())
        self.ws_user_row.set_title(t("workspace_user", lang))
        self.ws_user_row.set_subtitle(self.ws_username)
        self.ws_pass_row.set_title(t("workspace_password", lang))
        self.ws_pass_row.set_subtitle(self.ws_password)
        self.ws_port_row.set_title(t("workspace_port", lang))
        self.ws_port_row.set_subtitle(str(self.ws_port))

        self.ws_edit_row.set_title(t("dialog_edit_title", lang))
        self.edit_btn.set_label(t("btn_edit", lang))

        # Display Mode (Mirror vs Extend)
        curr_mode = self.mode_combo_row.get_selected()
        self.mode_group.set_title(t("section_display_mode", lang))
        self.mode_combo_row.set_title(t("section_display_mode", lang))
        while self.mode_model.get_n_items() > 0:
            self.mode_model.remove(0)
        self.mode_model.append(t("mode_extend", lang))
        self.mode_model.append(t("mode_clone", lang))
        self.mode_combo_row.set_selected(curr_mode if curr_mode < 2 else 0)

        # 2nd Display Position
        curr_pos = self.pos_combo_row.get_selected()
        self.pos_group.set_title(t("section_position", lang))
        self.pos_combo_row.set_title(t("section_position", lang))
        while self.pos_model.get_n_items() > 0:
            self.pos_model.remove(0)
        self.pos_model.append(t("pos_right", lang))
        self.pos_model.append(t("pos_left", lang))
        self.pos_model.append(t("pos_top", lang))
        self.pos_model.append(t("pos_bottom", lang))
        self.pos_combo_row.set_selected(curr_pos if curr_pos < 4 else 0)

        # Visibility Rules
        self.workspace_group.set_visible(is_workspace)
        self.device_group.set_visible(not is_workspace)
        self.perf_group.set_visible(is_airplay)

        is_extend = (self.mode_combo_row.get_selected() == 0) # 0 is Extend
        self.mode_group.set_visible(is_workspace)
        self.pos_group.set_visible(is_workspace and is_extend)

        # Performance Settings
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
        is_workspace = (idx == 1)

        self.workspace_group.set_visible(is_workspace)
        self.device_group.set_visible(not is_workspace)
        self.perf_group.set_visible(is_airplay)

        is_extend = (self.mode_combo_row.get_selected() == 0)
        self.mode_group.set_visible(is_workspace)
        self.pos_group.set_visible(is_workspace and is_extend)

    def _on_mode_changed(self, combo_row, pspec):
        idx = self.proto_combo_row.get_selected()
        is_workspace = (idx == 1)
        is_extend = (combo_row.get_selected() == 0)
        self.pos_group.set_visible(is_workspace and is_extend)

    def _on_position_changed(self, combo_row, pspec):
        pos_idx = combo_row.get_selected()
        pos_keys = ["right", "left", "top", "bottom"]
        chosen_pos = pos_keys[pos_idx] if pos_idx < len(pos_keys) else "right"
        self.display_mgr.arrange_position("Virtual-1", chosen_pos)

    def _on_copy_ip(self, button):
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(self.ws_ip_row.get_subtitle())

    def _on_change_language(self, button, code, popover):
        self.current_lang = code
        popover.popdown()
        self._refresh_texts()

    def _on_open_edit_dialog(self, button):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=t("dialog_edit_title", self.current_lang),
            body=""
        )

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)

        user_entry = Adw.EntryRow(title=t("workspace_user", self.current_lang))
        user_entry.set_text(self.ws_username)
        content.append(user_entry)

        pass_entry = Adw.PasswordEntryRow(title=t("workspace_password", self.current_lang))
        pass_entry.set_text(self.ws_password)
        content.append(pass_entry)

        port_entry = Adw.EntryRow(title=t("workspace_port", self.current_lang))
        port_entry.set_text(str(self.ws_port))
        content.append(port_entry)

        dialog.set_extra_child(content)

        dialog.add_response("cancel", t("btn_cancel", self.current_lang))
        dialog.add_response("save", t("btn_save", self.current_lang))
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

        def on_response(dialog, response):
            if response == "save":
                new_u = user_entry.get_text().strip()
                new_p = pass_entry.get_text().strip()
                new_port = port_entry.get_text().strip()
                if new_u:
                    self.ws_username = new_u
                if new_p:
                    self.ws_password = new_p
                if new_port and new_port.isdigit():
                    self.ws_port = int(new_port)
                self._refresh_texts()

        dialog.connect("response", on_response)
        dialog.present()

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
        proto_map = ["airplay", "workspace", "cast"]
        chosen_proto = proto_map[proto_idx] if proto_idx < len(proto_map) else "airplay"

        mode_idx = self.mode_combo_row.get_selected()
        chosen_mode = "extend" if mode_idx == 0 else "clone"

        # Workspace Mode: Virtual Second Display
        if chosen_proto == "workspace":
            pos_idx = self.pos_combo_row.get_selected()
            pos_keys = ["right", "left", "top", "bottom"]
            chosen_pos = pos_keys[pos_idx] if pos_idx < len(pos_keys) else "right"

            success = self.streamer.start_workspace(
                mode=chosen_mode,
                username=self.ws_username,
                password=self.ws_password,
                port=self.ws_port
            )
            if success:
                if chosen_mode == "extend":
                    threading.Timer(2.0, self.display_mgr.arrange_position, args=("Virtual-1", chosen_pos)).start()
                self._refresh_texts()
            return

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
