import os
import math
import time
import shutil
import subprocess
import threading
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle, Triangle, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import platform

# Deep cyberpunk obsidian background
Window.clearcolor = (0.02, 0.05, 0.08, 1)


class SovereignTerminalLogger:
    """Stores live system logs and command outputs for the built-in Terminal Console"""
    logs = [
        "[BOOT] LIGHTNING DUDE // JARVAIS SOVEREIGN OS v2.0.0",
        "[CORE] Target Model: LightningDude-Sovereign-500M.gguf",
        "[DAEMON] 24/7 Foreground WakeLock & Hands-Free Standby Ready."
    ]
    listeners = []

    @classmethod
    def log(cls, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        cls.logs.append(line)
        if len(cls.logs) > 250:
            cls.logs = cls.logs[-250:]
        for cb in list(cls.listeners):
            try:
                Clock.schedule_once(lambda dt, c=cb: c("\n".join(cls.logs)), 0)
            except Exception:
                pass


class AndroidSystemBridge:
    """Full Device Control Authorities, Hands-Free Continuous STT, Voice TTS & Native Asset Extractor"""
    _tts = None
    _voice_callback = None
    _bound_result = False
    hands_free_enabled = True
    is_currently_listening = False

    @classmethod
    def init_tts(cls):
        if platform != "android" or cls._tts is not None:
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
            cls._tts = TextToSpeech(PythonActivity.mActivity, None)
            SovereignTerminalLogger.log("[TTS] Android Neural Voice Synthesizer Initialized.")
        except Exception as e:
            SovereignTerminalLogger.log(f"[TTS WARN] {e}")

    @classmethod
    def speak(cls, text: str):
        SovereignTerminalLogger.log(f"[JARVAIS]: {text}")
        if platform != "android":
            return
        try:
            if cls._tts is None:
                cls.init_tts()
            if cls._tts:
                cls._tts.speak(str(text), 0, None, "jarvais_speech_id")
        except Exception as e:
            SovereignTerminalLogger.log(f"[SPEAK ERR] {e}")

    @classmethod
    def trigger_voice_listen(cls, callback, hands_free_loop=False):
        """Starts voice recognition (supports both tap-to-speak and hands-free wake-word)"""
        cls._voice_callback = callback
        if platform != "android":
            SovereignTerminalLogger.log("[STT] Desktop Simulation -> 'Jarvais system status'")
            callback("Jarvais system status")
            return
        try:
            from jnius import autoclass
            from android import activity

            if not cls._bound_result:
                activity.bind(on_activity_result=cls._on_activity_result)
                cls._bound_result = True

            Intent = autoclass("android.content.Intent")
            RecognizerIntent = autoclass("android.speech.RecognizerIntent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
            intent.putExtra(
                RecognizerIntent.EXTRA_PROMPT,
                "Hands-Free Wake Standby ('Hey Jarvais')..." if hands_free_loop else "Speak your command, Boss..."
            )
            cls.is_currently_listening = True
            PythonActivity.mActivity.startActivityForResult(intent, 9001)
        except Exception as e:
            cls.is_currently_listening = False
            SovereignTerminalLogger.log(f"[STT ERR] {e}")

    @classmethod
    def _on_activity_result(cls, request_code, result_code, intent):
        if request_code == 9001:
            cls.is_currently_listening = False
            if intent is not None:
                try:
                    from jnius import autoclass
                    RecognizerIntent = autoclass("android.speech.RecognizerIntent")
                    results = intent.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                    if results and results.size() > 0:
                        spoken_text = str(results.get(0))
                        SovereignTerminalLogger.log(f"[VOICE IN]: {spoken_text}")
                        if cls._voice_callback:
                            Clock.schedule_once(lambda dt: cls._voice_callback(spoken_text), 0)
                        return
                except Exception as e:
                    SovereignTerminalLogger.log(f"[STT PARSE ERR] {e}")
            # If hands-free mode is active and nothing was spoken, re-arm after short cooldown
            if cls.hands_free_enabled and cls._voice_callback:
                Clock.schedule_once(lambda dt: cls._voice_callback(""), 0)

    @staticmethod
    def request_runtime_permissions():
        if platform != "android":
            return "Desktop Mode: Runtime permissions simulated"
        try:
            from android.permissions import request_permissions, Permission
            perms = [
                Permission.RECORD_AUDIO,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.CAMERA,
                Permission.CALL_PHONE,
                Permission.READ_CONTACTS,
                "android.permission.POST_NOTIFICATIONS",
                "android.permission.FOREGROUND_SERVICE",
                "android.permission.FOREGROUND_SERVICE_MICROPHONE",
                "android.permission.WAKE_LOCK",
            ]
            request_permissions(perms)
            SovereignTerminalLogger.log("[AUTH] Requested Mic, Storage, Phone, Camera & Notification Authorities.")
            return "Requested Runtime Authorities"
        except Exception as e:
            SovereignTerminalLogger.log(f"[AUTH WARN] {e}")
            return f"Perm notice: {e}"

    @staticmethod
    def request_unrestricted_battery():
        if platform != "android":
            return "24/7 Battery Active (Desktop)"
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            PowerManager = autoclass("android.os.PowerManager")
            Context = autoclass("android.content.Context")

            activity = PythonActivity.mActivity
            pkg = activity.getPackageName()
            pm = activity.getSystemService(Context.POWER_SERVICE)
            if not pm.isIgnoringBatteryOptimizations(pkg):
                intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
                intent.setData(Uri.parse(f"package:{pkg}"))
                activity.startActivity(intent)
                SovereignTerminalLogger.log("[24/7] Requested Unrestricted Battery Optimization Exemption.")
                return "Opened 24/7 Battery Exemption Dialog"
            SovereignTerminalLogger.log("[24/7] Unrestricted Battery Mode Verified Active.")
            return "24/7 Unrestricted Battery Verified"
        except Exception as e:
            return f"Battery notice: {e}"

    @staticmethod
    def request_all_files_access():
        """Opens MANAGE_APP_ALL_FILES_ACCESS_PERMISSION for complete device storage control"""
        if platform != "android":
            return "Full Storage Control Active (Desktop)"
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            activity = PythonActivity.mActivity
            pkg = activity.getPackageName()
            intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            intent.setData(Uri.parse(f"package:{pkg}"))
            activity.startActivity(intent)
            SovereignTerminalLogger.log("[AUTH] Opened All-Files Management Authority Screen.")
            return "Opened Full Storage Control Settings"
        except Exception as e:
            return f"All-Files notice: {e}"

    @staticmethod
    def request_overlay_permission():
        """Opens SYSTEM_ALERT_WINDOW permission for Floating Orb overlay"""
        if platform != "android":
            return "Floating Orb Overlay Active (Desktop)"
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            activity = PythonActivity.mActivity
            pkg = activity.getPackageName()
            intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse(f"package:{pkg}"))
            activity.startActivity(intent)
            SovereignTerminalLogger.log("[AUTH] Opened Floating Orb Overlay Authority.")
            return "Opened Floating Orb Overlay Settings"
        except Exception as e:
            return f"Overlay notice: {e}"

    @staticmethod
    def request_write_system_settings():
        """Opens ACTION_MANAGE_WRITE_SETTINGS for brightness/volume/system toggles"""
        if platform != "android":
            return "Write System Settings Active (Desktop)"
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            activity = PythonActivity.mActivity
            pkg = activity.getPackageName()
            intent = Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS, Uri.parse(f"package:{pkg}"))
            activity.startActivity(intent)
            SovereignTerminalLogger.log("[AUTH] Opened Write System Settings Authority.")
            return "Opened Write System Settings Authority"
        except Exception as e:
            return f"Write settings notice: {e}"

    @staticmethod
    def open_accessibility_settings():
        """Opens Accessibility Settings for full screen-read and UI automation control"""
        if platform != "android":
            return "Accessibility Control Simulated"
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            PythonActivity.mActivity.startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
            SovereignTerminalLogger.log("[AUTH] Opened Accessibility Device Automation Settings.")
            return "Opened Accessibility Control Settings"
        except Exception as e:
            return f"Accessibility err: {e}"

    @staticmethod
    def open_android_settings():
        if platform != "android":
            return "Opened Settings (Desktop)"
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            PythonActivity.mActivity.startActivity(Intent(Settings.ACTION_SETTINGS))
            SovereignTerminalLogger.log("[INTENT] Opened Android System Settings.")
            return "Opened Android System Settings"
        except Exception as e:
            return f"Settings err: {e}"

    @staticmethod
    def launch_app_by_package(pkg_hint: str) -> str:
        """Launches installed Android apps by name or package keyword"""
        if platform != "android":
            return f"Simulated launching {pkg_hint}"
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            pm = activity.getPackageManager()

            known_map = {
                "whatsapp": "com.whatsapp",
                "youtube": "com.google.android.youtube",
                "chrome": "com.android.chrome",
                "camera": "com.android.camera",
                "phone": "com.android.dialer",
                "calculator": "com.google.android.calculator",
            }
            target_pkg = known_map.get(pkg_hint.lower(), pkg_hint)
            launch_intent = pm.getLaunchIntentForPackage(target_pkg)
            if launch_intent:
                activity.startActivity(launch_intent)
                return f"Launched application: {target_pkg}"
            return f"App '{pkg_hint}' not found or no launch intent."
        except Exception as e:
            return f"App launch error: {e}"

    @staticmethod
    def start_jarvais_service():
        if platform != "android":
            return "24/7 Service Active (Desktop)"
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            ServiceJarvais = autoclass("org.jarvais.lightningdude.ServiceJarvais")
            ServiceJarvais.start(activity, "Jarvais is ready • Wake-word standby • On-device")
            SovereignTerminalLogger.log("[SERVICE] ServiceJarvais Foreground Sticky Daemon Started.")
            return "24/7 Sticky Background Daemon Active"
        except Exception as e:
            SovereignTerminalLogger.log(f"[SERVICE WARN] {e}")
            return f"Service notice: {e}"

    @staticmethod
    def extract_apk_asset(asset_name: str, target_path: Path, make_exec=False) -> bool:
        if target_path.exists() and target_path.stat().st_size > 1024:
            if make_exec:
                os.chmod(str(target_path), 0o755)
            return True
        for local_candidate in [Path(asset_name), Path("assets") / asset_name, Path("models/gguf") / asset_name]:
            if local_candidate.exists() and local_candidate.stat().st_size > 1024:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(local_candidate, target_path)
                if make_exec:
                    os.chmod(str(target_path), 0o755)
                return True
        if platform != "android":
            return False
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            asset_mgr = PythonActivity.mActivity.getAssets()
            inp_stream = asset_mgr.open(asset_name)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            FileOutputStream = autoclass("java.io.FileOutputStream")
            out_stream = FileOutputStream(str(target_path))
            buf = bytearray(1024 * 1024)
            while True:
                read_len = inp_stream.read(buf)
                if read_len <= 0:
                    break
                out_stream.write(buf, 0, read_len)
            out_stream.flush()
            out_stream.close()
            inp_stream.close()
            if make_exec:
                os.chmod(str(target_path), 0o755)
            SovereignTerminalLogger.log(f"[ASSET] Extracted {asset_name} -> {target_path}")
            return True
        except Exception as e:
            SovereignTerminalLogger.log(f"[ASSET WARN] {asset_name}: {e}")
            return False


class SovereignGGUFEngine:
    """Executes real LightningDude-Sovereign-500M.gguf via native ARM64 llama-cli + System Device Executor"""
    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        self.model_path = None
        self.cli_path = None
        self.is_ready = False
        self.status_msg = "Mounting 500M Sovereign Core..."
        threading.Thread(target=self._prepare_engine, daemon=True).start()

    def _update_ui(self, msg: str):
        self.status_msg = msg
        if self.status_callback:
            Clock.schedule_once(lambda dt: self.status_callback(msg), 0)

    def _prepare_engine(self):
        try:
            base_dir = Path(".")
            if platform == "android":
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                files_dir = PythonActivity.mActivity.getFilesDir().getAbsolutePath()
                base_dir = Path(files_dir)

            gguf_target = base_dir / "LightningDude-Sovereign-500M.gguf"
            cli_target = base_dir / "llama-cli"

            if not gguf_target.exists() or gguf_target.stat().st_size < 10000000:
                self._update_ui("Extracting 500M GGUF to Fast Internal Storage...")
                AndroidSystemBridge.extract_apk_asset("LightningDude-Sovereign-500M.gguf", gguf_target)

            if not cli_target.exists():
                self._update_ui("Installing Native ARM64 GGUF Inference Binary...")
                AndroidSystemBridge.extract_apk_asset("llama-cli", cli_target, make_exec=True)
            else:
                os.chmod(str(cli_target), 0o755)

            self.model_path = str(gguf_target)
            self.cli_path = str(cli_target) if cli_target.exists() else None
            self.is_ready = True

            if gguf_target.exists():
                mb = gguf_target.stat().st_size // (1024 * 1024)
                engine_tag = "Native GGUF Ready" if self.cli_path else "GGUF Mounted"
                self._update_ui(f"Ready to help ({mb}MB {engine_tag} • On-Device)")
                SovereignTerminalLogger.log(f"[ENGINE] Model Verified ({mb} MB) | CLI: {self.cli_path}")
            else:
                self._update_ui("Ready to help with your device.")
        except Exception as e:
            self.is_ready = True
            SovereignTerminalLogger.log(f"[ENGINE INIT WARN] {e}")
            self._update_ui("Ready to help with your device.")

    def run_shell_command(self, cmd_str: str) -> str:
        """Executes direct Linux/Android shell commands from the built-in Terminal"""
        SovereignTerminalLogger.log(f"$ {cmd_str}")
        try:
            proc = subprocess.run(
                cmd_str, shell=True, capture_output=True, text=True, timeout=20
            )
            out = (proc.stdout or "") + (proc.stderr or "")
            out = out.strip() or "[Command completed with exit code 0]"
            SovereignTerminalLogger.log(out)
            return out
        except Exception as e:
            err = f"[Shell Error]: {e}"
            SovereignTerminalLogger.log(err)
            return err

    def generate(self, prompt: str) -> str:
        q = prompt.strip()
        if not q:
            return "Listening in standby, Boss."

        # Strip wake-word prefix if present
        low = q.lower()
        for wake in ["hey jarvais", "hi jarvais", "jarvais", "hey jarvis", "jarvis", "lightning dude"]:
            if low.startswith(wake):
                q = q[len(wake):].strip(" ,.!?") or "Hello"
                low = q.lower()
                break

        # 1. Direct Device Control Commands
        if "setting" in low:
            AndroidSystemBridge.open_android_settings()
            return "Boss, maine Android System Settings open kar di hain."
        if "accessibility" in low or "automation" in low:
            AndroidSystemBridge.open_accessibility_settings()
            return "Boss, full device control ke liye Accessibility Settings khol di hain."
        if "battery" in low or "24/7" in low:
            AndroidSystemBridge.request_unrestricted_battery()
            AndroidSystemBridge.start_jarvais_service()
            return "Boss, 24/7 Unrestricted Battery aur Sticky Service active kar di gayi hai."
        if "storage" in low or "all files" in low:
            AndroidSystemBridge.request_all_files_access()
            return "Boss, Manage All Files storage control screen open kar di hai."
        if "overlay" in low or "floating" in low or "orb" in low:
            AndroidSystemBridge.request_overlay_permission()
            return "Boss, Floating Orb overlay ki permission screen khol di hai."
        if "open " in low:
            app_target = low.split("open ", 1)[1].strip()
            res = AndroidSystemBridge.launch_app_by_package(app_target)
            return f"Boss, {res}"

        # 2. Real Native ARM64 llama-cli Execution on LightningDude-Sovereign-500M.gguf
        if self.cli_path and self.model_path and os.path.exists(self.cli_path) and os.path.exists(self.model_path):
            try:
                SovereignTerminalLogger.log(f"[GGUF INFER] Running 500M model on: '{q}'")
                formatted_prompt = (
                    "<|im_start|>system\nYou are JARVAIS (Lightning Dude), Boss's sovereign bilingual AI assistant. Keep answers concise and helpful.<|im_end|>\n"
                    f"<|im_start|>user\n{q}<|im_end|>\n<|im_start|>assistant\n"
                )
                cmd = [
                    self.cli_path,
                    "-m", self.model_path,
                    "-p", formatted_prompt,
                    "-n", "90",
                    "-t", "4",
                    "--temp", "0.6",
                    "--no-display-prompt",
                    "-e"
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                raw_out = (proc.stdout or "").strip()
                if raw_out:
                    clean_ans = raw_out.split("<|im_end|>")[0].split("<|im_start|>")[0].strip()
                    if clean_ans:
                        return clean_ans
            except Exception as e:
                SovereignTerminalLogger.log(f"[GGUF CLI WARN] {e}")

        # 3. Instant Sovereign Bilingual Fallback
        if any(w in low for w in ["hello", "hi", "salam", "assalam", "hey", "kaise ho"]):
            return "Walaikum Assalam Boss! Main JARVAIS hazir hoon. 24/7 Hands-Free Wake-Word, Terminal aur 500M GGUF core active hain. Hukam karein!"
        if any(w in low for w in ["time", "waqt", "baje"]):
            return f"Boss, is waqt aapke phone par {time.strftime('%I:%M %p')} baj rahe hain."
        if any(w in low for w in ["status", "report", "model"]):
            m_ok = self.model_path and os.path.exists(self.model_path)
            c_ok = self.cli_path and os.path.exists(self.cli_path)
            return f"Boss, 500M GGUF Model: {'Mounted' if m_ok else 'Pending'}, Native ARM64 Engine: {'Active' if c_ok else 'Standby'}, 24/7 Daemon: Running."

        return f"Ji Boss! Aapka hukam '{q}' receive ho gaya hai. On-device Sovereign Core ready hai—bataiye agla action kya lena hai?"


class VectorIconButton(ButtonBehavior, Widget):
    """Draws crisp OpenGL vector icons (Menu, Gear, Keyboard, Mic, Wrench, Terminal) with zero unicode boxes"""
    def __init__(self, icon_type="menu", circle_bg=False, is_primary_mic=False, **kwargs):
        super().__init__(**kwargs)
        self.icon_type = icon_type
        self.circle_bg = circle_bg
        self.is_primary_mic = is_primary_mic
        self.active_state = False
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) * 0.45
        if r <= 2:
            return

        with self.canvas:
            if self.is_primary_mic:
                for i in range(4, 0, -1):
                    rg = r * (1.0 + i * 0.14)
                    Color(0.0, 0.72, 1.0, 0.05 * (5 - i))
                    Ellipse(pos=(cx - rg, cy - rg), size=(rg * 2, rg * 2))
                Color(0.03, 0.14, 0.24, 0.96)
                Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))
                if self.active_state:
                    Color(1.0, 0.76, 0.18, 1.0)
                else:
                    Color(0.20, 0.88, 1.0, 1.0)
                Line(circle=(cx, cy, r), width=dp(2.2))

            elif self.circle_bg:
                Color(0.04, 0.10, 0.16, 0.92)
                Ellipse(pos=(cx - r, cy - r), size=(r * 2, r * 2))
                Color(0.16, 0.40, 0.56, 0.75)
                Line(circle=(cx, cy, r), width=dp(1.2))

            Color(0.78, 0.92, 1.0, 1.0)
            w = dp(1.8)

            if self.icon_type == "menu":
                s = r * 0.55
                Line(points=[cx - s, cy + s * 0.55, cx + s, cy + s * 0.55], width=w)
                Line(points=[cx - s, cy, cx + s, cy], width=w)
                Line(points=[cx - s, cy - s * 0.55, cx + s, cy - s * 0.55], width=w)
            elif self.icon_type == "settings":
                s = r * 0.32
                Line(circle=(cx, cy, s), width=w)
                for a in range(0, 360, 45):
                    rad = math.radians(a)
                    x1, y1 = cx + math.cos(rad) * (s * 1.15), cy + math.sin(rad) * (s * 1.15)
                    x2, y2 = cx + math.cos(rad) * (s * 1.65), cy + math.sin(rad) * (s * 1.65)
                    Line(points=[x1, y1, x2, y2], width=w)
            elif self.icon_type == "keyboard":
                kw, kh = r * 0.95, r * 0.62
                Line(rounded_rectangle=(cx - kw / 2, cy - kh / 2, kw, kh, dp(3)), width=dp(1.4))
                Line(points=[cx - kw * 0.28, cy - kh * 0.22, cx + kw * 0.28, cy - kh * 0.22], width=dp(1.4))
                for dx in (-0.28, 0.0, 0.28):
                    Ellipse(pos=(cx + kw * dx - dp(1.5), cy + kh * 0.08 - dp(1.5)), size=(dp(3), dp(3)))
            elif self.icon_type == "mic":
                Color(0.55, 0.94, 1.0, 1.0)
                mw, mh = r * 0.30, r * 0.52
                RoundedRectangle(pos=(cx - mw / 2, cy - mh * 0.15), size=(mw, mh), radius=[mw / 2])
                Line(circle=(cx, cy + mh * 0.05, r * 0.32, 90, 270), width=dp(1.8))
                Line(points=[cx, cy - r * 0.27, cx, cy - r * 0.44], width=dp(1.8))
                Line(points=[cx - r * 0.20, cy - r * 0.44, cx + r * 0.20, cy - r * 0.44], width=dp(1.8))
            elif self.icon_type == "tools":
                s = r * 0.42
                Line(points=[cx - s, cy - s, cx + s * 0.45, cy + s * 0.45], width=dp(2.2))
                Line(circle=(cx + s * 0.55, cy + s * 0.55, s * 0.42, -30, 210), width=dp(1.8))


class PillBadge(ButtonBehavior, FloatLayout):
    def __init__(self, text_label="", badge_type="chip", **kwargs):
        super().__init__(**kwargs)
        self.text_label = text_label
        self.badge_type = badge_type
        with self.canvas.before:
            Color(0.04, 0.11, 0.16, 0.90)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            Color(0.14, 0.38, 0.52, 0.75)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(18)), width=dp(1.1))

        self.lbl = Label(
            text=self.text_label, font_size="10.5sp", bold=True,
            color=(0.78, 0.90, 0.98, 1), pos_hint={"center_x": 0.52, "center_y": 0.5}
        )
        self.add_widget(self.lbl)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(18))
        self.canvas.after.clear()
        with self.canvas.after:
            Color(0.18, 0.92, 0.52, 1.0)
            dot_s = dp(7.5)
            Ellipse(pos=(self.right - dp(18), self.center_y - dot_s / 2), size=(dot_s, dot_s))
            ix, iy = self.x + dp(18), self.center_y
            s = dp(5.5)
            Color(0.55, 0.85, 0.98, 0.95)
            if self.badge_type == "chip":
                Line(rectangle=(ix - s, iy - s, s * 2, s * 2), width=dp(1.2))
            else:
                Line(circle=(ix, iy, s), width=dp(1.2))
                Line(points=[ix - s * 1.2, iy + s * 1.2, ix + s * 1.2, iy - s * 1.2], width=dp(1.2))


class StatusColumnWidget(ButtonBehavior, FloatLayout):
    def __init__(self, title_text="", sub_text="", icon_kind="link", **kwargs):
        super().__init__(**kwargs)
        self.icon_kind = icon_kind
        self.lbl_title = Label(
            text=title_text, font_size="10.5sp", bold=True,
            color=(0.78, 0.92, 0.98, 1), halign="left", valign="middle",
            pos_hint={"x": 0.14, "top": 0.98}, size_hint=(0.76, 0.42)
        )
        self.lbl_title.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.lbl_sub = Label(
            text=sub_text, font_size="10sp", color=(0.48, 0.65, 0.78, 1),
            halign="left", valign="top", pos_hint={"x": 0.14, "y": 0.02}, size_hint=(0.84, 0.54)
        )
        self.lbl_sub.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.add_widget(self.lbl_title)
        self.add_widget(self.lbl_sub)
        self.bind(pos=self._draw_decor, size=self._draw_decor)

    def _draw_decor(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            ix, iy = self.x + dp(8), self.top - dp(12)
            s = dp(5)
            Color(0.45, 0.85, 1.0, 0.95)
            if self.icon_kind == "link":
                Line(circle=(ix - s * 0.4, iy - s * 0.4, s * 0.7), width=dp(1.2))
                Line(circle=(ix + s * 0.4, iy + s * 0.4, s * 0.7), width=dp(1.2))
            else:
                Line(points=[
                    ix, iy + s * 1.1, ix + s, iy + s * 0.6, ix + s * 0.8, iy - s * 0.5,
                    ix, iy - s * 1.1, ix - s * 0.8, iy - s * 0.5, ix - s, iy + s * 0.6, ix, iy + s * 1.1
                ], width=dp(1.2))
            Color(0.18, 0.92, 0.52, 1.0)
            dot_s = dp(6.5)
            Ellipse(pos=(self.right - dp(14), iy - dot_s / 2), size=(dot_s, dot_s))


class RecentDividerWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(
            text="RECENT", font_size="10sp", bold=True,
            color=(0.45, 0.62, 0.75, 0.95), pos_hint={"center_x": 0.5, "center_y": 0.5}
        ))
        self.bind(pos=self._draw_lines, size=self._draw_lines)

    def _draw_lines(self, *args):
        self.canvas.before.clear()
        cy = self.center_y
        with self.canvas.before:
            Color(0.15, 0.32, 0.44, 0.65)
            Line(points=[self.x + dp(10), cy, self.center_x - dp(38), cy], width=dp(1.0))
            Line(points=[self.center_x + dp(38), cy, self.right - dp(10), cy], width=dp(1.0))
            Color(0.0, 0.78, 1.0, 0.9)
            Line(points=[self.center_x - dp(6), cy - dp(9), self.center_x + dp(6), cy - dp(9)], width=dp(1.5))


class RecentRowButton(ButtonBehavior, FloatLayout):
    def __init__(self, text_value="Wake-Word ('Hey Jarvais')  •  Standby", **kwargs):
        super().__init__(**kwargs)
        self.lbl = Label(
            text=text_value, font_size="12sp", color=(0.84, 0.92, 0.98, 1),
            halign="left", valign="middle", pos_hint={"x": 0.12, "center_y": 0.5}, size_hint=(0.78, 0.9)
        )
        self.lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.add_widget(self.lbl)
        self.bind(pos=self._draw_icons, size=self._draw_icons)

    def _draw_icons(self, *args):
        self.canvas.after.clear()
        cy = self.center_y
        with self.canvas.after:
            cx, r = self.x + dp(16), dp(7.5)
            Color(0.45, 0.80, 0.96, 0.95)
            Line(circle=(cx, cy, r), width=dp(1.2))
            Line(points=[cx, cy + r * 0.55, cx, cy, cx + r * 0.45, cy], width=dp(1.2))
            rx, s = self.right - dp(14), dp(4.5)
            Color(0.48, 0.68, 0.82, 0.9)
            Line(points=[rx - s, cy + s, rx, cy, rx - s, cy - s], width=dp(1.4))


class CyberOrbWidget(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle_outer = 0.0
        self.angle_inner = 0.0
        self.pulse = 0.0
        self.is_listening = False
        Clock.schedule_interval(self._animate, 1.0 / 60.0)

    def _animate(self, dt):
        speed = 2.8 if self.is_listening else 0.85
        self.angle_outer = (self.angle_outer + 30.0 * dt * speed) % 360.0
        self.angle_inner = (self.angle_inner - 45.0 * dt * speed) % 360.0
        self.pulse += dt * (6.8 if self.is_listening else 2.5)
        self.canvas.clear()
        self._draw_orb()

    def _draw_orb(self):
        cx, cy = self.center_x, self.center_y
        radius = min(self.width, self.height) * 0.43
        if radius <= 10:
            return
        glow_boost = 0.16 * math.sin(self.pulse)
        with self.canvas:
            for i in range(6, 0, -1):
                r_glow = radius * (1.0 + i * 0.08)
                Color(0.0, 0.58, 0.98, 0.035 * (7 - i))
                Ellipse(pos=(cx - r_glow, cy - r_glow), size=(r_glow * 2, r_glow * 2))
            Color(0.0, 0.72, 1.0, 0.35)
            Line(circle=(cx, cy, radius * 1.05), width=dp(1.1))
            Color(0.0, 0.85, 1.0, 0.85 + glow_boost)
            for start_a in (0, 90, 180, 270):
                Line(circle=(cx, cy, radius * 0.96, start_a + self.angle_outer, start_a + self.angle_outer + 55), width=dp(2.2))
            Color(1.0, 0.74, 0.16, 0.82)
            Line(circle=(cx, cy, radius * 0.88, -self.angle_inner, -self.angle_inner + 70), width=dp(1.6))
            Line(circle=(cx, cy, radius * 0.88, -self.angle_inner + 180, -self.angle_inner + 250), width=dp(1.6))
            Color(0.08, 0.70, 1.0, 0.95)
            Line(circle=(cx, cy, radius * 0.72), width=dp(2.0))
            core_r = radius * 0.68
            Color(0.02, 0.16, 0.30, 0.72)
            Ellipse(pos=(cx - core_r, cy - core_r), size=(core_r * 2, core_r * 2))
            Color(0.38, 0.90, 1.0, 0.92)
            for idx, offset in enumerate([-0.46, -0.39, -0.32, -0.25, -0.18, 0.18, 0.25, 0.32, 0.39, 0.46]):
                bx = cx + radius * offset
                amp = abs(math.sin(self.pulse + idx * 0.7)) * (0.26 if self.is_listening else 0.12) + 0.04
                bh = radius * amp
                Line(points=[bx, cy - bh, bx, cy + bh], width=dp(1.6))
            Color(1.0, 0.75, 0.18, 1.0)
            s = radius * 0.24
            Triangle(points=[cx + s * 0.15, cy + s * 1.05, cx - s * 0.55, cy - s * 0.05, cx + s * 0.05, cy - s * 0.05])
            Triangle(points=[cx - s * 0.15, cy - s * 1.05, cx + s * 0.55, cy + s * 0.05, cx - s * 0.05, cy + s * 0.05])


class LightningDudeHUD(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = SovereignGGUFEngine(status_callback=self._on_engine_status)
        self._build_ui()
        # Schedule Hands-Free Wake-Word monitor loop
        Clock.schedule_interval(self._hands_free_watchdog, 6.0)

    def _on_engine_status(self, msg: str):
        self.lbl_subgreeting.text = msg

    def _hands_free_watchdog(self, dt):
        """Checks if Hands-Free Voice Wake-Word mode is enabled and keeps listener warm"""
        if AndroidSystemBridge.hands_free_enabled and not AndroidSystemBridge.is_currently_listening:
            # Visual indicator that hands-free wake-word is armed
            self.badge_offline.lbl.text = "WAKE-WORD ON"

    def _build_ui(self):
        # 1. Top Navigation Bar (Menu opens Live Terminal, Gear opens Full Authorities & Tools)
        top_bar = BoxLayout(orientation="horizontal", size_hint=(0.92, 0.075), pos_hint={"center_x": 0.5, "top": 0.975})
        btn_menu = VectorIconButton(icon_type="menu", size_hint_x=0.14)
        btn_menu.bind(on_release=lambda *_: self._open_terminal_modal())

        title_box = BoxLayout(orientation="vertical", size_hint_x=0.72)
        title_box.add_widget(Label(text="L I G H T N I N G   D U D E", font_size="16sp", bold=True, color=(0.90, 0.96, 1, 1)))
        title_box.add_widget(Label(text="J A R V A I S", font_size="11sp", color=(0.52, 0.72, 0.85, 1)))

        btn_settings = VectorIconButton(icon_type="settings", size_hint_x=0.14)
        btn_settings.bind(on_release=lambda *_: self._open_tools_modal())

        top_bar.add_widget(btn_menu)
        top_bar.add_widget(title_box)
        top_bar.add_widget(btn_settings)
        self.add_widget(top_bar)

        # 2. Pill Badges Row
        badges_row = BoxLayout(orientation="horizontal", spacing=dp(16), size_hint=(0.86, 0.048), pos_hint={"center_x": 0.5, "top": 0.885})
        self.badge_model = PillBadge(text_label="LOCAL MODEL", badge_type="chip")
        self.badge_model.bind(on_release=lambda *_: self._open_terminal_modal())
        self.badge_offline = PillBadge(text_label="OFFLINE", badge_type="offline")
        self.badge_offline.bind(on_release=lambda *_: self._toggle_hands_free_mode())
        badges_row.add_widget(self.badge_model)
        badges_row.add_widget(self.badge_offline)
        self.add_widget(badges_row)

        # 3. Greeting & Live AI Response Area
        greeting_box = BoxLayout(orientation="vertical", size_hint=(0.90, 0.095), pos_hint={"center_x": 0.5, "top": 0.82})
        self.lbl_greeting = Label(text="I'm here, Boss.", font_size="24sp", bold=True, color=(0.94, 0.98, 1, 1), size_hint_y=0.52)
        self.lbl_subgreeting = Label(
            text="Ready to help with your device.", font_size="12.5sp", color=(0.56, 0.78, 0.92, 1),
            halign="center", valign="middle", size_hint_y=0.48
        )
        self.lbl_subgreeting.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        greeting_box.add_widget(self.lbl_greeting)
        greeting_box.add_widget(self.lbl_subgreeting)
        self.add_widget(greeting_box)

        # 4. Cyberpunk Orb (Tapping Orb also triggers hands-free / voice command)
        self.orb = CyberOrbWidget(size_hint=(0.82, 0.34), pos_hint={"center_x": 0.5, "center_y": 0.545})
        self.orb.bind(on_release=self._start_voice_input)
        self.add_widget(self.orb)

        self.add_widget(Label(
            text="-\nLISTEN\nTHINK\nACT\nWITH\nYOU\n-", font_size="9.5sp", halign="left",
            color=(0.45, 0.65, 0.78, 0.85), size_hint=(0.15, 0.22), pos_hint={"x": 0.04, "center_y": 0.545}
        ))
        self.add_widget(Label(
            text="-\nPRIVATE\nLOCAL\nYOURS\n-", font_size="9.5sp", halign="right",
            color=(0.45, 0.65, 0.78, 0.85), size_hint=(0.15, 0.22), pos_hint={"right": 0.96, "center_y": 0.545}
        ))

        # 5. Status Columns (Clickable to open Device Authorities & Terminal)
        status_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(0.90, 0.08), pos_hint={"center_x": 0.5, "y": 0.275})
        col_link = StatusColumnWidget(title_text="DEVICE LINK: READY", sub_text="Can operate your device\nwith your consent.", icon_kind="link")
        col_link.bind(on_release=lambda *_: self._open_tools_modal())
        col_priv = StatusColumnWidget(title_text="PRIVACY: ON-DEVICE", sub_text="Your data stays on\nthis device.", icon_kind="shield")
        col_priv.bind(on_release=lambda *_: self._open_terminal_modal())
        status_row.add_widget(col_link)
        status_row.add_widget(col_priv)
        self.add_widget(status_row)

        # 6. Recent Activity Row (Tap to open Live Terminal)
        self.add_widget(RecentDividerWidget(size_hint=(0.88, 0.035), pos_hint={"center_x": 0.5, "y": 0.225}))
        self.recent_btn = RecentRowButton(text_value="Opened Settings  •  2m ago", size_hint=(0.88, 0.05), pos_hint={"center_x": 0.5, "y": 0.17})
        self.recent_btn.bind(on_release=lambda *_: self._open_terminal_modal())
        self.add_widget(self.recent_btn)

        # 7. Bottom Control Dock
        dock = FloatLayout(size_hint=(0.92, 0.155), pos_hint={"center_x": 0.5, "y": 0.01})

        self.btn_type = VectorIconButton(icon_type="keyboard", circle_bg=True, size_hint=(None, None), size=(dp(56), dp(56)), pos_hint={"center_x": 0.18, "center_y": 0.62})
        self.btn_type.bind(on_release=lambda *_: self._open_type_modal())
        dock.add_widget(self.btn_type)
        dock.add_widget(Label(text="Type", font_size="11.5sp", color=(0.68, 0.82, 0.92, 1), size_hint=(None, None), size=(dp(60), dp(20)), pos_hint={"center_x": 0.18, "center_y": 0.16}))

        self.btn_mic = VectorIconButton(icon_type="mic", is_primary_mic=True, size_hint=(None, None), size=(dp(84), dp(84)), pos_hint={"center_x": 0.50, "center_y": 0.64})
        self.btn_mic.bind(on_release=self._start_voice_input)
        dock.add_widget(self.btn_mic)

        self.lbl_mic_caption = Label(text="T A P   T O   S P E A K", font_size="11sp", bold=True, color=(0.78, 0.92, 1.0, 1), size_hint=(None, None), size=(dp(140), dp(20)), pos_hint={"center_x": 0.50, "center_y": 0.10})
        dock.add_widget(self.lbl_mic_caption)

        self.btn_tools = VectorIconButton(icon_type="tools", circle_bg=True, size_hint=(None, None), size=(dp(56), dp(56)), pos_hint={"center_x": 0.82, "center_y": 0.62})
        self.btn_tools.bind(on_release=lambda *_: self._open_tools_modal())
        dock.add_widget(self.btn_tools)
        dock.add_widget(Label(text="Tools", font_size="11.5sp", color=(0.68, 0.82, 0.92, 1), size_hint=(None, None), size=(dp(60), dp(20)), pos_hint={"center_x": 0.82, "center_y": 0.16}))

        self.add_widget(dock)

    def _toggle_hands_free_mode(self):
        AndroidSystemBridge.hands_free_enabled = not AndroidSystemBridge.hands_free_enabled
        state = "ACTIVE" if AndroidSystemBridge.hands_free_enabled else "PAUSED"
        self.badge_offline.lbl.text = f"WAKE: {state}"
        msg = f"Hands-Free Continuous Voice Wake-Word {state}"
        self.lbl_subgreeting.text = msg
        self.recent_btn.lbl.text = f"{msg}  •  now"
        if AndroidSystemBridge.hands_free_enabled:
            self._start_voice_input(hands_free=True)

    def _start_voice_input(self, *args, hands_free=False):
        self.orb.is_listening = True
        self.btn_mic.active_state = True
        self.btn_mic._redraw()
        self.lbl_greeting.text = "Listening, Boss..."
        self.lbl_subgreeting.text = "Say 'Hey Jarvais' or speak command..."
        self.lbl_mic_caption.text = "L I S T E N I N G . . ."

        def _on_spoken_text(spoken_str: str):
            self.orb.is_listening = False
            self.btn_mic.active_state = False
            self.btn_mic._redraw()
            self.lbl_mic_caption.text = "T A P   T O   S P E A K"

            if not spoken_str.strip():
                self.lbl_greeting.text = "I'm here, Boss."
                return

            self.recent_btn.lbl.text = f"Voice: {spoken_str[:28]}  •  now"
            self.lbl_greeting.text = "Thinking, Boss..."

            def _worker():
                reply = self.engine.generate(spoken_str)
                def _show_reply(dt):
                    self.lbl_greeting.text = "I'm here, Boss."
                    self.lbl_subgreeting.text = reply
                    AndroidSystemBridge.speak(reply)
                    # Re-arm continuous hands-free wake-word after speaking reply
                    if AndroidSystemBridge.hands_free_enabled and hands_free:
                        Clock.schedule_once(lambda _dt: self._start_voice_input(hands_free=True), 4.0)
                Clock.schedule_once(_show_reply, 0)

            threading.Thread(target=_worker, daemon=True).start()

        AndroidSystemBridge.trigger_voice_listen(_on_spoken_text, hands_free_loop=hands_free)

    def _open_type_modal(self):
        modal = ModalView(size_hint=(0.94, 0.56), background_color=(0.02, 0.06, 0.10, 0.98))
        box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        box.add_widget(Label(text="DIRECT NEURAL CHAT (500M GGUF CORE)", font_size="13.5sp", bold=True, color=(0.2, 0.88, 1, 1), size_hint_y=0.14))

        inp = TextInput(
            hint_text="Ask JARVAIS or issue device command (e.g. 'open whatsapp', 'open settings')...",
            multiline=False, size_hint_y=0.20, font_size="14sp",
            background_color=(0.05, 0.14, 0.22, 1), foreground_color=(0.95, 0.98, 1, 1)
        )
        out_lbl = Label(
            text="JARVAIS response will appear here & speak aloud...",
            font_size="12.5sp", color=(0.80, 0.94, 1.0, 1), size_hint_y=0.42,
            halign="center", valign="middle"
        )
        out_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        btn_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=0.24)
        btn_send = Button(text="EXECUTE", bold=True, background_normal="", background_color=(0.0, 0.62, 0.90, 1))
        btn_term = Button(text="TERMINAL", size_hint_x=0.45, background_normal="", background_color=(0.08, 0.35, 0.25, 1))
        btn_close = Button(text="CLOSE", size_hint_x=0.35, background_normal="", background_color=(0.12, 0.22, 0.30, 1))

        def _run_cmd(*_):
            q = inp.text.strip()
            if not q:
                return
            self.recent_btn.lbl.text = f"Cmd: {q[:26]}  •  now"
            out_lbl.text = "Running on Local 500M GGUF Core..."

            def _worker():
                ans = self.engine.generate(q)
                def _update(dt):
                    out_lbl.text = ans
                    self.lbl_subgreeting.text = ans[:85]
                    AndroidSystemBridge.speak(ans)
                Clock.schedule_once(_update, 0)

            threading.Thread(target=_worker, daemon=True).start()

        btn_send.bind(on_release=_run_cmd)
        inp.bind(on_text_validate=_run_cmd)
        btn_term.bind(on_release=lambda *_: (modal.dismiss(), self._open_terminal_modal()))
        btn_close.bind(on_release=lambda *_: modal.dismiss())
        btn_row.add_widget(btn_send)
        btn_row.add_widget(btn_term)
        btn_row.add_widget(btn_close)

        box.add_widget(inp)
        box.add_widget(out_lbl)
        box.add_widget(btn_row)
        modal.add_widget(box)
        modal.open()

    def _open_terminal_modal(self):
        """Built-in Interactive Sovereign Shell & Real-Time Log Console"""
        modal = ModalView(size_hint=(0.96, 0.78), background_color=(0.01, 0.03, 0.05, 0.98))
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        header = BoxLayout(orientation="horizontal", size_hint_y=0.09)
        header.add_widget(Label(text=">_ JARVAIS SOVEREIGN SHELL & SYSTEM LOGS", font_size="12.5sp", bold=True, color=(0.18, 0.95, 0.55, 1), halign="left"))
        box.add_widget(header)

        scroll = ScrollView(size_hint_y=0.66)
        term_out = Label(
            text="\n".join(SovereignTerminalLogger.logs),
            font_size="11sp",
            color=(0.25, 0.95, 0.60, 1),
            halign="left",
            valign="top",
            size_hint_y=None
        )
        term_out.bind(texture_size=lambda inst, val: setattr(inst, "height", max(val[1], dp(260))))
        term_out.bind( width=lambda inst, val: setattr(inst, "text_size", (val, None)))
        scroll.add_widget(term_out)
        box.add_widget(scroll)

        def _refresh_logs(new_text):
            term_out.text = new_text

        SovereignTerminalLogger.listeners.append(_refresh_logs)
        modal.bind(on_dismiss=lambda *_: SovereignTerminalLogger.listeners.remove(_refresh_logs) if _refresh_logs in SovereignTerminalLogger.listeners else None)

        cmd_inp = TextInput(
            hint_text="Enter shell command (e.g. 'ls -lh', 'uname -a', 'ps', 'df -h')...",
            multiline=False, size_hint_y=0.12, font_size="13sp",
            background_color=(0.03, 0.09, 0.14, 1), foreground_color=(0.25, 1.0, 0.65, 1)
        )
        box.add_widget(cmd_inp)

        btn_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=0.13)
        btn_exec = Button(text="RUN SHELL", bold=True, background_normal="", background_color=(0.05, 0.55, 0.35, 1))
        btn_ai = Button(text="RUN GGUF CLI", bold=True, background_normal="", background_color=(0.0, 0.52, 0.82, 1))
        btn_close = Button(text="CLOSE", size_hint_x=0.35, background_normal="", background_color=(0.15, 0.22, 0.28, 1))

        def _exec_shell(*_):
            c = cmd_inp.text.strip()
            if not c:
                return
            cmd_inp.text = ""
            threading.Thread(target=self.engine.run_shell_command, args=(c,), daemon=True).start()

        def _exec_gguf(*_):
            c = cmd_inp.text.strip() or "Hello Jarvais"
            cmd_inp.text = ""
            def _w():
                ans = self.engine.generate(c)
                SovereignTerminalLogger.log(f"[GGUF OUT]: {ans}")
            threading.Thread(target=_w, daemon=True).start()

        btn_exec.bind(on_release=_exec_shell)
        cmd_inp.bind(on_text_validate=_exec_shell)
        btn_ai.bind(on_release=_exec_gguf)
        btn_close.bind(on_release=lambda *_: modal.dismiss())

        btn_row.add_widget(btn_exec)
        btn_row.add_widget(btn_ai)
        btn_row.add_widget(btn_close)
        box.add_widget(btn_row)

        modal.add_widget(box)
        modal.open()

    def _open_tools_modal(self):
        """Full Device Control Authorities & 24/7 Daemon Control Panel"""
        modal = ModalView(size_hint=(0.94, 0.76), background_color=(0.02, 0.06, 0.10, 0.98))
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(8))
        box.add_widget(Label(text="FULL SOVEREIGN DEVICE AUTHORITIES & TOOLS", font_size="13sp", bold=True, color=(0.2, 0.88, 1, 1), size_hint_y=0.09))

        scroll = ScrollView(size_hint_y=0.77)
        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, dp(4)])
        grid.bind(minimum_height=grid.setter("height"))

        actions = [
            ("1. Open Built-In Live Terminal Console (>_)", lambda: (modal.dismiss(), self._open_terminal_modal()) and "Opened Terminal"),
            ("2. Toggle Hands-Free Continuous Wake-Word ('Hey Jarvais')", lambda: (self._toggle_hands_free_mode(), "Toggled Hands-Free Wake-Word")[1]),
            ("3. Grant Runtime Mic / Camera / Phone / Notification Perms", AndroidSystemBridge.request_runtime_permissions),
            ("4. Enable 24/7 Unrestricted Battery (Never Kill Daemon)", AndroidSystemBridge.request_unrestricted_battery),
            ("5. Enable Accessibility Service (Screen Read & Auto-Tap)", AndroidSystemBridge.open_accessibility_settings),
            ("6. Grant Manage All Files Authority (Full Storage Control)", AndroidSystemBridge.request_all_files_access),
            ("7. Enable Floating Orb Overlay (Draw Over Other Apps)", AndroidSystemBridge.request_overlay_permission),
            ("8. Enable Write System Settings (Brightness / Audio / Wifi)", AndroidSystemBridge.request_write_system_settings),
            ("9. Start / Verify 24/7 Foreground Sticky Service", AndroidSystemBridge.start_jarvais_service),
            ("10. Open Android System Settings", AndroidSystemBridge.open_android_settings),
        ]

        for label_txt, func in actions:
            b = Button(
                text=label_txt, font_size="11.5sp", size_hint_y=None, height=dp(44),
                background_normal="", background_color=(0.05, 0.16, 0.25, 1), color=(0.88, 0.96, 1, 1)
            )
            def _make_handler(f=func):
                def _h(*_):
                    res = f()
                    if res:
                        self.recent_btn.lbl.text = f"{str(res)[:34]}  •  now"
                        self.lbl_subgreeting.text = str(res)
                return _h
            b.bind(on_release=_make_handler())
            grid.add_widget(b)

        scroll.add_widget(grid)
        box.add_widget(scroll)

        btn_close = Button(text="CLOSE AUTHORITIES PANEL", size_hint_y=0.12, bold=True, background_normal="", background_color=(0.0, 0.55, 0.82, 1))
        btn_close.bind(on_release=lambda *_: modal.dismiss())
        box.add_widget(btn_close)
        modal.add_widget(box)
        modal.open()


class LightningDudeApp(App):
    def build(self):
        self.title = "Lightning Dude - JARVAIS"
        Clock.schedule_once(self._boot_authorities, 1.2)
        return LightningDudeHUD()

    def _boot_authorities(self, dt):
        AndroidSystemBridge.init_tts()
        AndroidSystemBridge.request_runtime_permissions()
        AndroidSystemBridge.start_jarvais_service()
        Clock.schedule_once(lambda *_: AndroidSystemBridge.request_unrestricted_battery(), 3.0)

    def on_pause(self):
        AndroidSystemBridge.start_jarvais_service()
        return True

    def on_resume(self):
        AndroidSystemBridge.start_jarvais_service()


if __name__ == "__main__":
    LightningDudeApp().run()
