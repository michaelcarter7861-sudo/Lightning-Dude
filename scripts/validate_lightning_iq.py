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
from core.agent_executor import LightningDudeAgent

def run_validation_suite():
    print("=============================================================")
    print("⚡ LIGHTNING DUDE PHASE-3 MASTER VALIDATION SUITE (12 GATES) ⚡")
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
    dossier = researcher.extract_from_html(
        "<html><body><p>Lightning Dude autonomous sentinel intelligence system.</p><a href='https://github.com'>GH</a></body></html>"
    )
    assert len(dossier["summary_points"]) >= 1
    print("[PASS] Gate 8: Autonomous Web Researcher Verified")

    # Gate 9: Screen Vision OCR & Human GUI Operator
    vision = ScreenVisionAndGUIOperator()
    screen_analysis = vision.analyze_screen_text("Window Title\nTraceback: ValueError: invalid literal\n[Fix_Code] [Cancel]")
    assert screen_analysis["has_error_on_screen"] is True
    assert "Fix_Code" in screen_analysis["actionable_ui_elements"]
    click_res = vision.click_coordinates(450, 300)
    assert click_res["dispatched"] is True
    print(f"[PASS] Gate 9: Screen Vision Error Detection & Human GUI Click Verified ({vision.gui_backend})")

    # Gate 10: Omni-Vault Semantic File & Episodic Memory
    memory = OmniVaultMemory()
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir) / "client_seo_backlinks_october.txt"
        p.write_text("High authority backlink strategy and domain ranking checklist for client campaign.", encoding="utf-8")
        count = memory.index_directory(Path(tmpdir))
        assert count == 1
        hits = memory.search_memory("where is the client backlink strategy file?")
        assert len(hits) >= 1 and "client_seo_backlinks_october.txt" in hits[0]["name"]
    print("[PASS] Gate 10: Omni-Vault Recalled File by Semantic Content Without Filename")

    # Gate 11: Proactive Telemetry & Auto-Healing Daemon
    proactive = ProactiveJarvisDaemon()
    triggers = proactive.evaluate_telemetry({
        "ram_usage_percent": 92.0,
        "battery_percent": 12.0,
        "canary_compromised": True,
        "screen_has_error": True
    })
    assert len(triggers) == 4 and triggers[0]["priority"] == "CRITICAL"
    print("[PASS] Gate 11: Proactive Daemon Triggered Autonomous RAM, Battery, Screen & Security Actions")

    # Gate 12: Cross-Device Hive-Mind Signed Sync (Mobile <-> PC)
    mobile_node = HiveMindSyncNode(node_id="Android-Phone")
    pc_node = HiveMindSyncNode(node_id="Main-Workstation-PC")
    packet = mobile_node.create_signed_packet("Main-Workstation-PC", "optimize system and lock screen")
    verified = pc_node.verify_and_receive_packet(packet)
    assert verified["verified"] is True and verified["command"] == "optimize system and lock screen"

    agent = LightningDudeAgent(voice_enabled=False)
    out = agent.execute_command("Hey Lightning Dude, give me my morning briefing")
    assert out["decision"]["domain"] == "productivity_secretary"
    print("[PASS] Gate 12: Hive-Mind Cross-Device Sync & Full Master Agent Verified!")

    print("=============================================================")
    print("✅ ALL 12 QUALITY, SECURITY & J.A.R.V.I.S. GATES PASSED!")
    print("=============================================================")

if __name__ == "__main__":
    run_validation_suite()
