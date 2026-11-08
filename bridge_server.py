#!/usr/bin/env python3
"""
Ramord Cast - Galaxy S23 Smart View Multi View Bridge Server
Ultra-low-latency streaming bridge from Wayland PipeWire desktop to phone.
"""

import http.server
import socketserver
import subprocess
import threading
import os
import sys
import time
import dbus
import dbus.mainloop.glib
from gi.repository import GLib

PORT = 8088
IP = "192.168.1.101"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Ramord Cast - Smart View Bridge</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body, html {
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #000;
            color: #fff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        #stream-img {
            width: 100vw;
            height: 100vh;
            object-fit: contain;
            display: block;
            background: #000;
        }
        #fullscreen-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(30, 30, 30, 0.85);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 30px;
            padding: 12px 24px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            backdrop-filter: blur(8px);
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: opacity 0.3s;
        }
        #fullscreen-btn:active {
            transform: scale(0.96);
        }
        .hidden { opacity: 0; pointer-events: none; }
    </style>
</head>
<body>
    <img id="stream-img" src="/stream" alt="Live Screen Stream" />
    <button id="fullscreen-btn" onclick="toggleFullscreen()">⛶ Tam Ekran / Fullscreen</button>

    <script>
        const btn = document.getElementById('fullscreen-btn');
        let hideTimeout;

        function resetHideTimer() {
            btn.classList.remove('hidden');
            clearTimeout(hideTimeout);
            hideTimeout = setTimeout(() => {
                btn.classList.add('hidden');
            }, 3000);
        }

        document.addEventListener('touchstart', resetHideTimer);
        document.addEventListener('click', resetHideTimer);
        resetHideTimer();

        async function toggleFullscreen() {
            if (!document.fullscreenElement) {
                try {
                    await document.documentElement.requestFullscreen();
                    if (screen.orientation && screen.orientation.lock) {
                        try { await screen.orientation.lock('landscape'); } catch(e) {}
                    }
                } catch (err) {}
            } else {
                if (document.exitFullscreen) {
                    await document.exitFullscreen();
                }
            }
        }

        if ('wakeLock' in navigator) {
            navigator.wakeLock.request('screen').catch(() => {});
        }
    </script>
</body>
</html>
"""

def get_screencast_node():
    """Acquire PipeWire ScreenCast node from XDG Desktop Portal."""
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    loop = GLib.MainLoop()

    portal = bus.get_object('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop')
    screencast = dbus.Interface(portal, 'org.freedesktop.portal.ScreenCast')

    node_res = [None]
    now_int = int(time.time())
    sess_tok = f"s_{now_int}"

    def on_sess(resp, res):
        if resp == 0:
            h = res['session_handle']
            t_src = f"src_{int(time.time() * 1000) % 100000}"
            s_name = bus.get_unique_name()[1:].replace('.', '_')
            bus.add_signal_receiver(
                lambda r, re: on_src(r, re, h),
                'Response', 'org.freedesktop.portal.Request', 'org.freedesktop.portal.Desktop',
                f"/org/freedesktop/portal/desktop/request/{s_name}/{t_src}"
            )
            screencast.SelectSources(
                h,
                {'types': dbus.UInt32(1), 'multiple': dbus.Boolean(False), 'cursor_mode': dbus.UInt32(2), 'handle_token': t_src}
            )
        else:
            loop.quit()

    def on_src(resp, res, h):
        if resp == 0:
            t_st = f"st_{int(time.time() * 1000) % 100000}"
            s_name = bus.get_unique_name()[1:].replace('.', '_')
            bus.add_signal_receiver(
                on_st,
                'Response', 'org.freedesktop.portal.Request', 'org.freedesktop.portal.Desktop',
                f"/org/freedesktop/portal/desktop/request/{s_name}/{t_st}"
            )
            screencast.Start(h, '', {'handle_token': t_st})
        else:
            loop.quit()

    def on_st(resp, res):
        if resp == 0:
            node_res[0] = res['streams'][0][0]
        loop.quit()

    s_name = bus.get_unique_name()[1:].replace('.', '_')
    bus.add_signal_receiver(
        on_sess,
        'Response', 'org.freedesktop.portal.Request', 'org.freedesktop.portal.Desktop',
        f"/org/freedesktop/portal/desktop/request/{s_name}/{sess_tok}"
    )
    screencast.CreateSession({'session_handle_token': sess_tok, 'handle_token': sess_tok})

    GLib.timeout_add_seconds(5, loop.quit)
    loop.run()
    return node_res[0]

current_pipewire_node = None

class StreamingHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        global current_pipewire_node
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        elif self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=ffserver')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Connection', 'close')
            self.end_headers()

            if not current_pipewire_node:
                current_pipewire_node = get_screencast_node()

            node = current_pipewire_node
            print(f"[Stream] Starting Wayland PipeWire stream with node {node}")

            gst_cmd = [
                'gst-launch-1.0', '-q',
                'pipewiresrc', f'path={node}', 'do-timestamp=true',
                '!', 'videoconvert',
                '!', 'jpegenc', 'quality=75',
                '!', 'multipartmux', 'boundary=ffserver',
                '!', 'fdsink', 'fd=1'
            ]
            proc = subprocess.Popen(gst_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            try:
                while True:
                    chunk = proc.stdout.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    proc.kill()
        else:
            self.send_error(404)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run():
    global current_pipewire_node
    print("[Portal] Acquiring PipeWire node...")
    current_pipewire_node = get_screencast_node()
    print(f"[Portal] Acquired PipeWire Node: {current_pipewire_node}")

    server = ThreadedHTTPServer(('0.0.0.0', PORT), StreamingHandler)
    url = f"http://{IP}:{PORT}"
    print(f"\n=======================================================")
    print(f"  RAMORD CAST - GALAXY S23 SMART VIEW BRIDGING ACTIVE  ")
    print(f"=======================================================")
    print(f"  Phone Link: {url}\n")
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    run()
