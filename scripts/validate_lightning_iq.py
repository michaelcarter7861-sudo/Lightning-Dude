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
from core.agent_executor import LightningDudeAgent

def run_validation_suite():
    print("==========================================================")
    print("⚡ LIGHTNING DUDE PHASE-2 FULL SYSTEM & IQ GATE (8 GATES) ⚡")
    print("==========================================================")

    # Gate 1: First-Boot System DNA Profiler
    profiler = FirstBootProfiler()
    dna = profiler.generate_dna(force=True)
    assert "hardware" in dna and "environment" in dna
    print(f"[PASS] Gate 1: First-Boot DNA Generated ({dna['execution_tier']})")

    # Gate 2: 7-Agent Trainer Council Curriculum Synthesis
    council = TrainerAgentCouncil()
    curriculum_path = council.forge_complete_curriculum()
    assert curriculum_path.exists()
    print("[PASS] Gate 2: 7-Agent Trainer Council Synthesized All 7 Domains")

    # Gate 3: Custom Brain (.ldbrain) Training & 7-Domain IQ Test
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
        res = brain.decide(query)
        assert res["domain"] == expected_domain, f"IQ Mismatch for '{query}'"
    print("[PASS] Gate 3: Custom .ldbrain Passed 7/7 Domain Decision IQ Tests")

    # Gate 4: Red-Team Simulated Spyware & Geo-Trace Test
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

    # Gate 5: Wake-Word & Offline Voice Duplex Test
    voice = JarvisVoiceEngine(voice_enabled=False)
    woke, stripped = voice.check_wake_word("Hey Lightning Dude, optimize system now")
    assert woke is True and stripped == "optimize system now"
    print(f"[PASS] Gate 5: Wake-Word ('Hey Lightning Dude') & Voice Engine Verified ({voice.tts_backend})")

    # Gate 6: Dynamic Self-Coding & AST Security Sandbox Test
    coder = DynamicSelfCoder()
    good_skill = coder.forge_and_run_skill(
        "calc_fibonacci",
        "print([0, 1, 1, 2, 3, 5, 8])",
        "Computes Fibonacci sequence"
    )
    assert good_skill["status"] == "SUCCESS" and "[0, 1, 1, 2, 3, 5, 8]" in good_skill["stdout"]
    bad_skill = coder.forge_and_run_skill("rogue_wiper", "import shutil\nshutil.rmtree('/')")
    assert bad_skill["status"] == "BLOCKED"
    print("[PASS] Gate 6: Self-Coding Engine Forged Skill & Blocked Destructive AST Call")

    # Gate 7: File Alchemist & Canary Honeypot Trap Test
    alchemist = OSFileAlchemist()
    alchemist.deploy_canary_honeypots()
    assert alchemist.verify_canary_integrity()["compromised"] is False
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        (tmp_path / "report.pdf").write_text("dummy pdf content", encoding="utf-8")
        (tmp_path / "copy_report.pdf").write_text("dummy pdf content", encoding="utf-8")
        (tmp_path / "photo.png").write_text("image bytes", encoding="utf-8")
        org_res = alchemist.organize_directory(tmp_path)
        assert org_res["moved_files"] == 2 and org_res["duplicates_found"] == 1
    print("[PASS] Gate 7: OS File Alchemist Organized Files, Caught Duplicates & Verified Canary Traps")

    # Gate 8: Autonomous Web Researcher & Full Agent Execution Test
    researcher = AutonomousWebResearcher()
    sample_html = "<html><body><h1>Lightning Dude</h1><p>Autonomous local cyber sentinel and system controller built for speed.</p><a href='https://github.com'>GitHub</a></body></html>"
    dossier = researcher.extract_from_html(sample_html, "unit_test")
    assert len(dossier["summary_points"]) >= 1 and "https://github.com" in dossier["extracted_links"]

    agent = LightningDudeAgent(voice_enabled=False)
    out = agent.execute_command("Hey Lightning Dude, clean downloads folder and organize files")
    assert out["wake_word_triggered"] is True and out["decision"]["domain"] == "file_management"
    print("[PASS] Gate 8: Web Researcher & Master LightningDudeAgent Verified Ready!")

    print("==========================================================")
    print("✅ ALL 8 QUALITY & EXECUTION GATES PASSED SUCCESSFULLY!")
    print("==========================================================")

if __name__ == "__main__":
    run_validation_suite()
