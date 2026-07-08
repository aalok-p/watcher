# Watcher 

> Real-time AI GPU health coach. Watches your GPU metrics, diagnoses bottlenecks, and explains fixes in plain English.


## Setup

### Linux

```bash
# Clone the repo 
git clone <repo-url>
cd watcher

# Install NVIDIA Container Toolkit (skip if already installed)
sudo bash setup-nvidia-gpu.sh

# Start with docker-compose
docker compose up --build
```

### Windows (WSL2)

```bash
# 1. Install Docker Desktop with WSL2 backend
# 2. In WSL2, install NVIDIA GPU driver for WSL:
#    https://developer.nvidia.com/cuda/wsl

# Clone the repo
git clone <repo-url>
cd watcher

# Run Windows setup checks
powershell.exe -File setup-windows.ps1

# Install NVIDIA Container Toolkit (skip if already installed)
sudo bash setup-nvidia-gpu.sh

# Start with docker-compose
docker compose up --build
```

Then open: **http://localhost:8000**

Watcher (Video Demo) - **https://youtu.be/G8i196ag9CY?si=JXK_Bs2pw1fh0TzJ**


things to add -
- [x] read nvidia-smi
- [x] rule based diagnosis
- [x] llm based diagnosis & reasoning
- [ ] add vsison sdk to monitor
- [ ] monitor via prometheus
- [ ] make cli version
