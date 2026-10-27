import json
import time
import math
from pathlib import Path
from collections import Counter

class OmniVaultMemory:
    """
    Indexes local files, notes, and past conversations by semantic content
    so Lightning Dude can recall any file or fact in milliseconds even if the user forgets the filename.
    """

    TEXT_EXTENSIONS = {".txt", ".md", ".py", ".json", ".csv", ".log", ".sh", ".yml", ".yaml"}

    def __init__(self, vault_dir: str = "omni_vault"):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.vault_dir / "omni_semantic_index.json"
        if not self.index_file.exists():
            self._save_index({"documents": {}, "episodes": []})

    def _load_index(self) -> dict:
        return json.loads(self.index_file.read_text(encoding="utf-8"))

    def _save_index(self, data: dict) -> None:
        self.index_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def _tokenize(text: str) -> list:
        clean = "".join(c.lower() if c.isalnum() else " " for c in text)
        return [w for w in clean.split() if len(w) > 2]

    def index_directory(self, root_dir: Path) -> int:
        root_dir = Path(root_dir)
        data = self._load_index()
        docs = data.get("documents", {})
        indexed_count = 0

        for path in root_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in self.TEXT_EXTENSIONS:
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")[:20000]
                    tokens = self._tokenize(path.name + " " + content)
                    docs[str(path)] = {
                        "name": path.name,
                        "updated_at": int(time.time()),
                        "token_freq": dict(Counter(tokens).most_common(60)),
                        "preview": content[:180].strip().replace("\n", " ")
                    }
                    indexed_count += 1
                except Exception:
                    continue

        data["documents"] = docs
        self._save_index(data)
        return indexed_count

    def search_memory(self, query: str, top_k: int = 3) -> list:
        q_tokens = self._tokenize(query)
        data = self._load_index()
        docs = data.get("documents", {})
        scored = []

        for fpath, meta in docs.items():
            freqs = meta.get("token_freq", {})
            score = sum(freqs.get(t, 0) for t in q_tokens) / (math.sqrt(len(freqs)) + 1.0)
            if score > 0:
                scored.append({
                    "path": fpath,
                    "name": meta["name"],
                    "score": round(score, 3),
                    "preview": meta["preview"]
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def remember_episode(self, command: str, domain: str, outcome: str) -> None:
        data = self._load_index()
        episodes = data.get("episodes", [])
        episodes.append({
            "timestamp": int(time.time()),
            "command": command,
            "domain": domain,
            "outcome": outcome
        })
        data["episodes"] = episodes[-200:]
        self._save_index(data)
