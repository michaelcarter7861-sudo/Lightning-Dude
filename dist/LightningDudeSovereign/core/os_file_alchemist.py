import os
import json
import shutil
import hashlib
from pathlib import Path

class OSFileAlchemist:
    """
    Handles real file organization, duplicate detection, system cache cleanup,
    and deploys Canary Honeypot files to catch ransomware/spyware red-handed.
    """

    CATEGORY_MAP = {
        "Documents": {".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv", ".md"},
        "Images": {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"},
        "Audio_Video": {".mp3", ".wav", ".mp4", ".mkv", ".mov"},
        "Archives": {".zip", ".tar", ".gz", ".rar", ".7z"},
        "Code_Scripts": {".py", ".sh", ".js", ".ts", ".json", ".yml", ".yaml", ".cs", ".cpp"}
    }

    def __init__(self, canary_dir: str = "canary_traps"):
        self.canary_dir = Path(canary_dir)
        self.canary_dir.mkdir(parents=True, exist_ok=True)
        self.canary_manifest = self.canary_dir / "canary_hashes.json"

    @staticmethod
    def file_sha256(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def organize_directory(self, target_dir: Path) -> dict:
        target_dir = Path(target_dir)
        if not target_dir.exists():
            return {"moved_files": 0, "duplicates_found": 0}

        seen_hashes = {}
        moved_count = 0
        duplicates = []

        for item in list(target_dir.iterdir()):
            if item.is_dir() or item.name.startswith("."):
                continue

            f_hash = self.file_sha256(item)
            if f_hash in seen_hashes:
                duplicates.append(item.name)
                continue
            seen_hashes[f_hash] = item.name

            ext = item.suffix.lower()
            dest_folder = "Others"
            for cat, exts in self.CATEGORY_MAP.items():
                if ext in exts:
                    dest_folder = cat
                    break

            cat_path = target_dir / dest_folder
            cat_path.mkdir(exist_ok=True)
            shutil.move(str(item), str(cat_path / item.name))
            moved_count += 1

        return {
            "moved_files": moved_count,
            "duplicates_found": len(duplicates),
            "duplicate_Popup_list": duplicates
        }

    def deploy_canary_honeypots(self) -> dict:
        traps = {
            "wallet_seed_backup.vault": "CANARY_TRAP_TOKEN_DO_NOT_TOUCH_998811",
            "master_passwords_export.kdbx": "CANARY_TRAP_CREDENTIALS_HONEYPOT_774422"
        }
        hashes = {}
        for fname, content in traps.items():
            fpath = self.canary_dir / fname
            fpath.write_text(content, encoding="utf-8")
            hashes[fname] = self.file_sha256(fpath)

        self.canary_manifest.write_text(json.dumps(hashes, indent=2), encoding="utf-8")
        return {"canary_traps_active": len(hashes), "location": str(self.canary_dir)}

    def verify_canary_integrity(self) -> dict:
        if not self.canary_manifest.exists():
            self.deploy_canary_honeypots()

        baseline = json.loads(self.canary_manifest.read_text(encoding="utf-8"))
        tampered = []
        for fname, expected_hash in baseline.items():
            fpath = self.canary_dir / fname
            if not fpath.exists() or self.file_sha256(fpath) != expected_hash:
                tampered.append(fname)

        return {
            "compromised": len(tampered) > 0,
            "tampered_files": tampered
        }
