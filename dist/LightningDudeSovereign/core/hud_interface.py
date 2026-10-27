import os
import time

class JarvisHUD:
    """Renders a futuristic Sci-Fi J.A.R.V.I.S. Heads-Up Display (HUD) in the terminal."""

    @staticmethod
    def render_banner(tier: str, tts_backend: str, stt_backend: str):
        os.system("clear" if os.name == "posix" else "cls")
        print("==================================================================")
        print(" ⚡ L I G H T N I N G   D U D E   [J.A.R.V.I.S. SCI-FI HUD v4.0] ⚡")
        print("==================================================================")
        print(f" [CORE STATUS] : ACTIVE & AUTONOMOUS")
        print(f" [SYSTEM TIER] : {tier}")
        print(f" [VOICE ENGINE] : TTS -> {tts_backend} | STT -> {stt_backend}")
        print(f" [SECURITY]    : YARA Scan + Canary Honeypot Active")
        print("==================================================================")

    @staticmethod
    def render_thought_box(command: str, domain: str, confidence: float, plan: list):
        print(f"\n[🧠 COGNITIVE CORTEX]")
        print(f" ├── User Command : \"{command}\"")
        print(f" ├── Target Domain: {domain.upper()} (Confidence: {confidence * 100:.0f}%)")
        print(f" └── GOAP Action Plan:")
        for idx, step in enumerate(plan, 1):
            print(f"      [{idx}] ──► {step}")
        print("-" * 66)
