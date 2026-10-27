import json
import math
from pathlib import Path
from collections import Counter

BRAIN_WEIGHTS_PATH = Path("core/lightning_dude.ldbrain")

class LightningBrain:
    """
    100% Self-Contained Custom Cognitive + GOAP Decision Engine (.ldbrain).
    Requires ZERO external LLMs or cloud APIs.
    """

    def __init__(self, brain_path: Path = BRAIN_WEIGHTS_PATH):
        self.brain_path = brain_path
        self.memory_graph = []

    @staticmethod
    def _tokenize(text: str) -> list:
        clean = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return [tok for tok in clean.split() if len(tok) > 1]

    def train_from_curriculum(self, curriculum_path: Path) -> None:
        with open(curriculum_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        compiled_nodes = []
        for item in records:
            tokens = []
            for trig in item["triggers"]:
                tokens.extend(self._tokenize(trig))
            compiled_nodes.append({
                "domain": item["domain"],
                "token_weights": dict(Counter(tokens)),
                "plan": item["plan"],
                "response_template": item["response_template"]
            })

        brain_artifact = {
            "brain_version": "1.0.0-JarvisCore",
            "autonomous_goap_enabled": True,
            "nodes": compiled_nodes
        }
        self.brain_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.brain_path, "w", encoding="utf-8") as f:
            json.dump(brain_artifact, f, indent=2)
        self.memory_graph = compiled_nodes

    def load_brain(self) -> None:
        if not self.brain_path.exists():
            raise FileNotFoundError(f"Brain file missing: {self.brain_path}")
        with open(self.brain_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.memory_graph = data.get("nodes", [])

    def decide(self, user_command: str) -> dict:
        if not self.memory_graph:
            self.load_brain()

        query_tokens = self._tokenize(user_command)
        best_node = None
        best_score = -1.0

        for node in self.memory_graph:
            weights = node["token_weights"]
            score = sum(weights.get(t, 0) for t in query_tokens) / (math.sqrt(len(weights)) + 1.0)
            if score > best_score:
                best_score = score
                best_node = node

        if not best_node or best_score == 0:
            return {
                "domain": "self_coding",
                "confidence": 0.5,
                "plan": ["analyze_problem_spec", "synthesize_python_tool", "test_in_sandbox"],
                "voice_response": "Analyzing unfamiliar request, Sir. Engaging dynamic self-coding engine to solve it."
            }

        return {
            "domain": best_node["domain"],
            "confidence": round(min(0.99, 0.65 + best_score * 0.25), 2),
            "plan": best_node["plan"],
            "voice_response": best_node["response_template"]
        }
