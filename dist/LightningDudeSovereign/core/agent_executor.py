from pathlib import Path
from core.first_boot_profiler import FirstBootProfiler
from core.brain_engine import LightningBrain
from core.cyber_sentinel import CyberSentinelAndTracer
from core.voice_duplex import JarvisVoiceEngine
from core.self_coder import DynamicSelfCoder
from core.os_file_alchemist import OSFileAlchemist
from core.web_researcher import AutonomousWebResearcher
from core.screen_vision_gui import ScreenVisionAndGUIOperator
from core.omni_vault_memory import OmniVaultMemory
from core.proactive_daemon import ProactiveJarvisDaemon
from core.hive_mind_sync import HiveMindSyncNode

class LightningDudeAgent:
    """
    Complete J.A.R.V.I.S.-Class Autonomous System:
    - Custom Brain (.ldbrain) + 7-Agent Distilled Knowledge
    - First-Boot System DNA Profiler
    - Offline Voice & Wake-Word Duplex Engine
    - Dynamic Self-Coding Engine (Skills Vault)
    - OS File Alchemist & Canary Honeypot Shield
    - Autonomous Web Researcher
    - Cyber-Sentinel & Attacker Geo-Location Tracer
    - Screen Vision OCR & Human GUI Operator
    - Omni-Vault Semantic File & Episodic Memory
    - Proactive Telemetry & Habit Daemon
    - Cross-Device Hive-Mind LAN Sync
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
        self.vision_gui = ScreenVisionAndGUIOperator()
        self.memory = OmniVaultMemory()
        self.proactive = ProactiveJarvisDaemon()
        self.hive = HiveMindSyncNode(node_id=self.dna["environment"]["hostname"])
        self.alchemist.deploy_canary_honeypots()

    def execute_command(self, raw_input: str) -> dict:
        woke, clean_cmd = self.voice.check_wake_word(raw_input)
        decision = self.brain.decide(clean_cmd)
        canary_status = self.alchemist.verify_canary_integrity()
        self.voice.speak(decision["voice_response"])
        self.memory.remember_episode(clean_cmd, decision["domain"], "EXECUTED")

        return {
            "agent": "Lightning Dude",
            "wake_word_triggered": woke,
            "execution_tier": self.dna.get("execution_tier"),
            "command": clean_cmd,
            "decision": decision,
            "canary_shield_intact": not canary_status["compromised"]
        }
