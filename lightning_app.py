import json
import time
import threading
import psutil
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.brain_engine import SovereignBrainEngine

BRAIN = SovereignBrainEngine()
DAEMON_TELEMETRY = {
    "agent": "JARVAIS (Lightning Dude OS)",
    "status": "ONLINE - 24/7 AUTONOMOUS DAEMON",
    "cpu_percent": 0.0,
    "ram_percent": 0.0,
    "active_sockets": 0,
    "uptime_seconds": 0,
    "last_patrol_event": "Initializing 24/7 Cyber & OS Patrol..."
}
START_TIME = time.time()

def background_24_7_daemon():
    """Runs 24/7 in the background monitoring OS health, sockets, and tasks."""
    while True:
        try:
            DAEMON_TELEMETRY["cpu_percent"] = psutil.cpu_percent(interval=1)
            DAEMON_TELEMETRY["ram_percent"] = psutil.virtual_memory().percent
            conns = psutil.net_connections(kind="inet")
            DAEMON_TELEMETRY["active_sockets"] = len([c for c in conns if c.status == "ESTABLISHED"])
            DAEMON_TELEMETRY["uptime_seconds"] = int(time.time() - START_TIME)
            DAEMON_TELEMETRY["last_patrol_event"] = (
                f"Patrol OK | CPU: {DAEMON_TELEMETRY['cpu_percent']}% | "
                f"RAM: {DAEMON_TELEMETRY['ram_percent']}% | Active Sockets: {DAEMON_TELEMETRY['active_sockets']}"
            )
        except Exception as e:
            DAEMON_TELEMETRY["last_patrol_event"] = f"Daemon scan note: {e}"
        time.sleep(5)

HTML_HUD_GUI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JARVAIS // Lightning Dude 24/7 Sovereign OS</title>
<style>
  body { background: #050b14; color: #00f0ff; font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
  .hud-header { border: 1px solid #00f0ff; padding: 15px; border-radius: 8px; background: rgba(0, 240, 255, 0.05); box-shadow: 0 0 15px rgba(0,240,255,0.2); }
  .telemetry { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 15px; }
  .card { flex: 1; min-width: 140px; border: 1px solid #007799; padding: 12px; border-radius: 6px; background: #081526; }
  #chat-box { height: 360px; overflow-y: auto; border: 1px solid #00f0ff; margin-top: 20px; padding: 15px; border-radius: 8px; background: #04080f; }
  .msg-user { color: #ffffff; margin: 10px 0; }
  .msg-jarvais { color: #00ff9d; margin: 10px 0; white-space: pre-wrap; }
  .msg-meta { color: #ffaa00; font-size: 12px; }
  .input-bar { display: flex; gap: 10px; margin-top: 15px; }
  input { flex: 1; padding: 12px; background: #081526; border: 1px solid #00f0ff; color: #00f0ff; border-radius: 6px; font-size: 16px; }
  button { padding: 12px 24px; background: #00f0ff; color: #050b14; border: none; font-weight: bold; border-radius: 6px; cursor: pointer; }
</style>
</head>
<body>
  <div class="hud-header">
    <h2>⚡ J.A.R.V.A.I.S. // LIGHTNING DUDE SOVEREIGN APPLICATION</h2>
    <div id="patrol-status">Initializing 24/7 Background Daemon...</div>
    <div class="telemetry">
      <div class="card">CPU LOAD: <span id="cpu">--</span>%</div>
      <div class="card">RAM USAGE: <span id="ram">--</span>%</div>
      <div class="card">ACTIVE SOCKETS: <span id="sockets">--</span></div>
      <div class="card">UPTIME: <span id="uptime">--</span>s</div>
    </div>
  </div>
  <div id="chat-box">
    <div class="msg-jarvais">[JARVAIS]: Assalam-o-Alaikum Boss! Main JARVAIS hoon. Mera 24/7 background daemon aur local neural engine active hai. Hukam karein!</div>
  </div>
  <div class="input-bar">
    <input type="text" id="cmd" placeholder="Ask JARVAIS in Urdu, Roman Urdu, or English..." onkeydown="if(event.key==='Enter')sendCmd()">
    <button onclick="sendCmd()">EXECUTE</button>
  </div>
<script>
async function refreshTelemetry() {
  try {
    const r = await fetch('/telemetry');
    const d = await r.json();
    document.getElementById('cpu').innerText = d.cpu_percent;
    document.getElementById('ram').innerText = d.ram_percent;
    document.getElementById('sockets').innerText = d.active_sockets;
    document.getElementById('uptime').innerText = d.uptime_seconds;
    document.getElementById('patrol-status').innerText = d.last_patrol_event;
  } catch(e) {}
}
setInterval(refreshTelemetry, 3000);
refreshTelemetry();

async function sendCmd() {
  const inp = document.getElementById('cmd');
  const q = inp.value.trim();
  if(!q) return;
  inp.value = '';
  const box = document.getElementById('chat-box');
  box.innerHTML += `<div class="msg-user"><b>[BOSS]:</b> ${q}</div>`;
  box.scrollTop = box.scrollHeight;
  const r = await fetch('/command', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({query:q})});
  const res = await r.json();
  box.innerHTML += `<div class="msg-meta">🧠 THOUGHT: ${res.thought} | ⚙️ ACTION: ${res.action} (${res.latency_ms}ms)</div>`;
  box.innerHTML += `<div class="msg-jarvais"><b>[JARVAIS]:</b> ${res.reply}</div>`;
  box.scrollTop = box.scrollHeight;
}
</script>
</body>
</html>
"""

class JarvaisAppHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == "/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(DAEMON_TELEMETRY).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_HUD_GUI.encode("utf-8"))

    def do_POST(self):
        if self.path == "/command":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            query = body.get("query", "")
            result = BRAIN.think_and_execute(query)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

if __name__ == "__main__":
    t = threading.Thread(target=background_24_7_daemon, daemon=True)
    t.start()
    port = 8080
    print("=========================================================================")
    print(f"⚡ JARVAIS // LIGHTNING DUDE 24/7 APPLICATION LIVE AT: http://127.0.0.1:{port}")
    print("=========================================================================")
    HTTPServer(("0.0.0.0", port), JarvaisAppHandler).serve_forever()
