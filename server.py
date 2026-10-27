"""
ASUS TUF / ROG Fan Controller Web Dashboard Server
Runs a lightweight, zero-dependency HTTP server with REST API
"""

import http.server
import socketserver
import json
import os
import sys
import webbrowser
import threading
import time
from urllib.parse import urlparse, parse_qs

# Import the core controller
from asus_fan_controller import AsusFanController

PORT = 8990
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

controller = None

class FanAPIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def log_message(self, format, *args):
        # Suppress noisy polling logs in console
        if "/api/status" in args[0]:
            return
        super().log_message(format, *args)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                data = controller.get_telemetry()
                data['success'] = True
            except Exception as e:
                data = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        try:
            payload = json.loads(body.decode('utf-8'))
        except Exception:
            payload = {}

        if parsed.path == '/api/set_mode':
            mode = payload.get('mode', 'auto')
            ok = controller.set_preset(mode)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            resp = {'success': ok, 'mode': controller.active_mode, 'target': controller.target_percentage}
            self.wfile.write(json.dumps(resp).encode('utf-8'))

        elif parsed.path == '/api/set_percentage':
            pct = payload.get('percentage', 100)
            ok = controller.set_manual_percentage(pct)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            resp = {'success': ok, 'mode': controller.active_mode, 'target': controller.target_percentage}
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    global controller
    print("[*] Initializing ASUS Hardware Controller...")
    controller = AsusFanController()
    t = controller.get_telemetry()
    print(f"[+] Connected to ATKACPI! Initial CPU Fan: {t['cpu_rpm']} RPM, GPU Fan: {t['gpu_rpm']} RPM")

    # Reuse address to avoid port conflict
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), FanAPIHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n=======================================================")
        print(f"  ASUS TUF FAN CONTROL DASHBOARD ONLINE")
        print(f"  Access URL: {url}")
        print(f"=======================================================\n")
        print("[*] Press Ctrl+C in this window to stop.")
        
        # Open browser in a separate thread after 1 second
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Stopping server and restoring auto fans...")
        finally:
            if controller:
                controller.reset_to_auto()
                controller.close()
            print("[+] Done. Exited cleanly.")

if __name__ == "__main__":
    run_server()
