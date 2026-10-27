import time
import json
from pathlib import Path

class SentinelDaemonService:
    """
    Runs in the background to monitor system telemetry, canary traps,
    and trigger proactive routines without blocking the user.
    """

    def __init__(self, state_file: str = "omni_vault/daemon_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def heartbeat_tick(self, telemetry: dict) -> dict:
        timestamp = int(time.time())
        state = {
            "last_heartbeat": timestamp,
            "telemetry_received": telemetry,
            "status": "HEALTHY_AND_MONITORING"
        }
        self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state
