from typing import Optional
import subprocess
import platform
import time
from gpu_base import GPUmetrics


def read_rocm()-> Optional[GPUmetrics]:
    try:
        result = subprocess.run(
            ["rocm-smi", "--json"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return None
        import json
        data = json.loads(result.stdout)
        card_id = next(iter(data), None)
        if not card_id:
            return None
        card = data[card_id]
        return GPUmetrics(
            gpu_name=card.get("Card series", "AMD GPU"),
            gpu_util=float(card.get("GPU use (%)", 0)),
            mem_util=float(card.get("Memory use (%)", 0)),
            mem_used_mb=int(float(card.get("Used memory (MB)", 0))),
            mem_total_mb=int(float(card.get("Total memory (MB)", 0))),
            temperature=float(card.get("Temperature (Sensor edge) (C)", 0)),
            power_draw=float(card.get("Average GPU power (W)", 0)),
            power_limit=float(card.get("Critical temperature (C)", 80)),
            throttle_reason="none",
            timestamp=time.time(),
        )
    except Exception:
        return None


def amd_windows() -> Optional[GPUmetrics]:
    try:
        result = subprocess.run(
            ["wmic", "path", "Win32_VideoController", "get", "Name", "/format:value"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return None
        name = ""
        for line in result.stdout.splitlines():
            if line.startswith("Name="):
                candidate = line.split("=", 1)[1].strip()
                if any(kw in candidate.lower() for kw in ("amd", "radeon", "ryzen")):
                    name = candidate
                    break
        if not name:
            return None
        return GPUmetrics(
            gpu_name=name,
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
        print(f"[AMD] WMI error: {exc}")
        return None


def read_amd() -> Optional[GPUmetrics]:
    result = read_rocm()
    if result is not None:
        return result
    if platform.system() == "Windows":
        return amd_windows()
    return None
