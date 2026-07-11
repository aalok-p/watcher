from typing import Optional
import platform
import time
from gpu_base import GPUmetrics

ACER_KEYWORDS = {"acer", "predator", "nitro"}


def acer_system() -> bool:
    try:
        import subprocess
        result = subprocess.run(
            ["wmic", "computersystem", "get", "Manufacturer,Model", "/format:value"],
            capture_output=True, text=True, timeout=5,
        )
        info = result.stdout.lower()
        return any(kw in info for kw in ACER_KEYWORDS)
    except Exception:
        return False


def read_acer() -> Optional[GPUmetrics]:
    if platform.system() != "Windows":
        return None
    if not acer_system():
        return None

    try:
        import subprocess
        result = subprocess.run(
            ["wmic", "path", "Win32_VideoController", "get", "Name", "/format:value"],
            capture_output=True, text=True, timeout=5,
        )
        name = ""
        for line in result.stdout.splitlines():
            if line.startswith("Name="):
                name = line.split("=", 1)[1].strip()
                break
        if not name:
            return None

        return GPUmetrics(
            gpu_name=f"Acer / {name}",
            gpu_util=0.0,
            mem_util=0.0,
            mem_used_mb=0,
            mem_total_mb=0,
            temperature=0.0,
            power_draw=0.0,
            power_limit=0.0,
            throttle_reason="none",
            timestamp=time.time(),
        )
    except Exception as exc:
        print(f"[Acer] Error: {exc}")
        return None
