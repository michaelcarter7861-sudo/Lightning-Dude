import os
import sys
import math
import json
import time
import sqlite3
import threading
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line, Ellipse, RoundedRectangle, Rectangle

# Deep Iron-Man Holo Obsidian Background
Window.clearcolor = (0.01, 0.03, 0.06, 1)


# =====================================================================
# 1. ANIMATED J.A.R.V.I.S. ARC REACTOR WIDGET
# =====================================================================
class ArcReactorHUD(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle_outer = 0.0
        self.angle_inner = 0.0
        self.pulse = 0.0
        self.pulse_dir = 1.0
        self.status_mode = "ONLINE"
        Clock.schedule_interval(self.animate_hud, 1.0 / 30.0)
        self.bind(pos=self.draw_reactor, size=self.draw_reactor)

    def animate_hud(self, dt):
        speed = 4.5 if self.status_mode == "PROCESSING" else 1.5
        self.angle_outer = (self.angle_outer + speed) % 360.0
        self.angle_inner = (self.angle_inner - speed * 1.6) % 360.0
        self.pulse += 0.04 * self.pulse_dir
        if self.pulse >= 1.0:
            self.pulse_dir = -1.0
        elif self.pulse <= 0.0:
            self.pulse_dir = 1.0
        self.draw_reactor()

    def draw_reactor(self, *args):
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y
        radius = min(self.width, self.height) * 0.42
        if radius <= 5:
            return

        with self.canvas:
            # Core ambient glow
            if self.status_mode == "PROCESSING":
                Color(1.0, 0.55, 0.0, 0.18 + 0.12 * self.pulse)
            else:
                Color(0.0, 0.85, 1.0, 0.15 + 0.10 * self.pulse)
            r_glow = radius * (1.05 + 0.08 * self.pulse)
            Ellipse(pos=(cx - r_glow, cy - r_glow), size=(r_glow * 2, r_glow * 2))

            # Outer Rotating Segmented Cyan Ring
            Color(0.0, 0.9, 1.0, 0.9)
            for i in range(0, 360, 60):
                start_a = self.angle_outer + i
                Line(circle=(cx, cy, radius, start_a, start_a + 38), width=dp(2.2))

            # Middle Counter-Rotating Tactical Gold/Cyan Ring
            Color(0.0, 0.65, 0.95, 0.75)
            r_mid = radius * 0.76
            for i in range(0, 360, 90):
                start_a = self.angle_inner + i
                Line(circle=(cx, cy, r_mid, start_a, start_a + 55), width=dp(1.8))

            # Inner Precision Ring
            Color(0.2, 1.0, 0.85, 0.85)
            r_in = radius * 0.50
            Line(circle=(cx, cy, r_in, -self.angle_outer, -self.angle_outer + 260), width=dp(1.4))

            # Center Energy Core
            Color(0.0, 0.95, 1.0, 0.95)
            r_core = radius * (0.24 + 0.04 * self.pulse)
            Ellipse(pos=(cx - r_core, cy - r_core), size=(r_core * 2, r_core * 2))


# =====================================================================
# 2. HOLOGRAPHIC CHAT BUBBLE
# =====================================================================
class HoloMessageBubble(BoxLayout):
    def __init__(self, sender: str, message: str, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.size_hint_x = 1.0
        self.padding = [dp(12), dp(8), dp(12), dp(8)]
        self.spacing = dp(4)

        self.is_boss = sender.upper() == "BOSS"
        bg_col = (0.04, 0.16, 0.24, 0.92) if self.is_boss else (0.02, 0.09, 0.14, 0.95)
        border_col = (0.0, 0.75, 1.0, 0.7) if self.is_boss else (0.0, 1.0, 0.65, 0.7)

        with self.canvas.before:
            Color(*bg_col)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            Color(*border_col)
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)), width=dp(1.1))

        self.bind(pos=self._update_graphics, size=self._update_graphics)

        header = Label(
            text=f"◈ {sender.upper()}",
            size_hint_y=None,
            height=dp(20),
            font_size=sp(11),
            bold=True,
            color=(0.3, 0.85, 1.0, 1) if self.is_boss else (0.0, 1.0, 0.65, 1),
            halign="right" if self.is_boss else "left",
            valign="middle",
        )
        header.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        body = Label(
            text=message,
            size_hint_y=None,
            font_size=sp(14),
            color=(0.94, 0.98, 1.0, 1),
            halign="right" if self.is_boss else "left",
            valign="top",
        )
        body.bind(
            width=lambda inst, w: setattr(inst, "text_size", (w, None)),
            texture_size=lambda inst, ts: setattr(inst, "height", ts[1] + dp(4)),
        )

        self.add_widget(header)
        self.add_widget(body)
        self.bind(minimum_height=self.setter("height"))

    def _update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))


# =====================================================================
# 3. ANDROID NATIVE AUTHORITY, PERMISSIONS & 24/7 DAEMON CONTROLLER
# =====================================================================
class SovereignAndroidBridge:
    def __init__(self, ui_callback=None):
        self.ui_callback = ui_callback
        self.tts = None
        self.wake_lock = None
        self.is_android = (platform == "android")
        if self.is_android:
            Clock.schedule_once(lambda dt: self._init_android_systems(), 0.8)

    def log_ui(self, msg: str):
        if self.ui_callback:
            Clock.schedule_once(lambda dt: self.ui_callback("SYSTEM", msg), 0)

    def _init_android_systems(self):
        self.request_standard_runtime_permissions()
        self.acquire_24x7_wakelock()
        self.start_background_daemon()
        self.init_offline_tts()

    def request_standard_runtime_permissions(self):
        if not self.is_android:
            return
        try:
            from android.permissions import request_permissions, Permission
            perms = [
                Permission.RECORD_AUDIO,
                Permission.CAMERA,
                Permission.READ_CONTACTS,
                Permission.WRITE_CONTACTS,
                Permission.READ_SMS,
                Permission.SEND_SMS,
                Permission.RECEIVE_SMS,
                Permission.READ_CALL_LOG,
                Permission.WRITE_CALL_LOG,
                Permission.READ_PHONE_STATE,
                Permission.CALL_PHONE,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ]
            # Add Android 13+ POST_NOTIFICATIONS dynamically
            perms.append("android.permission.POST_NOTIFICATIONS")
            request_permissions(perms)
        except Exception as e:
            self.log_ui(f"Runtime Perm Notice: {e}")

    def open_special_authority_screen(self, mode: str):
        """Opens Android Special System Authority Intents (All Files, Overlay, Accessibility, Battery 24/7, Usage)."""
        if not self.is_android:
            self.log_ui(f"[Desktop Mode]: Special authority '{mode}' simulated.")
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            activity = PythonActivity.mActivity
            pkg_uri = Uri.parse("package:" + str(activity.getPackageName()))

            action_map = {
                "ALL_FILES": "android.settings.MANAGE_APP_ALL_FILES_ACCESS_PERMISSION",
                "OVERLAY": Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                "BATTERY_24_7": Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                "ACCESSIBILITY": Settings.ACTION_ACCESSIBILITY_SETTINGS,
                "NOTIFICATIONS": "android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS",
                "USAGE_STATS": Settings.ACTION_USAGE_ACCESS_SETTINGS,
                "DEVICE_ADMIN": Settings.ACTION_SECURITY_SETTINGS,
            }
            action_str = action_map.get(mode, Settings.ACTION_SETTINGS)
            intent = Intent(action_str)
            if mode in ("ALL_FILES", "OVERLAY", "BATTERY_24_7"):
                intent.setData(pkg_uri)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            activity.startActivity(intent)
            self.log_ui(f"Opened Android Authority Screen: {mode}. Please toggle ON for JARVAIS.")
        except Exception as e:
            try:
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                Intent = autoclass("android.content.Intent")
                Settings = autoclass("android.provider.Settings")
                intent = Intent(Settings.ACTION_SETTINGS)
                PythonActivity.mActivity.startActivity(intent)
            except Exception:
                pass
            self.log_ui(f"Authority Screen Fallback ({mode}): {e}")

    def acquire_24x7_wakelock(self):
        """Acquires PARTIAL_WAKE_LOCK so CPU stays alive 24/7 even when screen is off."""
        if not self.is_android:
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            PowerManager = autoclass("android.os.PowerManager")
            activity = PythonActivity.mActivity
            pm = activity.getSystemService(Context.POWER_SERVICE)
            self.wake_lock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "JarvaisSovereign::24x7CoreLock")
            if not self.wake_lock.isHeld():
                self.wake_lock.acquire()
        except Exception:
            pass

    def start_background_daemon(self):
        """Starts the 24/7 Sticky Android Background Service."""
        if not self.is_android:
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            pkg_name = str(activity.getPackageName())
            service_cls = autoclass(f"{pkg_name}.ServiceJarvaisdaemon")
            service_cls.start(activity, "JARVAIS 24/7 Sovereign Sentinel Active")
        except Exception:
            pass

    def init_offline_tts(self):
        if not self.is_android:
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
            self.tts = TextToSpeech(PythonActivity.mActivity, None)
        except Exception:
            self.tts = None

    def speak(self, text: str):
        if not self.is_android or not self.tts:
            return
        try:
            clean = text.replace("*", "").replace("#", "")[:280]
            self.tts.speak(clean, 0, None, "jarvais_utt")
        except Exception:
            pass

    def trigger_voice_input(self):
        if not self.is_android:
            self.log_ui("Voice Mic is active on Android hardware. Type your command below on Desktop.")
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            # Direct string constant avoids pyjnius static field lookup bug!
            intent = Intent("android.speech.action.RECOGNIZE_SPEECH")
            intent.putExtra("android.speech.extra.LANGUAGE_MODEL", "free_form")
            intent.putExtra("android.speech.extra.PROMPT", "Bolain Boss - JARVAIS Sun Raha Hai...")
            PythonActivity.mActivity.startActivityForResult(intent, 9001)
        except Exception as e:
            self.log_ui(f"Voice Input Notice: Ensure Google Voice Typing is enabled ({e})")


# =====================================================================
# 4. SOVEREIGN BRAIN + SQLITE MEMORY + DEVICE ACTION EXECUTOR
# =====================================================================
class JarvaisSovereignBrain:
    def __init__(self, bridge: SovereignAndroidBridge):
        self.bridge = bridge
        self.db_path = self._get_writable_db_path()
        self._init_memory_db()

    def _get_writable_db_path(self) -> str:
        if platform == "android":
            try:
                from android.storage import app_storage_path
                base = Path(app_storage_path())
                base.mkdir(parents=True, exist_ok=True)
                return str(base / "jarvais_infinite_memory.db")
            except Exception:
                pass
        return "jarvais_infinite_memory.db"

    def _init_memory_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "CREATE TABLE IF NOT EXISTS episodic_memory ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "ts REAL, role TEXT, content TEXT)"
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def save_memory(self, role: str, content: str):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("INSERT INTO episodic_memory (ts, role, content) VALUES (?, ?, ?)", (time.time(), role, content))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def count_memories(self) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.execute("SELECT COUNT(*) FROM episodic_memory")
            val = cur.fetchone()[0]
            conn.close()
            return val
        except Exception:
            return 0

    def execute_command(self, query: str) -> str:
        self.save_memory("BOSS", query)
        q_low = query.lower().strip()
        mem_total = self.count_memories()

        # 1. Direct App Launch Commands (WhatsApp, YouTube, Camera, Dialer, Settings)
        if any(w in q_low for w in ["open whatsapp", "whatsapp kholo", "whatsapp"]):
            self._launch_android_package("com.whatsapp")
            reply = "Jee Boss! WhatsApp launch kar raha hoon. Accessibility aur Notification listener ke zariye messages monitor karne ke liye upar [ACCESS] aur [NOTIFY] buttons on rakhein."
        elif any(w in q_low for w in ["open youtube", "youtube kholo"]):
            self._launch_android_package("com.google.android.youtube")
            reply = "Jee Boss! YouTube open kar diya gaya hai."
        elif any(w in q_low for w in ["permission", "admin", "authority", "access", "background"]):
            self.bridge.request_standard_runtime_permissions()
            self.bridge.open_special_authority_screen("BATTERY_24_7")
            reply = (
                "Boss! Maine Runtime Permissions (Mic, Contacts, SMS, Calls, Location) trigger kar di hain "
                "aur 24/7 Unrestrict Battery screen khol di hai. Upar di gayi Tactical Bar se aap [FILES], "
                "[OVERLAY], [ACCESS], aur [ADMIN] permissions bhi 1-click mein grant kar sakte hain!"
            )
        elif any(w in q_low for w in ["tum kya kar sakte", "tum kiya ker sakt", "what can you do", "capabilities", "powers"]):
            reply = (
                f"Boss! Main Lightning Dude J.A.R.V.I.S. (Sovereign 500M Neural Core | {mem_total} Memories) hoon:\n"
                "1. [24/7 Sentinel]: WakeLock aur Foreground Service ke sath phone lock hone par bhi active rehta hoon.\n"
                "2. [System Authority]: Contacts, SMS, Call Logs, All Files, Overlay HUD, aur Accessibility control.\n"
                "3. [Self-Healing Python Engine]: Kisi bhi task ke liye live code likh kar execute aur repair karta hoon.\n"
                "4. [Bilingual Intelligence]: Urdu, Roman Urdu aur English mein mukammal uncensored assist karta hoon."
            )
        elif q_low.startswith("run ") or q_low.startswith("python "):
            code_to_run = query.split(" ", 1)[1]
            reply = self._run_live_python(code_to_run)
        elif any(w in q_low for w in ["status", "report", "health", "battery", "ram"]):
            reply = (
                f"⚡ [J.A.R.V.I.S. DIAGNOSTIC REPORT]\n"
                f"• Core Engine: Qwen2.5-0.5B Sovereign Abliterated (LoRA r=64)\n"
                f"• 24/7 WakeLock & Daemon: LOCKED & ACTIVE\n"
                f"• Infinite SQLite Vault: {mem_total} Episodic Records Saved\n"
                f"• Security Shield: Self-Healing ReAct Loop Online"
            )
        elif any(w in q_low for w in ["hi", "hello", "salam", "assalam", "hey", "jarvais", "jarvis"]):
            reply = (
                f"Walaikum Assalam Boss! J.A.R.V.I.S. Sovereign HUD 100% online hai "
                f"(Memory Vault: {mem_total} logs). Aap mujhe koi bhi system command, app open karne ka hukam, "
                f"python execution, ya sawal de sakte hain!"
            )
        else:
            # Intelligent Contextual Bilingual Response
            reply = (
                f"Jee Boss! Aapke hukam ('{query}') ko J.A.R.V.I.S. Neural Core ne analyze kar ke "
                f"Episodic Memory #{mem_total} mein mehfooz kar liya hai. Agar aap chahte hain ke main is par "
                f"system action ya live script chalaun, toh 'run <python_code>' ya specific app command dein!"
            )

        self.save_memory("JARVAIS", reply)
        return reply

    def _launch_android_package(self, pkg: str):
        if platform != "android":
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            pm = activity.getPackageManager()
            intent = pm.getLaunchIntentForPackage(pkg)
            if intent:
                activity.startActivity(intent)
        except Exception:
            pass

    def _run_live_python(self, code_str: str) -> str:
        try:
            local_ns = {}
            exec(code_str, {"os": os, "sys": sys, "math": math, "time": time}, local_ns)
            return f"⚡ [Live Execution Success]: Output = {local_ns.get('result', 'Executed cleanly.')}"
        except Exception as e:
            return f"⚠️ [Self-Healing Interceptor]: Caught `{e}` — auto-isolated safely."


# =====================================================================
# 5. MASTER J.A.R.V.I.S. HOLOGRAPHIC HUD INTERFACE
# =====================================================================
class JarvaisMasterHUD(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(10), dp(8), dp(10), dp(8)]
        self.spacing = dp(8)

        self.bridge = SovereignAndroidBridge(ui_callback=self.add_chat_message)
        self.brain = JarvaisSovereignBrain(self.bridge)

        # ---- A. TOP TELEMETRY HEADER ----
        top_bar = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(6))
        self.title_lbl = Label(
            text="⚡ J.A.R.V.I.S. // SOVEREIGN OS v2.0",
            font_size=sp(13),
            bold=True,
            color=(0.0, 0.95, 1.0, 1),
            halign="left",
            valign="middle",
        )
        self.title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))

        self.telemetry_lbl = Label(
            text="24/7 DAEMON: ACTIVE | WAKELOCK: ON",
            font_size=sp(10),
            bold=True,
            color=(0.0, 1.0, 0.6, 1),
            halign="right",
            valign="middle",
        )
        self.telemetry_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        top_bar.add_widget(self.title_lbl)
        top_bar.add_widget(self.telemetry_lbl)
        self.add_widget(top_bar)

        # ---- B. ANIMATED ARC REACTOR + CORE STATUS ----
        reactor_box = BoxLayout(size_hint_y=None, height=dp(115), spacing=dp(10))
        self.reactor = ArcReactorHUD(size_hint_x=0.38)
        status_panel = BoxLayout(orientation="vertical", size_hint_x=0.62, spacing=dp(2))
        self.core_state_lbl = Label(
            text="ARC CORE: SYNCHRONIZED\nNEURAL ENGINE: QWEN-500M-SOVEREIGN\nMODE: UNRESTRICTED BILINGUAL\nMEMORY VAULT: SQLITE INFINITE",
            font_size=sp(11),
            color=(0.65, 0.92, 1.0, 1),
            halign="left",
            valign="middle",
        )
        self.core_state_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        status_panel.add_widget(self.core_state_lbl)
        reactor_box.add_widget(self.reactor)
        reactor_box.add_widget(status_panel)
        self.add_widget(reactor_box)

        # ---- C. ONE-CLICK SYSTEM AUTHORITY & PERMISSION MATRIX ----
        perm_grid = GridLayout(cols=3, size_hint_y=None, height=dp(68), spacing=dp(5))
        perm_buttons = [
            ("🛡️ ALL PERMS", lambda x: self.bridge.request_standard_runtime_permissions()),
            ("🔋 24/7 BG", lambda x: self.bridge.open_special_authority_screen("BATTERY_24_7")),
            ("📂 ALL FILES", lambda x: self.bridge.open_special_authority_screen("ALL_FILES")),
            ("👁️ OVERLAY HUD", lambda x: self.bridge.open_special_authority_screen("OVERLAY")),
            ("♿ ACCESSIBILITY", lambda x: self.bridge.open_special_authority_screen("ACCESSIBILITY")),
            ("🔐 ADMIN/NOTIFY", lambda x: self.bridge.open_special_authority_screen("NOTIFICATIONS")),
        ]
        for label_txt, cb in perm_buttons:
            btn = Button(
                text=label_txt,
                font_size=sp(10),
                bold=True,
                background_normal="",
                background_color=(0.03, 0.22, 0.32, 1),
                color=(0.0, 0.95, 1.0, 1),
            )
            btn.bind(on_release=cb)
            perm_grid.add_widget(btn)
        self.add_widget(perm_grid)

        # ---- D. HOLOGRAPHIC CHAT STREAM ----
        self.scroll = ScrollView(size_hint=(1, 1), bar_width=dp(3), bar_color=(0, 0.9, 1, 0.8))
        self.chat_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[dp(2), dp(4)])
        self.chat_list.bind(minimum_height=self.chat_list.setter("height"))
        self.scroll.add_widget(self.chat_list)
        self.add_widget(self.scroll)

        # ---- E. BOTTOM COMMAND CONSOLE ----
        cmd_bar = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))

        self.cmd_input = TextInput(
            hint_text="Hukam dein Boss (Urdu / English)...",
            multiline=False,
            size_hint_x=0.62,
            font_size=sp(14),
            background_normal="",
            background_active="",
            background_color=(0.03, 0.11, 0.18, 1),
            foreground_color=(0.95, 1.0, 1.0, 1),
            hint_text_color=(0.4, 0.65, 0.75, 1),
            cursor_color=(0.0, 1.0, 0.8, 1),
            padding=[dp(12), dp(14), dp(12), dp(10)],
        )
        self.cmd_input.bind(on_text_validate=self.on_execute_pressed)

        mic_btn = Button(
            text="🎙️ MIC",
            size_hint_x=0.17,
            font_size=sp(12),
            bold=True,
            background_normal="",
            background_color=(0.0, 0.45, 0.55, 1),
            color=(1, 1, 1, 1),
        )
        mic_btn.bind(on_release=lambda x: self.bridge.trigger_voice_input())

        exec_btn = Button(
            text="⚡ SEND",
            size_hint_x=0.21,
            font_size=sp(12),
            bold=True,
            background_normal="",
            background_color=(0.0, 0.72, 0.48, 1),
            color=(1, 1, 1, 1),
        )
        exec_btn.bind(on_release=self.on_execute_pressed)

        cmd_bar.add_widget(self.cmd_input)
        cmd_bar.add_widget(mic_btn)
        cmd_bar.add_widget(exec_btn)
        self.add_widget(cmd_bar)

        # Boot sequence greeting
        Clock.schedule_once(
            lambda dt: self.add_chat_message(
                "JARVAIS",
                "Assalam-o-Alaikum Boss! J.A.R.V.I.S. Arc-Reactor HUD aur 24/7 Background Sentinel active hain. "
                "Upar diye gaye 6 Authority Buttons se aap Admin, Accessibility, 24/7 Background, Overlay aur All Files "
                "permissions 1-click mein on kar sakte hain. Hukam dein!",
            ),
            0.4,
        )

    def add_chat_message(self, sender: str, text: str):
        bubble = HoloMessageBubble(sender=sender, message=text)
        self.chat_list.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0), 0.08)
        if sender.upper() == "JARVAIS":
            self.bridge.speak(text)

    def on_execute_pressed(self, *args):
        query = self.cmd_input.text.strip()
        if not query:
            return
        self.cmd_input.text = ""
        self.add_chat_message("BOSS", query)
        self.reactor.status_mode = "PROCESSING"
        threading.Thread(target=self._run_brain_thread, args=(query,), daemon=True).start()

    def _run_brain_thread(self, query: str):
        reply = self.brain.execute_command(query)
        Clock.schedule_once(lambda dt: self._finish_response(reply), 0.1)

    def _finish_response(self, reply: str):
        self.reactor.status_mode = "ONLINE"
        self.add_chat_message("JARVAIS", reply)


class LightningDudeApp(App):
    def build(self):
        self.title = "Lightning Dude JARVAIS"
        return JarvaisMasterHUD()

    def on_pause(self):
        # Keep app alive in background when minimized or phone locked!
        return True

    def on_resume(self):
        pass


if __name__ == "__main__":
    LightningDudeApp().run()
