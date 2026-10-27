import sys
import json
import argparse
from core.agent_executor import LightningDudeAgent
from agents.trainer_council import TrainerAgentCouncil

def ensure_brain_ready(agent: LightningDudeAgent):
    if not agent.brain.brain_path.exists():
        council = TrainerAgentCouncil()
        curriculum = council.forge_complete_curriculum()
        agent.brain.train_from_curriculum(curriculum)

def main():
    parser = argparse.ArgumentParser(description="Lightning Dude - Autonomous J.A.R.V.I.S. AI")
    parser.add_argument("--cmd", type=str, help="Run a single command and exit")
    parser.add_argument("--voice", action="store_true", help="Enable offline TTS voice output")
    parser.add_argument("--dna", action="store_true", help="Print full device System DNA")
    args = parser.parse_args()

    agent = LightningDudeAgent(voice_enabled=args.voice)
    ensure_brain_ready(agent)

    if args.dna:
        print(json.dumps(agent.dna, indent=2))
        return

    if args.cmd:
        res = agent.execute_command(args.cmd)
        print(json.dumps(res, indent=2))
        return

    print("====================================================")
    print(f"⚡ LIGHTNING DUDE ONLINE | TIER: {agent.dna['execution_tier']}")
    print(f"🎙️ TTS Backend: {agent.voice.tts_backend} | STT: {agent.voice.stt_backend}")
    print("Type 'exit' to quit.")
    print("====================================================")

    while True:
        try:
            user_in = agent.voice.listen_once()
            if not user_in or user_in.lower() in ("exit", "quit"):
                agent.voice.speak("Powering down standby loop, Sir.")
                break
            res = agent.execute_command(user_in)
            print(f"[Plan]: {' -> '.join(res['decision']['plan'])}")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
