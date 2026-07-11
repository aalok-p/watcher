import os
from gpu_base import GPUmetrics, parse_throttle, mock

provider = os.getenv("GPU_PROVIDER", "nvidia").strip().lower()

if provider == "nvidia":
    from gpu_nvidia import read_nvidia as _read
else:
    _read = mock


def read_gpu():
    result = _read()
    if result is None:
        return mock()
    return result


__all__ = ["read_gpu", "GPUmetrics", "mock"]
