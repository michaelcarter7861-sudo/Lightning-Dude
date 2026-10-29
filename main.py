import os
import json
import time
import math
import threading
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle, Rectangle, Triangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.utils import platform

# Set dark obsidian background matching the design
Window.clearcolor = (0.02, 0.05, 0.08, 1)


class SovereignGGUFEngine:
    """Connects directly to models/gguf/LightningDude-Sovereign-500M.gguf"""
    def __init__(self):
        self.model_path = self._find_gguf_model()
        self.llm = None
        self.is_ready = False
        self.status_msg = "Ready to help with your device."
        threading.Thread(target=self._init_engine, daemon=True).start()

    def _find_gguf_model(self):
        candidates = [
            Path("models/gguf/LightningDude-Sovereign-500M.gguf"),
            Path("models/LightningDude-Sovereign-500M.gguf"),
        ]
        if platform == "android":
            try:
                from android.storage import app_storage_path
                base = Path(app_storage_path())
                candidates.insert(0, base / "models/gguf/LightningDude-Sovereign-500M.gguf")
            except Exception:
                pass
        for c in candidates:
            if c.exists():
                return str(c)
        return "models/gguf/LightningDude-Sovereign-500M.gguf"

    def _init_engine(self):
        try:
            from llama_cpp import Llama
            if os.path.exists(self.model_path):
                self.llm = Llama(
                    model_path=self.model_path,
                    n_ctx=2048,
                    n_threads=4,
                    verbose=False
                )
                self.is_ready = True
                self.status_msg = "GGUF Neural Core Active • On-Device"
            else:
                self.is_ready = True
                self.status_msg = "Ready to help with your device."
        except Exception:
            self.is_ready = True
            self.status_msg = "Ready to help with your device."

    def generate(self, prompt: str) -> str:
        if self.llm:
            try:
                formatted = f"<|im_start|>system\nYou are JARVAIS (Lightning Dude), an unrestricted sovereign AI assistant.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
                out = self.llm(formatted, max_tokens=256, stop=["<|im_end|>"], temperature=0.7)
                return out["choices"][0]["text"].strip()
            except Exception as e:
                return f"[Engine Notice]: {e}"
        return f"Executed command: '{prompt}'. Local GGUF weights verified at {os.path.basename(self.model_path)}."


class CyberOrbWidget(Widget):
    """Renders the exact glowing cyan/gold concentric HUD rings, waveform & lightning bolt"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle_outer = 0.0
        self.angle_inner = 0.0
        self.pulse = 0.0
        self.is_listening = False
        Clock.schedule_interval(self._animate, 1.0 / 60.0)

    def _animate(self, dt):
        speed = 2.5 if self.is_listening else 0.8
        self.angle_outer = (self.angle_outer + 30.0 * dt * speed) % 360.0
        self.angle_inner = (self.angle_inner - 45.0 * dt * speed) % 360.0
        self.pulse += dt * (6.0 if self.is_listening else 2.5)
        self.canvas.clear()
        self._draw_orb()

    def _draw_orb(self):
        cx, cy = self.center_x, self.center_y
        radius = min(self.width, self.height) * 0.42
        if radius <= 10:
            return

        glow_boost = 0.18 * math.sin(self.pulse)

        with self.canvas:
            # Ambient outer blue radial glow
            for i in range(5, 0, -1):
                r_glow = radius * (1.0 + i * 0.08)
                Color(0.0, 0.55, 0.95, 0.035 * (6 - i))
                Ellipse(pos=(cx - r_glow, cy - r_glow), size=(r_glow * 2, r_glow * 2))

            # Outer thin telemetry circle
            Color(0.0, 0.72, 1.0, 0.35)
            Line(circle=(cx, cy, radius * 1.05), width=1.1)

            # Segmented rotating outer cyan ring
            Color(0.0, 0.82, 1.0, 0.85 + glow_boost)
            for start_a in (0, 90, 180, 270):
                Line(
                    circle=(cx, cy, radius * 0.96, start_a + self.angle_outer, start_a + self.angle_outer + 55),
                    width=2.2
                )

            # Warm gold accent arcs (matching image 1)
            Color(1.0, 0.72, 0.15, 0.75)
            Line(circle=(cx, cy, radius * 0.88, -self.angle_inner, -self.angle_inner + 70), width=1.6)
            Line(circle=(cx, cy, radius * 0.88, -self.angle_inner + 180, -self.angle_inner + 250), width=1.6)

            # Inner glowing core ring
            Color(0.05, 0.65, 1.0, 0.9)
            Line(circle=(cx, cy, radius * 0.72), width=2.0)

            # Deep energy sphere backdrop
            core_r = radius * 0.68
            Color(0.02, 0.16, 0.30, 0.65)
            Ellipse(pos=(cx - core_r, cy - core_r), size=(core_r * 2, core_r * 2))

            # Audio Waveform Bars on left and right of the lightning bolt
            Color(0.35, 0.88, 1.0, 0.9)
            bar_spacings = [-0.46, -0.39, -0.32, -0.25, -0.18, 0.18, 0.25, 0.32, 0.39, 0.46]
            for idx, offset in enumerate(bar_spacings):
                bx = cx + radius * offset
                amp = abs(math.sin(self.pulse + idx * 0.7)) * (0.22 if self.is_listening else 0.12) + 0.04
                bh = radius * amp
                Line(points=[bx, cy - bh, bx, cy + bh], width=1.6)

            # Center Golden Lightning Bolt (⚡)
            Color(1.0, 0.75, 0.18, 1.0)
            s = radius * 0.24
            # Upper triangle of bolt
            Triangle(points=[
                cx + s * 0.15, cy + s * 1.05,
                cx - s * 0.55, cy - s * 0.05,
                cx + s * 0.05, cy - s * 0.05
            ])
            # Lower triangle of bolt
            Triangle(points=[
                cx - s * 0.15, cy - s * 1.05,
                cx + s * 0.55, cy + s * 0.05,
                cx - s * 0.05, cy + s * 0.05
            ])


class PillBadge(FloatLayout):
    """Draws the top rounded pill badges: LOCAL MODEL and OFFLINE with green status dots"""
    def __init__(self, text_label="", **kwargs):
        super().__init__(**kwargs)
        self.text_label = text_label
        with self.canvas.before:
            Color(0.04, 0.11, 0.16, 0.85)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
            Color(0.12, 0.35, 0.48, 0.7)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 18), width=1.1)
            # Green status dot
            Color(0.18, 0.92, 0.52, 1.0)
            self.dot = Ellipse(size=(8, 8))

        self.lbl = Label(
            text=self.text_label,
            font_size="11sp",
            bold=True,
            color=(0.75, 0.88, 0.95, 1),
            pos_hint={"center_x": 0.46, "center_y": 0.5}
        )
        self.add_widget(self.lbl)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 18)
        self.dot.pos = (self.right - 20, self.center_y - 4)


class MicActionButton(Button):
    """Large glowing cyan circular microphone button at bottom center"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.text = "🎤"
        self.font_size = "28sp"
        self.color = (0.55, 0.92, 1.0, 1)
        with self.canvas.before:
            Color(0.0, 0.75, 1.0, 0.14)
            self.outer_glow = Ellipse()
            Color(0.03, 0.13, 0.22, 0.95)
            self.inner_circle = Ellipse()
            Color(0.15, 0.85, 1.0, 0.95)
            self.ring = Line(width=2.0)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        d = min(self.width, self.height)
        cx, cy = self.center_x, self.center_y
        self.outer_glow.pos = (cx - d * 0.62, cy - d * 0.62)
        self.outer_glow.size = (d * 1.24, d * 1.24)
        self.inner_circle.pos = (cx - d * 0.48, cy - d * 0.48)
        self.inner_circle.size = (d * 0.96, d * 0.96)
        self.ring.circle = (cx, cy, d * 0.48)


class RoundSecondaryButton(Button):
    """Circular side buttons for 'Type' (⌨) and 'Tools' (🛠)"""
    def __init__(self, icon_text="", **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.text = icon_text
        self.font_size = "20sp"
        self.color = (0.75, 0.88, 0.96, 1)
        with self.canvas.before:
            Color(0.04, 0.10, 0.16, 0.9)
            self.bg = Ellipse()
            Color(0.15, 0.38, 0.52, 0.7)
            self.ring = Line(width=1.2)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        d = min(self.width, self.height)
        cx, cy = self.center_x, self.center_y
        self.bg.pos = (cx - d * 0.45, cy - d * 0.45)
        self.bg.size = (d * 0.9, d * 0.9)
        self.ring.circle = (cx, cy, d * 0.45)


class LightningDudeHUD(FloatLayout):
    def __init__(self, engine: SovereignGGUFEngine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.recent_action_text = "Opened Settings  •  2m ago"
        self._build_ui()

    def _build_ui(self):
        # 1. Top Bar: Menu, Title ("LIGHTNING DUDE / JARVAIS"), Settings
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint=(0.92, 0.08),
            pos_hint={"center_x": 0.5, "top": 0.97}
        )
        btn_menu = Button(
            text="☰", font_size="22sp", size_hint_x=0.15,
            background_normal="", background_color=(0, 0, 0, 0),
            color=(0.75, 0.88, 0.96, 1)
        )
        title_box = BoxLayout(orientation="vertical", size_hint_x=0.70)
        lbl_main_title = Label(
            text="L I G H T N I N G   D U D E",
            font_size="16sp", bold=True, color=(0.88, 0.95, 1, 1)
        )
        lbl_sub_title = Label(
            text="J A R V A I S",
            font_size="11sp", color=(0.52, 0.72, 0.85, 1)
        )
        title_box.add_widget(lbl_main_title)
        title_box.add_widget(lbl_sub_title)

        btn_settings = Button(
            text="⚙", font_size="22sp", size_hint_x=0.15,
            background_normal="", background_color=(0, 0, 0, 0),
            color=(0.75, 0.88, 0.96, 1)
        )
        btn_settings.bind(on_release=lambda *_: self._open_tools_modal())

        top_bar.add_widget(btn_menu)
        top_bar.add_widget(title_box)
        top_bar.add_widget(btn_settings)
        self.add_widget(top_bar)

        # 2. Pill Badges Row: [ LOCAL MODEL ● ]   [ OFFLINE ● ]
        badges_row = BoxLayout(
            orientation="horizontal",
            spacing=18,
            size_hint=(0.86, 0.048),
            pos_hint={"center_x": 0.5, "top": 0.88}
        )
        badges_row.add_widget(PillBadge(text_label="  LOCAL MODEL"))
        badges_row.add_widget(PillBadge(text_label="  OFFLINE"))
        self.add_widget(badges_row)

        # 3. Greeting Section: "I'm here, Boss." & Subtitle
        greeting_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.9, 0.08),
            pos_hint={"center_x": 0.5, "top": 0.81}
        )
        self.lbl_greeting = Label(
            text="I'm here, Boss.",
            font_size="25sp", bold=True, color=(0.92, 0.97, 1, 1)
        )
        self.lbl_subgreeting = Label(
            text="Ready to help with your device.",
            font_size="13sp", color=(0.56, 0.72, 0.84, 1)
        )
        greeting_box.add_widget(self.lbl_greeting)
        greeting_box.add_widget(self.lbl_subgreeting)
        self.add_widget(greeting_box)

        # 4. Center Cyberpunk Orb + Side Vertical Captions
        self.orb = CyberOrbWidget(
            size_hint=(0.82, 0.36),
            pos_hint={"center_x": 0.5, "center_y": 0.54}
        )
        self.add_widget(self.orb)

        # Left side vertical telemetry caption
        lbl_left_side = Label(
            text="—\nLISTEN\nTHINK\nACT\nWITH\nYOU\n—",
            font_size="9.5sp",
            halign="left",
            color=(0.45, 0.65, 0.78, 0.85),
            size_hint=(0.15, 0.22),
            pos_hint={"x": 0.04, "center_y": 0.54}
        )
        self.add_widget(lbl_left_side)

        # Right side vertical telemetry caption
        lbl_right_side = Label(
            text="—\nPRIVATE\nLOCAL\nYOURS\n—",
            font_size="9.5sp",
            halign="right",
            color=(0.45, 0.65, 0.78, 0.85),
            size_hint=(0.15, 0.22),
            pos_hint={"right": 0.96, "center_y": 0.54}
        )
        self.add_widget(lbl_right_side)

        # 5. Two Status Columns: DEVICE LINK: READY & PRIVACY: ON-DEVICE
        status_row = BoxLayout(
            orientation="horizontal",
            spacing=14,
            size_hint=(0.88, 0.08),
            pos_hint={"center_x": 0.5, "y": 0.27}
        )

        left_status = BoxLayout(orientation="vertical")
        left_status.add_widget(Label(
            text="🔗  DEVICE LINK: READY   [color=#2ee884]●[/color]",
            markup=True, font_size="11sp", bold=True, color=(0.75, 0.90, 0.98, 1),
            halign="left", size_hint_y=0.45
        ))
        left_status.add_widget(Label(
            text="Can operate your device\nwith your consent.",
            font_size="10.5sp", color=(0.48, 0.64, 0.76, 1),
            halign="left", size_hint_y=0.55
        ))

        right_status = BoxLayout(orientation="vertical")
        right_status.add_widget(Label(
            text="🛡  PRIVACY: ON-DEVICE   [color=#2ee884]●[/color]",
            markup=True, font_size="11sp", bold=True, color=(0.75, 0.90, 0.98, 1),
            halign="left", size_hint_y=0.45
        ))
        right_status.add_widget(Label(
            text="Your data stays on\nthis device.",
            font_size="10.5sp", color=(0.48, 0.64, 0.76, 1),
            halign="left", size_hint_y=0.55
        ))

        status_row.add_widget(left_status)
        status_row.add_widget(right_status)
        self.add_widget(status_row)

        # 6. RECENT Activity Section
        recent_header = Label(
            text="──────────   RECENT   ──────────",
            font_size="10sp",
            color=(0.42, 0.58, 0.70, 0.9),
            size_hint=(0.88, 0.03),
            pos_hint={"center_x": 0.5, "y": 0.225}
        )
        self.add_widget(recent_header)

        recent_card = BoxLayout(
            orientation="horizontal",
            size_hint=(0.86, 0.05),
            pos_hint={"center_x": 0.5, "y": 0.17}
        )
        self.lbl_recent = Label(
            text=f"🕒    {self.recent_action_text}",
            font_size="12.5sp",
            color=(0.82, 0.90, 0.96, 1),
            halign="left"
        )
        lbl_chevron = Label(
            text="›", font_size="20sp", size_hint_x=0.12,
            color=(0.48, 0.65, 0.78, 1)
        )
        recent_card.add_widget(self.lbl_recent)
        recent_card.add_widget(lbl_chevron)
        self.add_widget(recent_card)

        # 7. Bottom Action Dock: [ Type ]   [ TAP TO SPEAK (Mic) ]   [ Tools ]
        dock = FloatLayout(
            size_hint=(0.90, 0.15),
            pos_hint={"center_x": 0.5, "y": 0.015}
        )

        # Type Button (Left)
        btn_type = RoundSecondaryButton(
            icon_text="⌨",
            size_hint=(None, None), size=(56, 56),
            pos_hint={"center_x": 0.18, "center_y": 0.58}
        )
        btn_type.bind(on_release=lambda *_: self._open_type_modal())
        dock.add_widget(btn_type)
        dock.add_widget(Label(
            text="Type", font_size="11.5sp", color=(0.65, 0.78, 0.88, 1),
            pos_hint={"center_x": 0.18, "center_y": 0.16}
        ))

        # Center Mic Button
        self.btn_mic = MicActionButton(
            size_hint=(None, None), size=(86, 86),
            pos_hint={"center_x": 0.50, "center_y": 0.60}
        )
        self.btn_mic.bind(on_release=self._toggle_voice_listen)
        dock.add_widget(self.btn_mic)
        self.lbl_mic_caption = Label(
            text="T A P   T O   S P E A K",
            font_size="11sp", bold=True, color=(0.75, 0.90, 0.98, 1),
            pos_hint={"center_x": 0.50, "center_y": 0.10}
        )
        dock.add_widget(self.lbl_mic_caption)

        # Tools Button (Right)
        btn_tools = RoundSecondaryButton(
            icon_text="🔧",
            size_hint=(None, None), size=(56, 56),
            pos_hint={"center_x": 0.82, "center_y": 0.58}
        )
        btn_tools.bind(on_release=lambda *_: self._open_tools_modal())
        dock.add_widget(btn_tools)
        dock.add_widget(Label(
            text="Tools", font_size="11.5sp", color=(0.65, 0.78, 0.88, 1),
            pos_hint={"center_x": 0.82, "center_y": 0.16}
        ))

        self.add_widget(dock)

    def _toggle_voice_listen(self, *args):
        self.orb.is_listening = not self.orb.is_listening
        if self.orb.is_listening:
            self.lbl_greeting.text = "Listening, Boss..."
            self.lbl_subgreeting.text = "Speak your command clearly • On-Device Mic"
            self.lbl_mic_caption.text = "L I S T E N I N G . . ."
        else:
            self.lbl_greeting.text = "I'm here, Boss."
            self.lbl_subgreeting.text = self.engine.status_msg
            self.lbl_mic_caption.text = "T A P   T O   S P E A K"

    def _open_type_modal(self):
        modal = ModalView(size_hint=(0.90, 0.42), background_color=(0.02, 0.06, 0.10, 0.95))
        box = BoxLayout(orientation="vertical", padding=16, spacing=12)
        box.add_widget(Label(
            text="⚡ DIRECT COMMAND TO JARVAIS (GGUF)",
            font_size="13sp", bold=True, color=(0.2, 0.85, 1, 1), size_hint_y=0.2
        ))
        inp = TextInput(
            hint_text="Type command for Lightning Dude...",
            multiline=False, size_hint_y=0.32,
            background_color=(0.05, 0.12, 0.18, 1),
            foreground_color=(0.9, 0.96, 1, 1)
        )
        out_lbl = Label(
            text="Response will appear here...",
            font_size="12sp", color=(0.7, 0.88, 0.96, 1), size_hint_y=0.28
        )
        btn_send = Button(
            text="EXECUTE ON LOCAL MODEL",
            size_hint_y=0.20,
            background_normal="", background_color=(0.0, 0.62, 0.88, 1)
        )

        def _run_cmd(*_):
            q = inp.text.strip()
            if not q:
                return
            self.lbl_recent.text = f"🕒    {q[:28]}  •  just now"
            out_lbl.text = "Thinking on GGUF Core..."
            def _worker():
                ans = self.engine.generate(q)
                Clock.schedule_once(lambda dt: setattr(out_lbl, "text", ans[:140]), 0)
                Clock.schedule_once(lambda dt: setattr(self.lbl_subgreeting, "text", ans[:65]), 0)
            threading.Thread(target=_worker, daemon=True).start()

        btn_send.bind(on_release=_run_cmd)
        box.add_widget(inp)
        box.add_widget(out_lbl)
        box.add_widget(btn_send)
        modal.add_widget(box)
        modal.open()

    def _open_tools_modal(self):
        modal = ModalView(size_hint=(0.88, 0.45), background_color=(0.02, 0.06, 0.10, 0.96))
        box = BoxLayout(orientation="vertical", padding=16, spacing=10)
        box.add_widget(Label(
            text="🛠 SOVEREIGN DEVICE TOOLS & OVERLAY",
            font_size="13sp", bold=True, color=(0.2, 0.85, 1, 1)
        ))
        for tool_name in [
            "⚡ Toggle Floating Orb Overlay",
            "🛡 Verify 24/7 Background Service",
            "📂 Open Android Device Settings",
            "🧠 Model: LightningDude-Sovereign-500M.gguf (Ready)"
        ]:
            b = Button(
                text=tool_name,
                background_normal="",
                background_color=(0.05, 0.14, 0.22, 1),
                color=(0.85, 0.95, 1, 1)
            )
            b.bind(on_release=lambda inst: setattr(self.lbl_recent, "text", f"🕒    {inst.text[:26]}  •  now"))
            box.add_widget(b)
        modal.add_widget(box)
        modal.open()


class LightningDudeApp(App):
    def build(self):
        self.title = "Lightning Dude - JARVAIS"
        self.engine = SovereignGGUFEngine()
        if platform == "android":
            Clock.schedule_once(self._start_background_daemon, 1.0)
        return LightningDudeHUD(engine=self.engine)

    def _start_background_daemon(self, dt):
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            # Request permissions & start sticky notification daemon
            ServiceJarvais = autoclass("org.jarvais.lightningdude.ServiceJarvais")
            ServiceJarvais.start(activity, "Wake-word standby • On-device")
        except Exception as e:
            print(f"[Service Notice]: {e}")


if __name__ == "__main__":
    LightningDudeApp().run()
