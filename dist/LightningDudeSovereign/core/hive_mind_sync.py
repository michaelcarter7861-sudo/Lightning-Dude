import json
import hmac
import time
import hashlib

class HiveMindSyncNode:
    """
    Allows Lightning Dude on Android and PC to securely authenticate and dispatch
    cross-device commands over LAN without any cloud server.
    """

    def __init__(self, node_id: str, shared_secret: str = "LIGHTNING_DUDE_HIVE_SECRET_KEY"):
        self.node_id = node_id
        self.shared_secret = shared_secret.encode("utf-8")

    def create_signed_packet(self, target_node: str, remote_command: str) -> dict:
        payload = {
            "source_node": self.node_id,
            "target_node": target_node,
            "command": remote_command,
            "timestamp": int(time.time())
        }
        raw_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature = hmac.new(self.shared_secret, raw_bytes, hashlib.sha256).hexdigest()
        return {"payload": payload, "hmac_sha256": signature}

    def verify_and_receive_packet(self, packet: dict) -> dict:
        payload = packet.get("payload", {})
        sig = packet.get("hmac_sha256", "")
        raw_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        expected_sig = hmac.new(self.shared_secret, raw_bytes, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(sig, expected_sig):
            return {"verified": False, "reason": "INVALID_HMAC_SIGNATURE"}

        return {
            "verified": True,
            "source_node": payload.get("source_node"),
            "command": payload.get("command")
        }
