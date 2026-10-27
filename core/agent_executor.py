from pathlib import Path
from core.first_boot_profiler import FirstBootProfiler
from core.brain_engine import LightningBrain
from core.cyber_sentinel import CyberSentinelAndTracer

class LightningDudeAgent:
    """
    Unified Master Agent combining:
    1. Custom Brain (.ldbrain)
    2. First-Boot System DNA Profiler
    3. OS / File / GUI / Self-Coding Executor
    4. Cyber-Sentinel & Location Tracer
    """

    def __init__(self):
        self.profiler = FirstBootProfiler()
        self.dna = self.profiler.generate_dna(force=False)
        self.brain = LightningBrain()
        self.sentinel = CyberSentinelAndTracer()

    def execute_command(self, command_text: str) -> dict:
        decision = self.brain.decide(command_text)
        return {
            "agent": "Lightning Dude",
            "execution_tier": self.dna.get("execution_tier"),
            "command": command_text,
            "decision": decision
        }
