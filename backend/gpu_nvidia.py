from typing import Optional
import subprocess
import time
from gpu_base import GPUmetrics, parse_throttle

NVIDIA_SMI_QUERY = (
    "name,"
    "utilization.gpu,"
    "utilization.memory,"
    "memory.used,"
    "memory.total,"
    "temperature.gpu,"
    "power.draw,"
    "power.limit,"
    "clocks_throttle_reasons.active"
)

POWER_LIMIT_UNSET = {"n/a", "[n/a]", "n/a,"}
THROTTLE_UNSET = {"n/a", ""}
NVIDIA_SMI_TIMEOUT = 5
NVIDIA_SMI_ARGS = [ "nvidia-smi", f"--query-gpu={NVIDIA_SMI_QUERY}", "--format=csv,noheader,nounits"]


def safe_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return 0.0


def safe_int(value: str) -> int:
    try:
        return int(float(value))
    except ValueError:
        return 0


def power_limit(raw: str) -> float:
    if raw.lower() in POWER_LIMIT_UNSET:
        return 0.0
    return safe_float(raw)


def throttle_val(raw: str) -> str:
    if raw in THROTTLE_UNSET:
        return "none"
    return parse_throttle(raw)


def read_nvidia() -> Optional[GPUmetrics]:
    try:
        result = subprocess.run( NVIDIA_SMI_ARGS, capture_output=True, text=True, timeout=NVIDIA_SMI_TIMEOUT)
    except FileNotFoundError:
        print("[NVIDIA] nvidia-smi not found. Is the NVIDIA driver installed?")
        return None
    except subprocess.TimeoutExpired:
        print("[NVIDIA] nvidia-smi timed out.")
        return None
    except Exception as exc:
        print(f"[NVIDIA] Failed to run nvidia-smi: {exc}")
        return None

    if result.returncode != 0:
        print(f"[NVIDIA] nvidia-smi exited with code {result.returncode}: {result.stderr.strip()}")
        return None

    line = result.stdout.strip().split("\n")[0]
    parts = [p.strip() for p in line.split(",")]

    if len(parts) < 9:
        print(f"[NVIDIA] Unexpected nvidia-smi output: {line}")
        return None

    return GPUmetrics(
        gpu_name=parts[0],
        gpu_util=safe_float(parts[1]),
        mem_util=safe_float(parts[2]),
        mem_used_mb=safe_int(parts[3]),
        mem_total_mb=safe_int(parts[4]),
        temperature=safe_float(parts[5]),
        power_draw=safe_float(parts[6]),
        power_limit=power_limit(parts[7]),
        throttle_reason=throttle_val(parts[8]),
        timestamp=time.time()    
        )
