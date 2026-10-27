from pathlib import Path
from core.first_boot_profiler import FirstBootProfiler
from core.brain_engine import LightningBrain
from core.cyber_sentinel import CyberSentinelAndTracer
from core.voice_duplex import JarvisVoiceEngine
from core.self_coder import DynamicSelfCoder
from core.os_file_alchemist import OSFileAlchemist
from core.web_researcher import AutonomousWebResearcher

class LightningDudeAgent:
    """
    Master Autonomous J.A.R.V.I.S. Engine combining:
    - Custom Brain (.ldbrain)
    - First-Boot System DNA Profiler
    - Offline Voice & Wake-Word Duplex Engine
    - Dynamic Self-Coding Engine (Skills Vault)
    - OS File Alchemist & Canary Honeypot Shield
    - Autonomous Web Researcher
    - Cyber-Sentinel & Attacker Geo-Location Tracer
    """

    def __init__(self, voice_enabled: bool = False):
        self.profiler = FirstBootProfiler()
        self.dna = self.profiler.generate_dna(force=False)
        self.brain = LightningBrain()
        self.sentinel = CyberSentinelAndTracer()
        self.voice = JarvisVoiceEngine(voice_enabled=voice_enabled)
        self.coder = DynamicSelfCoder()
        self.alchemist = OSFileAlchemist()
        self.researcher = AutonomousWebResearcher()
        self.alchemist.deploy_canary_honeypots()

    def execute_command(self, raw_input: str) -> dict:
        woke, clean_cmd = self.voice.check_wake_word(raw_input)
        decision = self.brain.decide(clean_cmd)
        canary_status = self.alchemist.verify_canary_integrity()
        self.voice.speak(decision["voice_response"])

        return {
            "agent": "Lightning Dude",
            "wake_word_triggered": woke,
            "execution_tier": self.dna.get("execution_tier"),
            "command": clean_cmd,
            "decision": decision,
            "canary_shield_intact": not canary_status["compromised"]
        }
