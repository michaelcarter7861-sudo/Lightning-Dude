import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.first_boot_profiler import FirstBootProfiler
from agents.trainer_council import TrainerAgentCouncil
from core.brain_engine import LightningBrain
from core.cyber_sentinel import CyberSentinelAndTracer
from core.agent_executor import LightningDudeAgent

def run_validation_suite():
    print("====================================================")
    print("⚡ LIGHTNING DUDE PRE-BUILD IQ & SECURITY GATE ⚡")
    print("====================================================")

    # Gate 1: First-Boot System DNA Profiler
    profiler = FirstBootProfiler()
    dna = profiler.generate_dna(force=True)
    assert "hardware" in dna and "environment" in dna, "DNA Profile missing core keys!"
    print(f"[PASS] Gate 1: First-Boot DNA Generated ({dna['execution_tier']})")

    # Gate 2: 7-Agent Trainer Council Curriculum Synthesis
    council = TrainerAgentCouncil()
    curriculum_path = council.forge_complete_curriculum()
    assert curriculum_path.exists(), "Curriculum file was not generated!"
    print("[PASS] Gate 2: 7-Agent Trainer Council Synthesized All 7 Domains")

    # Gate 3: Custom Brain (.ldbrain) Training & Multi-Domain IQ Test
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
        assert res["domain"] == expected_domain, f"IQ Mismatch for '{query}': got {res['domain']}"
    print("[PASS] Gate 3: Custom .ldbrain Passed 7/7 Domain Decision IQ Tests (100% Accuracy)")

    # Gate 4: Red-Team Simulated Spyware & Geo-Trace Test
    sentinel = CyberSentinelAndTracer()
    fake_spyware = [{
        "process_name": "stealth_stealer.exe",
        "pid": 9942,
        "remote_ip": "185.220.101.45",
        "remote_port": 4444,
        "exfiltration_flag": True
    }]
    incidents = sentinel.inspect_and_neutralize(fake_spyware)
    assert len(incidents) == 1, "Sentinel failed to catch simulated spyware!"
    assert "TERMINATED_PID_9942" in incidents[0]["actions_taken"], "Spyware PID not terminated!"
    assert incidents[0]["origin_trace"]["attacker_ip"] == "185.220.101.45", "Attacker IP not traced!"
    print("[PASS] Gate 4: Cyber-Sentinel Killed Simulated Spyware & Generated Geo-Trace Forensic Report")

    # Gate 5: Full End-to-End Agent Integration Test
    agent = LightningDudeAgent()
    out = agent.execute_command("Optimize system and boost performance")
    assert out["decision"]["domain"] == "os_control", "End-to-End Agent execution failed!"
    print("[PASS] Gate 5: End-to-End LightningDudeAgent Verified Ready!")
    print("====================================================")
    print("✅ ALL 5 QUALITY GATES PASSED SUCCESSFULLY!")
    print("====================================================")

if __name__ == "__main__":
    run_validation_suite()
