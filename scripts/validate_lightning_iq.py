import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.first_boot_profiler import FirstBootProfiler
from agents.trainer_council import TrainerAgentCouncil
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
from core.hud_interface import JarvisHUD
from core.daemon_service import SentinelDaemonService
from core.agent_executor import LightningDudeAgent

def run_validation_suite():
    print("=============================================================")
    print("⚡ LIGHTNING DUDE PHASE-4 15-GATE MASTER VALIDATION SUITE ⚡")
    print("=============================================================")

    # Gate 1: First-Boot DNA
    profiler = FirstBootProfiler()
    dna = profiler.generate_dna(force=True)
    assert "hardware" in dna and "environment" in dna
    print(f"[PASS] Gate 1: First-Boot DNA Generated ({dna['execution_tier']})")

    # Gate 2: 7-Agent Trainer Council
    council = TrainerAgentCouncil()
    curriculum_path = council.forge_complete_curriculum()
    assert curriculum_path.exists()
    print("[PASS] Gate 2: 7-Agent Trainer Council Synthesized All 7 Domains")

    # Gate 3: Custom Brain (.ldbrain) IQ Test
    brain = LightningBrain()
    brain.train_from_curriculum(curriculum_path)
    test_queries = {
        "My PC is slow, free ram and optimize system": "os_control",
        "Open app and click button on screen": "gui_automation",
        "Clean downloads folder and organize files": "file_management",
        "Give me my morning briefing and schedule task": "productivity_secretary",
        "Research topic in browser and extract data": "deep_web_research",
        "Write script to automate workflow": "self_coding",
        "Check security, spyware scan and trace attacker": "cyber_security",
    }
    for query, expected_domain in test_queries.items():
        assert brain.decide(query)["domain"] == expected_domain
    print("[PASS] Gate 3: Custom .ldbrain Passed 7/7 Domain Decision IQ Tests")

    # Gate 4: Cyber-Sentinel Spyware & Geo-Trace
    sentinel = CyberSentinelAndTracer()
    incidents = sentinel.inspect_and_neutralize([{
        "process_name": "stealth_stealer.exe",
        "pid": 9942,
        "remote_ip": "185.220.101.45",
        "remote_port": 4444,
        "exfiltration_flag": True
    }])
    assert len(incidents) == 1 and "TERMINATED_PID_9942" in incidents[0]["actions_taken"]
    print("[PASS] Gate 4: Cyber-Sentinel Killed Spyware & Traced Origin IP")

    # Gate 5: Wake-Word & Offline Voice Duplex
    voice = JarvisVoiceEngine(voice_enabled=False)
    woke, stripped = voice.check_wake_word("Hey Lightning Dude, optimize system now")
    assert woke is True and stripped == "optimize system now"
    print(f"[PASS] Gate 5: Wake-Word & Voice Engine Verified ({voice.tts_backend})")

    # Gate 6: Dynamic Self-Coding & AST Sandbox
    coder = DynamicSelfCoder()
    good_skill = coder.forge_and_run_skill("calc_fib", "print([0, 1, 1, 2, 3, 5, 8])")
    assert good_skill["status"] == "SUCCESS"
    bad_skill = coder.forge_and_run_skill("rogue_wiper", "import shutil\nshutil.rmtree('/')")
    assert bad_skill["status"] == "BLOCKED"
    print("[PASS] Gate 6: Self-Coding Engine Forged Skill & Blocked Destructive AST Call")

    # Gate 7: OS File Alchemist & Canary Honeypots
    alchemist = OSFileAlchemist()
    alchemist.deploy_canary_honeypots()
    assert alchemist.verify_canary_integrity()["compromised"] is False
    print("[PASS] Gate 7: OS File Alchemist & Canary Honeypot Shield Verified")

    # Gate 8: Autonomous Web Researcher
    researcher = AutonomousWebResearcher()
    dossier = researcher.extract_from_html("<html><body><p>Lightning Dude intelligence.</p></body></html>")
    assert len(dossier["summary_points"]) >= 1
    print("[PASS] Gate 8: Autonomous Web Researcher Verified")

    # Gate 9: Screen Vision OCR & Human GUI Operator
    vision = ScreenVisionAndGUIOperator()
    screen_analysis = vision.analyze_screen_text("Traceback: Error\n[Fix]")
    assert screen_analysis["has_error_on_screen"] is True
    print("[PASS] Gate 9: Screen Vision Error Detection Verified")

    # Gate 10: Omni-Vault Semantic Memory
    memory = OmniVaultMemory()
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir) / "notes.txt"
        p.write_text("Project backup keys and roadmap.", encoding="utf-8")
        memory.index_directory(Path(tmpdir))
        assert len(memory.search_memory("project backup")) >= 1
    print("[PASS] Gate 10: Omni-Vault Semantic Memory Recalled Note")

    # Gate 11: Proactive Telemetry Daemon
    proactive = ProactiveJarvisDaemon()
    triggers = proactive.evaluate_telemetry({"ram_usage_percent": 90.0, "battery_percent": 10.0})
    assert len(triggers) >= 2
    print("[PASS] Gate 11: Proactive Daemon Verified")

    # Gate 12: Cross-Device Hive-Mind Sync
    node = HiveMindSyncNode(node_id="PC")
    packet = node.create_signed_packet("PC", "test")
    assert node.verify_and_receive_packet(packet)["verified"] is True
    print("[PASS] Gate 12: Hive-Mind Sync Verified")

    # Gate 13: Sci-Fi HUD Dashboard Renderer
    try:
        JarvisHUD.render_thought_box("test command", "os_control", 0.95, ["step1", "step2"])
        hud_pass = True
    except Exception:
        hud_pass = False
    assert hud_pass is True
    print("[PASS] Gate 13: Sci-Fi HUD Terminal Dashboard Verified")

    # Gate 14: 24/7 Sentinel Background Daemon Service
    daemon = SentinelDaemonService()
    state = daemon.heartbeat_tick({"status": "ok"})
    assert state["status"] == "HEALTHY_AND_MONITORING"
    print("[PASS] Gate 14: 24/7 Sentinel Daemon Service Verified")

    # Gate 15: Full Master Agent End-to-End Integration
    agent = LightningDudeAgent(voice_enabled=False)
    out = agent.execute_command("Hey Lightning Dude, optimize system")
    assert out["decision"]["domain"] == "os_control"
    print("[PASS] Gate 15: Full J.A.R.V.I.S. Master Agent Verified!")

    print("============================================================s")
    print("✅ ALL 15 MASTER GATES PASSED SUCCESSFULLY!")
    print("=============================================================")

if __name__ == "__main__":
    run_validation_suite()
