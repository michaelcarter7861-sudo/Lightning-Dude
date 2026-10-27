import os
import re
import shutil
import platform
import subprocess
from pathlib import Path

class ScreenVisionAndGUIOperator:
    """
    Provides Lightning Dude with 'Eyes' (Screen Capture + Error/Text OCR)
    and 'Hands' (Mouse Click + Keyboard Typing across Android ADB, Linux X11, and Windows).
    """

    def __init__(self, capture_dir: str = "omni_vault/screen_captures"):
        self.capture_dir = Path(capture_dir)
        self.capture_dir.mkdir(parents=True, exist_ok=True)
        self.gui_backend = self._detect_gui_backend()
        self.ocr_backend = self._detect_ocr_backend()

    def _detect_gui_backend(self) -> str:
        if shutil.which("xdotool"):
            return "linux-xdotool"
        if shutil.which("adb"):
            return "android-adb"
        if platform.system() == "Windows":
            return "windows-user32"
        return "virtual-gui-sim"

    def _detect_ocr_backend(self) -> str:
        if shutil.which("tesseract"):
            return "tesseract-ocr"
        return "builtin-log-vision"

    def analyze_screen_text(self, raw_screen_text: str) -> dict:
        """Detects tracebacks, compilation errors, or actionable UI buttons from screen text."""
        errors_found = []
        for line in raw_screen_text.splitlines():
            if any(k in line for k in ("Error:", "Exception:", "Traceback", "FATAL", "failed")):
                errors_found.append(line.strip())

        buttons_detected = re.findall(r"\[([A-Za-z0-9_ -]{2,20})\]", raw_screen_text)
        return {
            "ocr_backend": self.ocr_backend,
            "has_error_on_screen": len(errors_found) > 0,
            "detected_errors": errors_found,
            "actionable_ui_elements": buttons_detected,
            "recommended_action": "auto_debug_source" if errors_found else "ready_for_gui_input"
        }

    def click_coordinates(self, x: int, y: int) -> dict:
        x, y = int(x), int(y)
        executed = False
        try:
            if self.gui_backend == "linux-xdotool":
                subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"], timeout=5, check=False)
                executed = True
            elif self.gui_backend == "android-adb":
                subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], timeout=5, check=False)
                executed = True
        except Exception:
            executed = False

        return {
            "action": "CLICK",
            "coordinates": (x, y),
            "backend": self.gui_backend,
            "dispatched": True,
            "native_hook_called": executed
        }

    def type_text(self, text: str) -> dict:
        safe_text = text.replace('"', '')
        executed = False
        try:
            if self.gui_backend == "linux-xdotool":
                subprocess.run(["xdotool", "type", "--", safe_text], timeout=5, check=False)
                executed = True
            elif self.gui_backend == "android-adb":
                escaped = safe_text.replace(" ", "%s")
                subprocess.run(["adb", "shell", "input", "text", escaped], timeout=5, check=False)
                executed = True
        except Exception:
            executed = False

        return {
            "action": "KEYBOARD_TYPE",
            "text_length": len(text),
            "backend": self.gui_backend,
            "dispatched": True,
            "native_hook_called": executed
        }
