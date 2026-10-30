import os
import math
import time
import subprocess
import threading
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle, Triangle
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

Window.clearcolor = (0.02, 0.05, 0.08, 1)


class SovereignTerminalLogger:
    logs = [
        "[BOOT] LIGHTNING DUDE // EXTERNAL GGUF SELECTOR MODE",
        "[CORE] Please select your .gguf model file from phone storage.",
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
        except Exception:
            pass

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
        except Exception:
            pass

    @classmethod
    def trigger_voice_listen(cls, callback, hands_free_loop=False):
        cls._voice_callback = callback
        if platform != "android":
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
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak command...")
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
                        if cls._voice_callback:
                            Clock.schedule_once(lambda dt: cls._voice_callback(spoken_text), 0)
                        return
                except Exception:
                    pass
            if cls.hands_free_enabled and cls._voice_callback:
                Clock.schedule_once(lambda dt: cls._voice_callback(""), 0)

    @staticmethod
    def request_runtime_permissions():
        if platform != "android":
            return "Permissions active (Desktop)"
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.RECORD_AUDIO,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                "android.permission.MANAGE_EXTERNAL_STORAGE",
                "android.permission.POST_NOTIFICATIONS",
                "android.permission.FOREGROUND_SERVICE",
                "android.permission.WAKE_LOCK",
            ])
            return "Requested Storage & Mic Authorities"
        except Exception as e:
            return f"Perm notice: {e}"

    @staticmethod
    def request_unrestricted_battery():
        if platform != "android":
            return "Battery Exemption Active (Desktop)"
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
                activity.startActivity(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse(f"package:{pkg}")))
                return "Opened Battery Exemption Settings"
            return "Battery Exemption Already Active"
        except Exception as e:
            return f"Battery notice: {e}"

    @staticmethod
    def start_jarvais_service():
        if platform != "android":
            return "Service Active (Desktop)"
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            ServiceJarvais = autoclass("org.jarvais.lightningdude.ServiceJarvais")
            ServiceJarvais.start(PythonActivity.mActivity, "Wake-word standby • External GGUF Mode")
            return "24/7 Sticky Background Daemon Running"
        except Exception as e:
            return f"Service notice: {e}"

    @staticmethod
    def extract_cli_binary() -> str:
        base_dir = Path(".")
        if platform == "android":
            try:
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                base_dir = Path(PythonActivity.mActivity.getFilesDir().getAbsolutePath())
            except Exception:
                pass
        cli_target = base_dir / "llama-cli"
        if cli_target.exists() and cli_target.stat().st_size > 1024:
            os.chmod(str(cli_target), 0o755)
            return str(cli_target)

        try:
            if platform == "android":
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                asset_mgr = PythonActivity.mActivity.getAssets()
                inp = asset_mgr.open("llama-cli")
                cli_target.parent.mkdir(parents=True, exist_ok=True)
                FileOutputStream = autoclass("java.io.FileOutputStream")
                out = FileOutputStream(str(cli_target))
                buf = bytearray(1024 * 512)
                while True:
                    r = inp.read(buf)
                    if r <= 0:
                        break
                    out.write(buf, 0, r)
                out.flush()
                out.close()
                inp.close()
            else:
                for cand in [Path("assets/llama-cli"), Path("llama-cli")]:
                    if cand.exists():
                        cli_target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(cand, cli_target)
                        break
            if cli_target.exists():
                os.chmod(str(cli_target), 0o755)
                return str(cli_target)
        except Exception as e:
            SovereignTerminalLogger.log(f"[CLI Extract Err]: {e}")
        return ""


class SovereignGGUFEngine:
    """Manages externally selected .gguf model files"""
    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        self.model_path = self._find_default_external_model()
        self.cli_path = AndroidSystemBridge.extract_cli_binary()
        self.is_ready = True

    def _find_default_external_model(self) -> str:
        search_dirs = [
            Path("/storage/emulated/0/Download"),
            Path("/storage/emulated/0/Documents"),
            Path("/storage/emulated/0"),
        ]
        if platform == "android":
            try:
                from android.storage import primary_external_storage_path
                search_dirs.insert(0, Path(primary_external_storage_path()) / "Download")
                search_dirs.insert(1, Path(primary_external_storage_path()))
            except Exception:
                pass

        for d in search_dirs:
            if d.exists():
                for f in d.glob("*.gguf"):
                    if f.stat().st_size > 10000000:
                        SovereignTerminalLogger.log(f"[MODEL] Found external GGUF: {f}")
                        return str(f)
        return ""

    def set_model_path(self, path: str):
        self.model_path = path
        if path and Path(path).exists():
            mb = Path(path).stat().st_size // (1024 * 1024)
            msg = f"Model Loaded ({mb}MB • {Path(path).name})"
            SovereignTerminalLogger.log(f"[MODEL] {msg}")
            if self.status_callback:
                self.status_callback(msg)

    def generate(self, prompt: str) -> str:
        q = prompt.strip()
        if not q:
            return "Listening in standby, Boss."

        low = q.lower()
        if "setting" in low:
            return "Boss, Android System Settings khol di hain."

        if not self.model_path or not Path(self.model_path).exists():
            return "Boss, koi valid .gguf model select nahi kiya gaya! Tools menu ya Model Badge par click kar ke apni .gguf file select karein."

        if self.cli_path and os.path.exists(self.cli_path):
            try:
                formatted_prompt = (
                    "<|im_start|>system\nYou are JARVAIS (Lightning Dude), Boss's sovereign bilingual AI assistant.<|im_end|>\n"
                    f"<|im_start|>user\n{q}<|im_end|>\n<|im_start|>assistant\n"
                )
                cmd = [self.cli_path, "-m", self.model_path, "-p", formatted_prompt, "-n", "90", "-t", "4", "--temp", "0.6", "--no-display-prompt", "-e"]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                raw_out = (proc.stdout or "").strip()
                if raw_out:
                    return raw_out.split("<|im_end|>")[0].split("<|im_start|>")[0].strip()
            except Exception as e:
                SovereignTerminalLogger.log(f"[GGUF Run Err]: {e}")

        return f"Ji Boss! '{q}' receive ho gaya. Model path: {Path(self.model_path).name}"


class VectorIconButton(ButtonBehavior, Widget):
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
                Color(1.0, 0.76, 0.18, 1.0) if self.active_state else Color(0.20, 0.88, 1.0, 1.0)
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
            elif self.icon_type == "keyboard":
                kw, kh = r * 0.95, r * 0.62
                Line(rounded_rectangle=(cx - kw / 2, cy - kh / 2, kw, kh, dp(3)), width=dp(1.4))
            elif self.icon_type == "mic":
                Color(0.55, 0.94, 1.0, 1.0)
                mw, mh = r * 0.30, r * 0.52
                RoundedRectangle(pos=(cx - mw / 2, cy - mh * 0.15), size=(mw, mh), radius=[mw / 2])
            elif self.icon_type == "tools":
                s = r * 0.42
                Line(points=[cx - s, cy - s, cx + s * 0.45, cy + s * 0.45], width=dp(2.2))


class PillBadge(ButtonBehavior, FloatLayout):
    def __init__(self, text_label="", badge_type="chip", **kwargs):
        super().__init__(**kwargs)
        self.text_label = text_label
        with self.canvas.before:
            Color(0.04, 0.11, 0.16, 0.90)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
            Color(0.14, 0.38, 0.52, 0.75)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(18)), width=dp(1.1))
        self.lbl = Label(text=self.text_label, font_size="10sp", bold=True, color=(0.78, 0.90, 0.98, 1), pos_hint={"center_x": 0.52, "center_y": 0.5})
        self.add_widget(self.lbl)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(18))


class StatusColumnWidget(ButtonBehavior, FloatLayout):
    def __init__(self, title_text="", sub_text="", **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text=title_text, font_size="10.5sp", bold=True, color=(0.78, 0.92, 0.98, 1), halign="left", valign="middle", pos_hint={"x": 0.14, "top": 0.98}, size_hint=(0.76, 0.42)))
        self.add_widget(Label(text=sub_text, font_size="10sp", color=(0.48, 0.65, 0.78, 1), halign="left", valign="top", pos_hint={"x": 0.14, "y": 0.02}, size_hint=(0.84, 0.54)))


class RecentDividerWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="RECENT", font_size="10sp", bold=True, color=(0.45, 0.62, 0.75, 0.95), pos_hint={"center_x": 0.5, "center_y": 0.5}))


class RecentRowButton(ButtonBehavior, FloatLayout):
    def __init__(self, text_value="Tap to Select External GGUF Model", **kwargs):
        super().__init__(**kwargs)
        self.lbl = Label(text=text_value, font_size="12sp", color=(0.84, 0.92, 0.98, 1), halign="left", valign="middle", pos_hint={"x": 0.12, "center_y": 0.5}, size_hint=(0.78, 0.9))
        self.lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.add_widget(self.lbl)


class CyberOrbWidget(ButtonBehavior, Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle_outer = 0.0
        self.is_listening = False
        Clock.schedule_interval(self._animate, 1.0 / 60.0)

    def _animate(self, dt):
        self.angle_outer = (self.angle_outer + 30.0 * dt) % 360.0
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y
        radius = min(self.width, self.height) * 0.43
        if radius <= 10:
            return
        with self.canvas:
            Color(0.0, 0.72, 1.0, 0.35)
            Line(circle=(cx, cy, radius * 1.05), width=dp(1.1))
            Color(1.0, 0.75, 0.18, 1.0)
            s = radius * 0.24
            Triangle(points=[cx + s * 0.15, cy + s * 1.05, cx - s * 0.55, cy - s * 0.05, cx + s * 0.05, cy - s * 0.05])


class LightningDudeHUD(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.engine = SovereignGGUFEngine(status_callback=self._on_engine_status)
        self._build_ui()

    def _on_engine_status(self, msg: str):
        self.lbl_subgreeting.text = msg

    def _build_ui(self):
        top_bar = BoxLayout(orientation="horizontal", size_hint=(0.92, 0.075), pos_hint={"center_x": 0.5, "top": 0.975})
        btn_menu = VectorIconButton(icon_type="menu", size_hint_x=0.14)
        btn_menu.bind(on_release=lambda *_: self._open_model_picker())

        title_box = BoxLayout(orientation="vertical", size_hint_x=0.72)
        title_box.add_widget(Label(text="L I G H T N I N G   D U D E", font_size="16sp", bold=True, color=(0.90, 0.96, 1, 1)))
        title_box.add_widget(Label(text="EXTERNAL GGUF SELECTOR", font_size="10.5sp", color=(0.2, 0.88, 1, 1)))

        btn_settings = VectorIconButton(icon_type="settings", size_hint_x=0.14)
        btn_settings.bind(on_release=lambda *_: self._open_tools_modal())

        top_bar.add_widget(btn_menu)
        top_bar.add_widget(title_box)
        top_bar.add_widget(btn_settings)
        self.add_widget(top_bar)

        badges_row = BoxLayout(orientation="horizontal", spacing=dp(16), size_hint=(0.86, 0.048), pos_hint={"center_x": 0.5, "top": 0.885})
        self.badge_model = PillBadge(text_label="SELECT .GGUF MODEL", badge_type="chip")
        self.badge_model.bind(on_release=lambda *_: self._open_model_picker())
        badges_row.add_widget(self.badge_model)
        self.add_widget(badges_row)

        greeting_box = BoxLayout(orientation="vertical", size_hint=(0.90, 0.095), pos_hint={"center_x": 0.5, "top": 0.82})
        self.lbl_greeting = Label(text="I'm here, Boss.", font_size="24sp", bold=True, color=(0.94, 0.98, 1, 1), size_hint_y=0.52)
        self.lbl_subgreeting = Label(text="Tap badge above to select your external .gguf file.", font_size="12sp", color=(0.56, 0.78, 0.92, 1), halign="center", valign="middle", size_hint_y=0.48)
        self.lbl_subgreeting.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        greeting_box.add_widget(self.lbl_greeting)
        greeting_box.add_widget(self.lbl_subgreeting)
        self.add_widget(greeting_box)

        self.orb = CyberOrbWidget(size_hint=(0.82, 0.34), pos_hint={"center_x": 0.5, "center_y": 0.545})
        self.orb.bind(on_release=lambda *_: self._open_model_picker())
        self.add_widget(self.orb)

        status_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(0.90, 0.08), pos_hint={"center_x": 0.5, "y": 0.275})
        col_link = StatusColumnWidget(title_text="EXTERNAL MODEL", sub_text="Select model from storage\nmanually.")
        status_row.add_widget(col_link)
        self.add_widget(status_row)

        self.add_widget(RecentDividerWidget(size_hint=(0.88, 0.035), pos_hint={"center_x": 0.5, "y": 0.225}))
        self.recent_btn = RecentRowButton(text_value="Tap here to pick .gguf model file", size_hint=(0.88, 0.05), pos_hint={"center_x": 0.5, "y": 0.17})
        self.recent_btn.bind(on_release=lambda *_: self._open_model_picker())
        self.add_widget(self.recent_btn)

        dock = FloatLayout(size_hint=(0.92, 0.155), pos_hint={"center_x": 0.5, "y": 0.01})
        self.btn_type = VectorIconButton(icon_type="keyboard", circle_bg=True, size_hint=(None, None), size=(dp(56), dp(56)), pos_hint={"center_x": 0.18, "center_y": 0.62})
        self.btn_type.bind(on_release=lambda *_: self._open_type_modal())
        dock.add_widget(self.btn_type)

        self.btn_mic = VectorIconButton(icon_type="mic", is_primary_mic=True, size_hint=(None, None), size=(dp(84), dp(84)), pos_hint={"center_x": 0.50, "center_y": 0.64})
        self.btn_mic.bind(on_release=lambda *_: self._open_model_picker())
        dock.add_widget(self.btn_mic)

        self.btn_tools = VectorIconButton(icon_type="tools", circle_bg=True, size_hint=(None, None), size=(dp(56), dp(56)), pos_hint={"center_x": 0.82, "center_y": 0.62})
        self.btn_tools.bind(on_release=lambda *_: self._open_tools_modal())
        dock.add_widget(self.btn_tools)
        self.add_widget(dock)

    def _open_model_picker(self):
        modal = ModalView(size_hint=(0.94, 0.80), background_color=(0.02, 0.06, 0.10, 0.98))
        box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        box.add_widget(Label(text="SELECT EXTERNAL .GGUF MODEL FILE", font_size="13.5sp", bold=True, color=(0.2, 0.88, 1, 1), size_hint_y=0.08))

        scroll = ScrollView(size_hint_y=0.74)
        grid = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, dp(4)])
        grid.bind(minimum_height=grid.setter("height"))

        found_files = []
        search_roots = [Path("/storage/emulated/0/Download"), Path("/storage/emulated/0/Documents"), Path("/storage/emulated/0")]
        if platform == "android":
            try:
                from android.storage import primary_external_storage_path
                search_roots.insert(0, Path(primary_external_storage_path()) / "Download")
                search_roots.insert(1, Path(primary_external_storage_path()))
            except Exception:
                pass

        for root in search_roots:
            if root.exists():
                try:
                    for f in root.glob("**/*.gguf"):
                        if f.stat().st_size > 5000000:
                            found_files.append(f)
                except Exception:
                    pass

        if not found_files:
            grid.add_widget(Label(text="No .gguf files found in Download/Documents.\nPlease place your model in phone storage.", font_size="12sp", color=(0.9, 0.4, 0.4, 1), size_hint_y=None, height=dp(60)))
        else:
            for fpath in found_files:
                sz = fpath.stat().st_size // (1024 * 1024)
                btn = Button(
                    text=f"{fpath.name} ({sz} MB)\n{fpath.parent}",
                    font_size="11.5sp", size_hint_y=None, height=dp(54),
                    background_normal="", background_color=(0.05, 0.16, 0.25, 1), color=(0.88, 0.96, 1, 1)
                )
                def _select(inst, fp=str(fpath)):
                    self.engine.set_model_path(fp)
                    self.badge_model.lbl.text = Path(fp).name[:20]
                    self.recent_btn.lbl.text = f"Model: {Path(fp).name}"
                    modal.dismiss()
                btn.bind(on_release=_select)
                grid.add_widget(btn)

        scroll.add_widget(grid)
        box.add_widget(scroll)

        btn_close = Button(text="CLOSE", size_hint_y=0.12, bold=True, background_normal="", background_color=(0.15, 0.22, 0.28, 1))
        btn_close.bind(on_release=lambda *_: modal.dismiss())
        box.add_widget(btn_close)
        modal.add_widget(box)
        modal.open()

    def _open_type_modal(self):
        modal = ModalView(size_hint=(0.94, 0.50), background_color=(0.02, 0.06, 0.10, 0.98))
        box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        box.add_widget(Label(text="CHAT WITH EXTERNAL MODEL", font_size="13.5sp", bold=True, color=(0.2, 0.88, 1, 1), size_hint_y=0.15))
        inp = TextInput(hint_text="Ask model...", multiline=False, size_hint_y=0.25, font_size="14sp", background_color=(0.05, 0.14, 0.22, 1), foreground_color=(0.95, 0.98, 1, 1))
        out_lbl = Label(text="Response...", font_size="12.5sp", color=(0.80, 0.94, 1.0, 1), size_hint_y=0.40, halign="center", valign="middle")
        out_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))

        def _run(*_):
            q = inp.text.strip()
            if not q:
                return
            out_lbl.text = "Thinking..."
            threading.Thread(target=lambda: Clock.schedule_once(lambda dt: setattr(out_lbl, "text", self.engine.generate(q)), 0), daemon=True).start()

        inp.bind(on_text_validate=_run)
        box.add_widget(inp)
        box.add_widget(out_lbl)
        modal.add_widget(box)
        modal.open()

    def _open_tools_modal(self):
        self._open_model_picker()


class LightningDudeApp(App):
    def build(self):
        self.title = "Lightning Dude - External GGUF"
        AndroidSystemBridge.request_runtime_permissions()
        AndroidSystemBridge.start_jarvais_service()
        return LightningDudeHUD()


if __name__ == "__main__":
    LightningDudeApp().run()
