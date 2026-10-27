import sys
import json
import argparse
from core.agent_executor import LightningDudeAgent
from agents.trainer_council import TrainerAgentCouncil
from core.hud_interface import JarvisHUD
from core.daemon_service import SentinelDaemonService

def ensure_brain_ready(agent: LightningDudeAgent):
    if not agent.brain.brain_path.exists():
        council = TrainerAgentCouncil()
        curriculum = council.forge_complete_curriculum()
        agent.brain.train_from_curriculum(curriculum)

def main():
    parser = argparse.ArgumentParser(description="Lightning Dude - Autonomous J.A.R.V.I.S. AI")
    parser.add_argument("--cmd", type=str, help="Run a single command and exit")
    parser.add_argument("--voice", action="store_true", help="Enable offline TTS voice output")
    parser.add_argument("--hud", action="store_true", help="Enable Sci-Fi HUD dashboard")
    args = parser.parse_args()

    agent = LightningDudeAgent(voice_enabled=args.voice)
    ensure_brain_ready(agent)
    daemon = SentinelDaemonService()

    if args.hud or not args.cmd:
        JarvisHUD.render_banner(agent.dna['execution_tier'], agent.voice.tts_backend, agent.voice.stt_backend)

    if args.cmd:
        res = agent.execute_command(args.cmd)
        if args.hud:
            JarvisHUD.render_thought_box(res["command"], res["decision"]["domain"], res["decision"]["confidence"], res["decision"]["plan"])
        print(json.dumps(res, indent=2))
        return

    print("Type your command or 'exit' to quit.\n")

    while True:
        try:
            user_in = agent.voice.listen_once()
            if not user_in or user_in.lower() in ("exit", "quit"):
                agent.voice.speak("Powering down standby loop, Sir.")
                break

            daemon.heartbeat_tick({"ram_usage_percent": 45.0, "battery_percent": 80.0, "canary_compromised": False})
            res = agent.execute_command(user_in)
            JarvisHUD.render_thought_box(res["command"], res["decision"]["domain"], res["decision"]["confidence"], res["decision"]["plan"])
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
