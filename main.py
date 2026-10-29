import os
import threading
from pathlib import Path
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

# Set Holo Dark Cyberpunk Background
Window.clearcolor = (0.02, 0.05, 0.08, 1)

class JarvaisChatBubble(BoxLayout):
    def __init__(self, sender, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = [15, 10, 15, 10]
        self.spacing = 5

        is_user = sender == "BOSS"
        
        # Header Label
        header = Label(
            text=f"[{sender}]",
            size_hint_y=None,
            height=24,
            font_size=13,
            bold=True,
            halign='right' if is_user else 'left',
            valign='middle'
        )
        header.bind(size=header.setter('text_size'))
        header.color = (0.2, 0.8, 1, 1) if is_user else (0.0, 1.0, 0.4, 1)

        # Message Content Label
        content = Label(
            text=text,
            size_hint_y=None,
            font_size=15,
            halign='right' if is_user else 'left',
            valign='middle'
        )
        content.bind(
            width=lambda *x: setattr(content, 'text_size', (content.width, None)),
            texture_size=lambda *x: setattr(content, 'height', content.texture_size[1])
        )
        content.color = (0.9, 0.9, 0.9, 1)

        self.add_widget(header)
        self.add_widget(content)
        self.bind(minimum_height=self.setter('height'))

class LightningDudeRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 12
        self.spacing = 10

        # 1. Top HUD Status Bar
        self.hud_bar = Label(
            text="[JARVAIS SOVEREIGN HUD] CPU: 12.5% | RAM: 42.0% | STATUS: ONLINE",
            size_hint_y=None,
            height=40,
            font_size=13,
            bold=True
        )
        self.hud_bar.color = (0.0, 1.0, 0.8, 1)
        self.add_widget(self.hud_bar)

        # 2. Chat Scroll Window
        self.scroll = ScrollView(size_hint=(1, 1))
        self.chat_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=[5, 5, 5, 5]
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.scroll.add_widget(self.chat_layout)
        self.add_widget(self.scroll)

        # 3. Bottom Input Control Panel
        input_panel = BoxLayout(size_hint_y=None, height=55, spacing=8)
        
        self.user_input = TextInput(
            hint_text="Hukam dein Boss...",
            size_hint=(0.75, 1),
            multiline=False,
            background_color=(0.05, 0.1, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 1, 0.5, 1),
            padding=[10, 15, 10, 10]
        )
        self.user_input.bind(on_text_validate=self.send_command)

        self.send_btn = Button(
            text="EXECUTE",
            size_hint=(0.25, 1),
            background_color=(0.0, 0.6, 0.3, 1),
            bold=True
        )
        self.send_btn.bind(on_press=self.send_command)

        input_panel.add_widget(self.user_input)
        input_panel.add_widget(self.send_btn)
        self.add_widget(input_panel)

        # Initial Greeting
        Clock.schedule_once(lambda dt: self.append_message("JARVAIS", "Assalam-o-Alaikum Boss! Lightning Dude Sovereign Core active hai. Farmayiye kya hukum hai?"), 0.5)

    def append_message(self, sender, text):
        bubble = JarvaisChatBubble(sender, text, size_hint_width=1)
        self.chat_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)

    def send_command(self, instance):
        query = self.user_input.text.strip()
        if not query:
            return

        self.append_message("BOSS", query)
        self.user_input.text = ""
        
        # Process in background thread to keep UI fluid
        threading.Thread(target=self.process_jarvais_response, args=(query,)).start()

    def process_jarvais_response(self, query):
        # Neural response simulation / model integration point
        response = f"Jee Boss! Aapke hukum '{query}' par sovereign neural engine aur self-healing vault ke zariye amal kiya ja raha hai. System fully operational hai."
        
        # Update UI safely from main thread
        Clock.schedule_once(lambda dt: self.append_message("JARVAIS", response), 0.1)

class LightningDudeApp(App):
    def build(self):
        self.title = "Lightning Dude JARVAIS"
        return LightningDudeRoot()

if __name__ == '__main__':
    LightningDudeApp().run()
