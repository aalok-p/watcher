import os
from gpu_base import GPUmetrics, parse_throttle, mock

provider = os.getenv("GPU_PROVIDER", "nvidia").strip().lower()

if provider == "nvidia":
    from gpu_nvidia import read_nvidia as _read
elif provider == "amd":
    from gpu_amd import read_amd as _read
elif provider == "acer":
    from gpu_acer import read_acer as _read
else:
    _read = mock


def read_gpu():
    result = _read()
    if result is None:
        return mock()
    return result


__all__ = ["read_gpu", "GPUmetrics", "mock"]
