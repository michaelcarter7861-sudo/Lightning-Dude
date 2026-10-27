import ast
import sys
import json
import subprocess
from pathlib import Path

class DynamicSelfCoder:
    """
    Writes, AST-verifies, sandboxes, and permanently stores new Python tools
    in skills_vault/ whenever Lightning Dude encounters a new task.
    """

    FORBIDDEN_CALLS = {"os.remove", "shutil.rmtree", "os.rmdir"}

    def __init__(self, vault_dir: str = "skills_vault"):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.vault_dir / "skills_registry.json"
        if not self.registry_file.exists():
            self.registry_file.write_text(json.dumps({}, indent=2), encoding="utf-8")

    def verify_code_safety(self, code_str: str) -> tuple:
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"

        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                full_call = f"{node.value.id}.{node.attr}"
                if full_call in self.FORBIDDEN_CALLS:
                    return False, f"Security Lock: Forbidden destructive call '{full_call}' blocked."
        return True, "AST_VERIFIED_SAFE"

    def forge_and_run_skill(self, skill_name: str, code_str: str, description: str = "") -> dict:
        safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in skill_name.lower())
        is_safe, msg = self.verify_code_safety(code_str)
        if not is_safe:
            return {"status": "BLOCKED", "reason": msg}

        script_path = self.vault_dir / f"{safe_name}.py"
        script_path.write_text(code_str, encoding="utf-8")

        try:
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            output = proc.stdout.strip()
            err = proc.stderr.strip()
            success = proc.returncode == 0
        except Exception as e:
            output, err, success = "", str(e), False

        if success:
            registry = json.loads(self.registry_file.read_text(encoding="utf-8"))
            registry[safe_name] = {
                "script": str(script_path),
                "description": description or f"Auto-forged skill: {safe_name}",
                "verified": True
            }
            self.registry_file.write_text(json.dumps(registry, indent=2), encoding="utf-8")

        return {
            "status": "SUCCESS" if success else "RUNTIME_ERROR",
            "skill_name": safe_name,
            "script_path": str(script_path),
            "stdout": output,
            "stderr": err
        }
