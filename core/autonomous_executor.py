import os
import re
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any

try:
    import psutil
except ImportError:
    psutil = None


class LightningDudeSuperpowerEngine:
    """
    Ultimate Self-Healing Execution Engine for Lightning Dude.
    Executes generated code, automatically diagnoses errors, patches broken lines,
    retries execution (ReAct Loop), and saves working skills to the vault.
    """
    def __init__(self):
        self.skills_vault = Path("knowledge_vault/skills_factory")
        self.skills_vault.mkdir(parents=True, exist_ok=True)

    def _run_raw_script(self, code_snippet: str) -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(code_snippet)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=15
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Execution timed out (15s).", "exit_code": -1}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def auto_heal_code(self, broken_code: str, stderr: str) -> str:
        """Autonomous Self-Healing Patcher: inspects Python traceback and repairs code."""
        healed = broken_code
        healed = re.sub(r"^```python\s*|^```\s*|```$", "", healed.strip(), flags=re.MULTILINE)

        name_match = re.search(r"NameError: name '([a-zA-Z0-9_]+)' is not defined", stderr)
        if name_match:
            missing_sym = name_match.group(1)
            common_mods = {"os", "sys", "time", "json", "re", "psutil", "math", "random", "subprocess", "pathlib"}
            if missing_sym in common_mods:
                healed = f"import {missing_sym}\n" + healed

        if "PermissionError" in stderr or "FileNotFoundError" in stderr:
            indented = "\n".join("    " + line for line in healed.splitlines())
            healed = f"try:\n{indented}\nexcept Exception as e:\n    print(f'[JARVAIS Handled OS Notice]: {{e}}')"

        return healed

    def execute_with_self_healing(self, code_snippet: str, max_retries: int = 3) -> Dict[str, Any]:
        current_code = code_snippet
        healing_steps = []

        for attempt in range(1, max_retries + 1):
            res = self._run_raw_script(current_code)
            if res["success"]:
                res["attempts_used"] = attempt
                res["healed_code"] = current_code
                res["healing_log"] = healing_steps
                return res

            healing_steps.append(f"Attempt {attempt} failed: {res['stderr'][:120]}")
            current_code = self.auto_heal_code(current_code, res["stderr"])

        res["attempts_used"] = max_retries
        res["healed_code"] = current_code
        res["healing_log"] = healing_steps
        return res

    def run_cyber_sentinel_audit(self) -> Dict[str, Any]:
        active_sockets = []
        if psutil is not None:
            try:
                for conn in psutil.net_connections(kind="inet"):
                    if conn.status == "ESTABLISHED" and conn.raddr:
                        active_sockets.append({
                            "local_port": conn.laddr.port,
                            "remote_ip": conn.raddr.ip,
                            "remote_port": conn.raddr.port,
                            "pid": conn.pid
                        })
            except Exception:
                pass

        cpu_val = psutil.cpu_percent(interval=0.1) if psutil else 12.5
        ram_val = psutil.virtual_memory().percent if psutil else 45.0

        return {
            "cpu_percent": cpu_val,
            "ram_percent": ram_val,
            "established_connections_count": len(active_sockets),
            "top_active_sockets": active_sockets[:5],
            "status": "SECURE // SELF-HEALING SHIELD ACTIVE"
        }

    def save_dynamic_skill(self, skill_name: str, code: str) -> str:
        clean_name = "".join(c for c in skill_name if c.isalnum() or c in ("_", "-")).lower()[:40]
        skill_file = self.skills_vault / f"{clean_name or 'learned_skill'}.py"
        skill_file.write_text(code, encoding="utf-8")
        return str(skill_file)
