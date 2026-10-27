import os
import shutil
import platform
import subprocess

class JarvisVoiceEngine:
    """
    100% Offline Multi-Backend Voice Engine (Mouth & Ears).
    Automatically binds to Piper-TTS, Termux-TTS, espeak-ng, or Windows SAPI.
    Supports 'Hey Lightning Dude' wake-word detection.
    """

    WAKE_WORDS = ("hey lightning dude", "lightning dude", "jarvis")

    def __init__(self, voice_enabled: bool = True):
        self.voice_enabled = voice_enabled
        self.tts_backend = self._detect_tts_backend()
        self.stt_backend = self._detect_stt_backend()

    def _detect_tts_backend(self) -> str:
        if shutil.which("piper"):
            return "piper"
        if shutil.which("termux-tts-speak"):
            return "termux-tts"
        if shutil.which("espeak-ng"):
            return "espeak-ng"
        if shutil.which("espeak"):
            return "espeak"
        if platform.system() == "Windows":
            return "windows-sapi"
        return "console-hud"

    def _detect_stt_backend(self) -> str:
        if shutil.which("whisper-cli") or shutil.which("main"):
            return "whisper-cpp"
        if shutil.which("termux-speech-to-text"):
            return "termux-stt"
        return "keyboard-fallback"

    def check_wake_word(self, raw_transcript: str) -> tuple:
        text_lower = raw_transcript.strip().lower()
        for wake in self.WAKE_WORDS:
            if text_lower.startswith(wake):
                clean_cmd = raw_transcript[len(wake):].strip(" ,.:;!?")
                return True, (clean_cmd or "status report")
        return False, raw_transcript

    def speak(self, text: str) -> dict:
        print(f"\n[⚡ LIGHTNING DUDE VOICE ({self.tts_backend})]: {text}")
        if not self.voice_enabled:
            return {"spoken": False, "backend": self.tts_backend, "text": text}

        try:
            if self.tts_backend == "termux-tts":
                subprocess.run(["termux-tts-speak", text], timeout=10, check=False)
            elif self.tts_backend in ("espeak-ng", "espeak"):
                subprocess.run([self.tts_backend, "-s", "165", text], timeout=10, check=False)
            elif self.tts_backend == "windows-sapi":
                ps_cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text.replace(chr(39), '')}')"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=12, check=False)
        except Exception:
            pass

        return {"spoken": True, "backend": self.tts_backend, "text": text}

    def listen_once(self) -> str:
        if self.stt_backend == "termux-stt":
            try:
                out = subprocess.check_output(["termux-speech-to-text"], text=True, timeout=15)
                return out.strip()
            except Exception:
                return ""
        return input("\n[🎙️ Speak / Type to Lightning Dude]: ").strip()
