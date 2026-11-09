#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ramord Cast - Display Mirroring & Wireless Virtual Second Monitor for Samsung Tizen & Linux
(Apple AirPlay 2, Samsung Workspace RDP 2nd Screen, Google Cast, GTK4 + Libadwaita, 6 Languages)
"""

import sys
import os
import signal
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
        self.set_icon_name("ramordcast")

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

        self.theme_mode = "auto"
        self.css_provider = None
        self._build_ui()
        self._apply_theme()
        self._refresh_texts()

        # Start background scanner
        self.scanner.start_scanning()

    def _detect_system_theme(self) -> str:
        try:
            sm = Adw.StyleManager.get_default()
            return "night" if sm.get_dark() else "day"
        except Exception:
            return "night"

    def _resolve_theme_key(self) -> str:
        if self.theme_mode in ("day", "night"):
            return self.theme_mode
        return self._detect_system_theme()

    def _apply_theme(self):
        """Applies solid Day (#F4F1EA/#EFECE6/#2B2A27/#1A3328) or Night (#080C0A/#101613/#E8E4DA/#589E7B) theme."""
        active_key = self._resolve_theme_key()
        is_day = (active_key == "day")

        if is_day:
            bg = "#F4F1EA"
            card = "#EFECE6"
            card_border = "rgba(26, 51, 40, 0.15)"
            text = "#2B2A27"
            dim = "#6B6862"
            accent = "#1A3328"
            accent_hover = "#284e3e"
            accent_text = "#F4F1EA"
            header_bg = "#EAE5DC"
        else:
            bg = "#080C0A"
            card = "#101613"
            card_border = "rgba(88, 158, 123, 0.20)"
            text = "#E8E4DA"
            dim = "#8A948E"
            accent = "#589E7B"
            accent_hover = "#6db893"
            accent_text = "#080C0A"
            header_bg = "#0d1310"

        css_text = f"""
        window, window.background {{
            border-radius: 16px;
            background: {bg};
            color: {text};
        }}

        headerbar {{
            background: {header_bg};
            border-bottom: 1px solid {card_border};
            color: {text};
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
        }}

        preferencesgroup > box {{
            background: {card};
            border: 1px solid {card_border};
            border-radius: 14px;
            padding: 4px;
            color: {text};
        }}

        .boxed-list {{
            background: {card};
            border: 1px solid {card_border};
            border-radius: 14px;
            color: {text};
        }}

        .boxed-list row {{
            border-bottom: 1px solid {card_border};
            color: {text};
        }}

        .suggested-action {{
            background: {accent};
            color: {accent_text};
            font-weight: 700;
            border: none;
        }}

        .suggested-action:hover {{
            background: {accent_hover};
        }}

        .destructive-action {{
            background: #ef4444;
            color: #ffffff;
            font-weight: 700;
            border: none;
        }}

        /* Modern Rounded Dropdowns & Popovers */
        popover contents, popover .view, popover listview {{
            background-color: {card};
            color: {text};
            border-radius: 12px;
            border: 1px solid {card_border};
            padding: 6px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}

        popover listview row {{
            padding: 10px 14px;
            border-radius: 8px;
            margin: 2px 0;
            min-height: 38px;
            color: {text};
        }}

        popover listview row:selected, popover listview row:hover {{
            background: {card_border};
            color: {accent};
        }}

        /* Fixed Banner Dimensions */
        statuspage > box {{
            min-height: 120px;
        }}

        statuspage .icon {{
            -gtk-icon-size: 64px;
            min-width: 64px;
            min-height: 64px;
        }}
        """

        if self.css_provider is not None:
            Gtk.StyleContext.remove_provider_for_display(
                Gdk.Display.get_default(),
                self.css_provider
            )

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_data(css_text.encode('utf-8'))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
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

        # Theme Switcher (Auto / Day / Night)
        self.theme_btn = Gtk.MenuButton()
        self.theme_btn.add_css_class("flat")
        self.theme_btn.set_tooltip_text("Theme / Tema")
        theme_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        theme_icon = Gtk.Image.new_from_icon_name("display-brightness-symbolic")
        self.theme_btn_label = Gtk.Label(label=t(f"theme_{self.theme_mode}", self.current_lang))
        self.theme_btn_label.add_css_class("heading")
        theme_btn_box.append(theme_icon)
        theme_btn_box.append(self.theme_btn_label)
        self.theme_btn.set_child(theme_btn_box)

        theme_popover = Gtk.Popover()
        theme_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        theme_box.set_margin_top(8)
        theme_box.set_margin_bottom(8)
        theme_box.set_margin_start(8)
        theme_box.set_margin_end(8)

        for m_key in ("auto", "day", "night"):
            m_btn = Gtk.Button(label=t(f"theme_{m_key}", self.current_lang))
            m_btn.add_css_class("flat")
            m_btn.connect("clicked", self._on_change_theme, m_key, theme_popover)
            theme_box.append(m_btn)

        theme_popover.set_child(theme_box)
        self.theme_btn.set_popover(theme_popover)
        self.header_bar.pack_start(self.theme_btn)

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

        # 1. Fixed Status Banner Box (Stable dimensions, no shrinking or overlapping)
        self.banner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.banner_box.set_halign(Gtk.Align.CENTER)
        self.banner_box.set_margin_top(12)
        self.banner_box.set_margin_bottom(12)
        content_box.append(self.banner_box)

        icon_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ramordcast.png")
        if os.path.exists(icon_file):
            self.banner_icon = Gtk.Image.new_from_file(icon_file)
            self.banner_icon.set_pixel_size(108)
        else:
            self.banner_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
            self.banner_icon.set_pixel_size(84)
        self.banner_box.append(self.banner_icon)

        self.banner_title = Gtk.Label(label="Ramord Cast")
        self.banner_title.add_css_class("title-1")
        self.banner_box.append(self.banner_title)

        self.banner_desc = Gtk.Label()
        self.banner_desc.add_css_class("body")
        self.banner_desc.add_css_class("dim-label")
        self.banner_desc.set_wrap(True)
        self.banner_desc.set_justify(Gtk.Justification.CENTER)
        self.banner_desc.set_max_width_chars(50)
        self.banner_box.append(self.banner_desc)

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

        # 6. Target Devices List (with animated Spinner & Scanning status)
        self.device_group = Adw.PreferencesGroup()
        content_box.append(self.device_group)

        # Header suffix for device group: scanning spinner + badge
        scan_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        scan_box.set_valign(Gtk.Align.CENTER)

        self.scan_spinner = Gtk.Spinner()
        self.scan_spinner.set_size_request(16, 16)
        scan_box.append(self.scan_spinner)

        self.scan_badge = Gtk.Label()
        self.scan_badge.add_css_class("caption")
        self.scan_badge.add_css_class("dim-label")
        scan_box.append(self.scan_badge)

        self.device_group.set_header_suffix(scan_box)

        self.device_list_box = Gtk.ListBox()
        self.device_list_box.add_css_class("boxed-list")
        self.device_list_box.connect("row-selected", self._on_device_selected)
        self.device_group.add(self.device_list_box)

        self.no_dev_row = Adw.ActionRow()
        self.device_list_box.append(self.no_dev_row)

        # Pre-populate device list from cache immediately (0ms instant display)
        for dev in self.scanner.get_cached_devices():
            self._add_device_row(dev)

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

        # 8. Developer Note Card (Multi View story & contact)
        self.note_group = Adw.PreferencesGroup()
        content_box.append(self.note_group)

        self.note_row = Adw.ActionRow()
        self.note_row.set_subtitle_lines(0)
        icon_note = Gtk.Image.new_from_icon_name("help-about-symbolic")
        self.note_row.add_prefix(icon_note)
        self.note_group.add(self.note_row)

    def _refresh_texts(self):
        """Refreshes all texts across 6 languages."""
        lang = self.current_lang

        self.set_title(t("app_title", lang))
        self.banner_title.set_label(t("app_title", lang))

        self.lang_btn_label.set_label(LANGUAGES.get(lang, "English"))
        if hasattr(self, "theme_btn_label"):
            self.theme_btn_label.set_label(t(f"theme_{self.theme_mode}", lang))

        curr_proto_idx = self.proto_combo_row.get_selected()
        is_airplay = (curr_proto_idx == 0)
        is_workspace = (curr_proto_idx == 1)

        if self.streamer.is_streaming:
            self.banner_desc.set_label(t("status_connected", lang))
            self.action_btn.set_label(t("btn_stop", lang))
            self.action_btn.remove_css_class("suggested-action")
            self.action_btn.add_css_class("destructive-action")
        else:
            self.banner_desc.set_label(t("status_ready", lang))
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

        # Developer Note
        self.note_group.set_title(t("author_note_title", lang))
        self.note_row.set_title(t("author_note_title", lang))
        self.note_row.set_subtitle(t("author_note_text", lang))

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

    def _on_change_theme(self, button, mode, popover):
        self.theme_mode = mode
        popover.popdown()
        self._apply_theme()
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
        self.banner_desc.set_label(t("status_scanning", self.current_lang))
        self.scan_badge.set_label(t("searching_badge", self.current_lang))
        self.scan_spinner.start()
        self.scan_spinner.set_visible(True)
        self.scan_badge.set_visible(True)
        self.refresh_btn.set_sensitive(False)

        def bg_scan():
            devs = self.scanner.scan_once()
            GLib.idle_add(self._on_scan_finished, devs)

        threading.Thread(target=bg_scan, daemon=True).start()

    def _on_scan_finished(self, devs):
        for d in devs:
            self._add_device_row(d)
        self.scan_spinner.stop()
        self.scan_spinner.set_visible(False)
        self.scan_badge.set_visible(False)
        self.refresh_btn.set_sensitive(True)
        if not self.streamer.is_streaming:
            self.banner_desc.set_label(t("status_ready", self.current_lang))

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

        self.banner_desc.set_label(t("status_connecting", self.current_lang))

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
            self.banner_desc.set_label(t("status_ready", self.current_lang))

    def _on_stream_status_bg(self, is_streaming, target_dev):
        GLib.idle_add(self._refresh_texts)

    def do_close_request(self):
        try:
            self.streamer.stop_stream()
        except Exception:
            pass
        return False


class RamordCastApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.ramord.cast",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        windows = self.get_windows()
        if not windows:
            win = RamordCastWindow(self)
            win.present()
        else:
            # Toggle behavior: if already running/open, close application cleanly
            for w in list(windows):
                w.close()
            self.quit()


def main():
    app = RamordCastApp()

    def handle_sig(sig, frame):
        for w in list(app.get_windows()):
            try:
                w.close()
            except Exception:
                pass
        app.quit()

    try:
        signal.signal(signal.SIGINT, handle_sig)
        signal.signal(signal.SIGTERM, handle_sig)
    except Exception:
        pass

    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
