#!/usr/bin/env python3
"""
Ramord Cast - Native Samsung Smart View WFD Server
Direct Wi-Fi Display / Miracast RTSP engine with Samsung proprietary Multi View extensions.
"""

import socket
import threading
import subprocess
import time
import os
import sys
import requests

TV_IP = "192.168.1.204"
LOCAL_IP = "192.168.1.101"
RTSP_PORT = 7236
LOCAL_MAC = "d8:80:83:f9:5c:dd"

class SamsungWFDServer:
    def __init__(self, target_ip=TV_IP, rtsp_port=RTSP_PORT):
        self.target_ip = target_ip
        self.rtsp_port = rtsp_port
        self.server_sock = None
        self.is_running = False
        self.client_rtp_port = 1028
        self.gst_process = None
        self.cseq = 1

    def trigger_tv(self):
        """Trigger Samsung TV's ScreenSharingService via UPnP SOAP to connect to our RTSP server."""
        url = f"http://{self.target_ip}:9119/upnp/control/ScreenSharingService1"
        headers = {
            'SOAPAction': '"urn:samsung.com:service:ScreenSharingService:1#X_ConnectScreenSharingM2TV"',
            'Content-Type': 'text/xml; charset="utf-8"'
        }
        body = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:X_ConnectScreenSharingM2TV xmlns:u="urn:samsung.com:service:ScreenSharingService:1">
      <mWlanMacAddress>{LOCAL_MAC}</mWlanMacAddress>
      <mP2pDeviceAddress>{LOCAL_MAC}</mP2pDeviceAddress>
      <mBluetoothMacAddress>{LOCAL_MAC}</mBluetoothMacAddress>
      <mWFDSourcePort>{self.rtsp_port}</mWFDSourcePort>
    </u:X_ConnectScreenSharingM2TV>
  </s:Body>
</s:Envelope>"""
        try:
            print(f"[WFD-Trigger] Sending X_ConnectScreenSharingM2TV to TV at {self.target_ip}...")
            r = requests.post(url, headers=headers, data=body, timeout=5)
            print(f"[WFD-Trigger] Response status: {r.status_code}")
            return r.status_code == 200
        except Exception as e:
            print(f"[WFD-Trigger] Error: {e}")
            return False

    def start(self):
        self.is_running = True
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, 'SO_REUSEPORT'):
            try:
                self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except Exception:
                pass
        self.server_sock.bind(('0.0.0.0', self.rtsp_port))
        self.server_sock.listen(2)
        print(f"[WFD-Server] Listening on port {self.rtsp_port}...")

        # Trigger TV in background thread after 0.5s
        threading.Thread(target=self._delayed_trigger, daemon=True).start()

        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _delayed_trigger(self):
        time.sleep(0.5)
        self.trigger_tv()

    def _accept_loop(self):
        while self.is_running:
            try:
                conn, addr = self.server_sock.accept()
                print(f"[WFD-Server] Connection accepted from: {addr}")
                threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()
            except Exception as e:
                if self.is_running:
                    print(f"[WFD-Server] Accept error: {e}")
                break

    def _handle_client(self, conn, addr):
        conn.settimeout(15.0)
        try:
            while self.is_running:
                data = conn.recv(4096)
                if not data:
                    break
                text = data.decode(errors='ignore')
                print(f"\n--- [RTSP IN from {addr[0]}] ---\n{text.strip()}\n")

                response = self._process_rtsp(text, addr[0])
                if response:
                    print(f"--- [RTSP OUT] ---\n{response.strip()}\n")
                    conn.sendall(response.encode())
        except Exception as e:
            print(f"[WFD-Client] Handler error: {e}")
        finally:
            conn.close()
            print(f"[WFD-Client] Connection closed with {addr}")

    def _process_rtsp(self, text, client_ip):
        lines = text.splitlines()
        if not lines:
            return ""

        request_line = lines[0]
        parts = request_line.split()
        if len(parts) < 2:
            return ""
        method = parts[0]
        uri = parts[1]

        # Extract CSeq
        cseq = "1"
        for l in lines:
            if l.lower().startswith("cseq:"):
                cseq = l.split(":", 1)[1].strip()

        if method == "OPTIONS":
            # M1 / M2: Return supported WFD methods
            return (
                f"RTSP/1.0 200 OK\r\n"
                f"CSeq: {cseq}\r\n"
                f"Public: org.wfa.wfd1.0, GET_PARAMETER, SET_PARAMETER, SETUP, PLAY, TEARDOWN\r\n"
                f"\r\n"
            )

        elif method == "GET_PARAMETER":
            # M3: TV asks for source capabilities
            # Inject proprietary Samsung Multi View WFD capabilities
            body = (
                "wfd_video_formats: 00 00 02 02 00000080 00000000 00000000 00 0000 0000 00 none none\r\n"
                "wfd_audio_codecs: none\r\n"
                "wfd_client_rtpports: RTP/AVP/UDP;unicast 1028 0 mode=play\r\n"
                "wfd_sec_view_mode: side_by_side\r\n"
                "wfd_sec_view_side_by_side: 1\r\n"
                "wfd_sec_multiview_focus: 1\r\n"
                "wfd_sec_hw_rotation: 0\r\n"
                "wfd_sec_dmr_support: 1\r\n"
            )
            return (
                f"RTSP/1.0 200 OK\r\n"
                f"CSeq: {cseq}\r\n"
                f"Content-Type: text/parameters\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"\r\n"
                f"{body}"
            )

        elif method == "SET_PARAMETER":
            # M4 / M5: TV sets playback parameters or notifies state
            for l in lines:
                if "wfd_client_rtpports" in l:
                    try:
                        # Extract client port
                        # Example: wfd_client_rtpports: RTP/AVP/UDP;unicast 1028 0 mode=play
                        tokens = l.split()
                        for tok in tokens:
                            if tok.isdigit():
                                self.client_rtp_port = int(tok)
                                print(f"[WFD] Discovered TV RTP port: {self.client_rtp_port}")
                                break
                    except Exception:
                        pass

            return (
                f"RTSP/1.0 200 OK\r\n"
                f"CSeq: {cseq}\r\n"
                f"\r\n"
            )

        elif method == "SETUP":
            # Extract client_port from Transport header
            for l in lines:
                if "client_port=" in l:
                    try:
                        cp = l.split("client_port=")[1].split("-")[0].split(";")[0].strip()
                        self.client_rtp_port = int(cp)
                        print(f"[WFD] Target RTP Port: {self.client_rtp_port}")
                    except Exception:
                        pass

            return (
                f"RTSP/1.0 200 OK\r\n"
                f"CSeq: {cseq}\r\n"
                f"Session: 18274619;timeout=60\r\n"
                f"Transport: RTP/AVP/UDP;unicast;client_port={self.client_rtp_port};server_port=60000-60001\r\n"
                f"\r\n"
            )

        elif method == "PLAY":
            print(f"[WFD] PLAY RECEIVED! Starting ultra-low latency VA-API RTP stream to {client_ip}:{self.client_rtp_port}...")
            self._start_rtp_stream(client_ip, self.client_rtp_port)

            return (
                f"RTSP/1.0 200 OK\r\n"
                f"CSeq: {cseq}\r\n"
                f"Session: 18274619\r\n"
                f"Range: npt=now-\r\n"
                f"RTP-Info: url={uri};seq=1;rtptime=0\r\n"
                f"\r\n"
            )

        elif method == "TEARDOWN":
            self.stop_stream()
            return f"RTSP/1.0 200 OK\r\nCSeq: {cseq}\r\n\r\n"

        return f"RTSP/1.0 200 OK\r\nCSeq: {cseq}\r\n\r\n"

    def _start_rtp_stream(self, target_ip, target_port):
        """Start hardware-accelerated H.264 RTP stream using GStreamer to Samsung TV."""
        self.stop_stream()

        # Modern GStreamer 1.28 VA-API encoder or x264 fallback
        encoder_elem = 'vah264enc'
        encoder_args = ['rate-control=cbr', 'bitrate=15000']

        gst_cmd = [
            'gst-launch-1.0', '-q',
            'pipewiresrc', 'do-timestamp=true',
            '!', 'videoconvert',
            '!', 'video/x-raw,format=NV12,framerate=30/1',
            '!', encoder_elem
        ] + encoder_args + [
            '!', 'rtph264pay', 'config-interval=1', 'pt=96',
            '!', 'udpsink', f'host={target_ip}', f'port={target_port}', 'sync=false'
        ]
        print(f"[Stream] Command: {' '.join(gst_cmd)}")
        try:
            self.gst_process = subprocess.Popen(gst_cmd)
        except Exception as e:
            print(f"[Stream] GStreamer failed: {e}")

    def stop_stream(self):
        if self.gst_process:
            try:
                self.gst_process.terminate()
                self.gst_process.wait(timeout=1)
            except Exception:
                self.gst_process.kill()
            self.gst_process = None

    def stop(self):
        self.is_running = False
        self.stop_stream()
        if self.server_sock:
            try:
                self.server_sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.server_sock.close()
            except Exception:
                pass
            self.server_sock = None

if __name__ == '__main__':
    server = SamsungWFDServer()
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
