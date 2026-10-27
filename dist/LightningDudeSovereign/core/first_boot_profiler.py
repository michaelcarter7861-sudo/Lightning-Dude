import os
import sys
import json
import time
import socket
import shutil
import platform
import subprocess
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

DNA_PATH = Path("system_dna.json")

class FirstBootProfiler:
    """Scans complete device hardware, OS, tools, and environment on PC & Android/Termux."""

    def __init__(self, output_path: Path = DNA_PATH):
        self.output_path = output_path

    def _read_proc_meminfo(self) -> tuple:
        total_gb, avail_gb = 4.0, 2.0
        try:
            if Path("/proc/meminfo").exists():
                info = {}
                with open("/proc/meminfo", "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val_kb = int(parts[1].strip().split()[0])
                            info[key] = val_kb
                total_kb = info.get("MemTotal", 4 * 1024 * 1024)
                avail_kb = info.get("MemAvailable", info.get("MemFree", 2 * 1024 * 1024))
                total_gb = round(total_kb / (1024 ** 2), 2)
                avail_gb = round(avail_kb / (1024 ** 2), 2)
        except Exception:
            pass
        return total_gb, avail_gb

    def scan_hardware(self) -> dict:
        if psutil is not None:
            try:
                mem = psutil.virtual_memory()
                total_ram = round(mem.total / (1024 ** 3), 2)
                avail_ram = round(mem.available / (1024 ** 3), 2)
                phys_cores = psutil.cpu_count(logical=False) or (os.cpu_count() or 1)
                log_cores = psutil.cpu_count(logical=True) or (os.cpu_count() or 1)
            except Exception:
                total_ram, avail_ram = self._read_proc_meminfo()
                phys_cores = os.cpu_count() or 1
                log_cores = os.cpu_count() or 1
        else:
            total_ram, avail_ram = self._read_proc_meminfo()
            phys_cores = os.cpu_count() or 1
            log_cores = os.cpu_count() or 1

        disk = shutil.disk_usage(str(Path.home() if Path.home().exists() else "/"))
        return {
            "architecture": platform.machine(),
            "processor": platform.processor() or platform.machine() or "ARM64/Generic-CPU",
            "cpu_physical_cores": phys_cores,
            "cpu_logical_threads": log_cores,
            "ram_total_gb": total_ram,
            "ram_available_gb": avail_ram,
            "disk_total_gb": round(disk.total / (1024 ** 3), 2),
            "disk_free_gb": round(disk.free / (1024 ** 3), 2),
        }

    def scan_os_and_env(self) -> dict:
        is_android = "ANDROID_ROOT" in os.environ or "com.termux" in os.environ.get("PREFIX", "")
        cli_tools = ["git", "python", "python3", "curl", "adb", "ffmpeg", "nmap", "powershell", "bash"]
        available_tools = {tool: bool(shutil.which(tool)) for tool in cli_tools}
        return {
            "os_system": "Android-Termux" if is_android else platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "hostname": socket.gethostname(),
            "python_version": sys.version.split()[0],
            "available_cli_tools": available_tools,
        }

    def scan_baseline_processes(self) -> list:
        if psutil is not None:
            try:
                return [p.info["name"] for p in psutil.process_iter(["name"]) if p.info.get("name")][:50]
            except Exception:
                pass
        try:
            out = subprocess.check_output(["ps", "-e", "-o", "comm="], text=True, stderr=subprocess.DEVNULL)
            return [line.strip() for line in out.splitlines() if line.strip()][:50]
        except Exception:
            return ["init", "bash", "python3"]

    def determine_execution_tier(self, hw: dict) -> str:
        ram = hw["ram_total_gb"]
        if ram >= 12:
            return "ULTRA_SENTINEL_MODE"
        elif ram >= 4:
            return "BALANCED_JARVIS_MODE"
        return "LIGHTWEIGHT_EDGE_MODE"

    def generate_dna(self, force: bool = False) -> dict:
        if self.output_path.exists() and not force:
            with open(self.output_path, "r", encoding="utf-8") as f:
                return json.load(f)

        hw = self.scan_hardware()
        env = self.scan_os_and_env()
        dna = {
            "agent_name": "Lightning Dude",
            "first_boot_timestamp": int(time.time()),
            "execution_tier": self.determine_execution_tier(hw),
            "hardware": hw,
            "environment": env,
            "baseline_processes": self.scan_baseline_processes(),
        }
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(dna, f, indent=2)
        return dna

if __name__ == "__main__":
    profiler = FirstBootProfiler()
    dna = profiler.generate_dna(force=True)
    print(f"[⚡] System DNA Profiled: {dna['environment']['os_system']} | RAM: {dna['hardware']['ram_total_gb']}GB | Tier: {dna['execution_tier']}")
