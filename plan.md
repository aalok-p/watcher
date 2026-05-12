# GPU expansion 

## Current State
- Linux + NVIDIA: Full support via nvidia-smi
- Windows: Docker Desktop + WSL2 (no native GPU monitoring)
- Other GPUs: Not supported

---

## 1. Windows Native Support

### What to Change
- Add Windows detection in gpu_m.py
- Add nvidia-smi PATH for Windows: `C:\Program Files\NVIDIA Corporation\NVSMI`
- Update docker-compose.yml to pass NVIDIA_VISIBLE_DEVICES for Docker Desktop
- Verify/setup-windows.ps1 handles GPU access check

### Files Affected
- backend/gpu_m.py
- backend/main.py
- docker-compose.yml
- setup-windows.ps1

---

## 2. Intel GPU Support

### What to Change
- Detect Intel GPU via win32_VideoController
- Query Intel driver WMI for temperature/metrics (Windows)
- On Linux: use intel_gpu_top package
- Fallback to mock if unavailable

### Files Affected
- backend/gpu_m.py
- setup-intel-gpu.sh / setup-intel-gpu.ps1

---

## 3. Acer GPU Support

### What to Change
- Detect via win32_VideoController (standard NVIDIA/AMD on Acer laptops)
- Read NitroSense/PredatorSense registry for fan speed, power modes
- On Linux: not applicable (Acer uses Windows-only software)
- GPU temp/power already captured via nvidia-smi

### Files Affected
- backend/gpu_m.py
- setup-acer-gpu.ps1

---

## 4. Architecture

```
backend/
├── gpu_m.py           # Main entry point
├── gpu_nvidia.py      # NVIDIA-specific reader
├── gpu_intel.py       # Intel-specific reader
├── gpu_acer.py        # Acer-specific reader
└── gpu_factory.py     # Auto-detect GPU and return handler
```

- GPUmetrics dataclass stays unchanged across all GPU types
- Factory pattern for clean GPU handler selection
- monitor_loop in main.py iterates over available GPU sources

---

## 5. Testing Matrix

| Platform | GPU | Test |
|----------|-----|------|
| Linux | NVIDIA | python -c "from gpu_m import read_gpu; print(read_gpu())" |
| Windows | NVIDIA | python -c "from gpu_m import read_gpu; print(read_gpu())" |
| Windows | Intel | python -c "from gpu_m import read_gpu; print(read_gpu())" |
| Docker | NVIDIA | docker run --gpus all python -c "from gpu_m import read_gpu; print(read_gpu())" |

---

## 6. Priority

1. Windows + NVIDIA (minimal changes)
2. Windows + Intel
3. Acer GPU (NitroSense integration)
4. Intel GPU on Linux
