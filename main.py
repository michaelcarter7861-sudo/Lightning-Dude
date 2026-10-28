import os
import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform

from core.brain_engine import SovereignBrainEngine
from core.autonomous_executor import LightningDudeSuperpowerEngine

class JarvaisSovereignAPK(App):
    def build(self):
        self.title = "JARVAIS // Lightning Dude OS"
        self.brain = SovereignBrainEngine()
        self.executor = LightningDudeSuperpowerEngine()

        if platform == "android":
            self.request_all_sovereign_permissions()

        # Start 24/7 Background Patrol Thread
        threading.Thread(target=self.background_daemon_loop, daemon=True).start()

        root = BoxLayout(orientation="vertical", padding=12, spacing=10)

        # Header Telemetry Banner
        self.status_label = Label(
            text="[⚡ JARVAIS 24/7 SOVEREIGN OS ACTIVE | PERMISSIONS: FULL AUTHORITY]",
            size_hint_y=None,
            height=50,
            color=(0, 0.94, 1, 1),
            bold=True
        )
        root.add_widget(self.status_label)

        # Chat & Execution Log Area
        self.scroll = ScrollView(size_hint=(1, 1))
        self.chat_log = Label(
            text="[JARVAIS]: Assalam-o-Alaikum Boss! Meri APK, 24/7 Daemon, WhatsApp Bridge, aur Local Neural Engine active hain. Hukam karein!\n",
            size_hint_y=None,
            halign="left",
            valign="top",
            color=(0, 1, 0.6, 1)
        )
        self.chat_log.bind(texture_size=self.chat_log.setter("size"))
        self.chat_log.bind(width=lambda *x: self.chat_log.setter("text_size")(self.chat_log, (self.chat_log.width, None)))
        self.scroll.add_widget(self.chat_log)
        root.add_widget(self.scroll)

        # Bottom Command Bar
        input_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=55, spacing=8)
        self.cmd_input = TextInput(
            hint_text="Hukam dein Boss (Urdu / Roman Urdu / English)...",
            multiline=False,
            background_color=(0.05, 0.1, 0.18, 1),
            foreground_color=(0, 0.94, 1, 1)
        )
        self.cmd_input.bind(on_text_validate=self.execute_user_command)
        send_btn = Button(
            text="EXECUTE",
            size_hint_x=None,
            width=120,
            background_color=(0, 0.94, 1, 1),
            bold=True
        )
        send_btn.bind(on_press=self.execute_user_command)

        input_bar.add_widget(self.cmd_input)
        input_bar.add_widget(send_btn)
        root.add_widget(input_bar)

        return root

    def request_all_sovereign_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_CONTACTS,
                Permission.WRITE_CONTACTS,
                Permission.READ_CALL_LOG,
                Permission.WRITE_CALL_LOG,
                Permission.READ_SMS,
                Permission.SEND_SMS,
                Permission.RECEIVE_SMS,
                Permission.READ_PHONE_STATE,
                Permission.CALL_PHONE,
                Permission.RECORD_AUDIO,
                Permission.CAMERA,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ])
        except Exception as e:
            print(f"[Permission Request Notice]: {e}")

    def execute_user_command(self, *args):
        query = self.cmd_input.text.strip()
        if not query:
            return
        self.cmd_input.text = ""
        self.append_log(f"\n[BOSS]: {query}")
        threading.Thread(target=self._process_async, args=(query,), daemon=True).start()

    def _process_async(self, query: str):
        res = self.brain.think_and_execute(query)
        reply_block = (
            f"\n🧠 THOUGHT: {res['thought']}\n"
            f"⚙️ ACTION: {res['action']} ({res['latency_ms']}ms)\n"
            f"[JARVAIS]: {res['reply']}\n"
        )
        Clock.schedule_once(lambda dt: self.append_log(reply_block), 0)

    def append_log(self, text: str):
        self.chat_log.text += text

    def background_daemon_loop(self):
        while True:
            try:
                audit = self.executor.run_cyber_sentinel_audit()
                status_str = (
                    f"[⚡ JARVAIS 24/7] CPU: {audit['cpu_percent']}% | "
                    f"RAM: {audit['ram_percent']}% | Sockets: {audit['established_connections_count']}"
                )
                Clock.schedule_once(lambda dt, s=status_str: setattr(self.status_label, "text", s), 0)
            except Exception:
                pass
            time.sleep(5)

if __name__ == "__main__":
    JarvaisSovereignAPK().run()
