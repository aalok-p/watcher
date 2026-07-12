from typing import Optional
import subprocess
import platform
import time
from gpu_base import GPUmetrics


def _read_intel_gpu_top() -> Optional[GPUmetrics]:
    try:
        result = subprocess.run(
            ["intel_gpu_top", "-J", "-l", "1"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            return None
        import json
        data = json.loads(result.stdout)
        engines = data.get("engines", {})
        busy_sum = 0.0
        count = 0
        for _, v in engines.items():
            if isinstance(v, dict) and "busy" in v:
                busy_sum += float(v["busy"])
                count += 1
        util = round(busy_sum / count, 1) if count else 0.0
        return GPUmetrics(
            gpu_name="Intel GPU",
            gpu_util=util,
            mem_util=0.0,
            mem_used_mb=0,
            mem_total_mb=0,
            temperature=0.0,
            power_draw=0.0,
            power_limit=0.0,
            throttle_reason="none",
            timestamp=time.time(),
        )
    except Exception:
        return None


def _read_intel_windows() -> Optional[GPUmetrics]:
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
                if "intel" in candidate.lower():
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
        print(f"[Intel] WMI error: {exc}")
        return None


def read_intel() -> Optional[GPUmetrics]:
    result = _read_intel_gpu_top()
    if result is not None:
        return result
    if platform.system() == "Windows":
        return _read_intel_windows()
    return None
