#!/bin/bash

# NVIDIA Container Toolkit Setup Script for Watcher
# Installs GPU support for Docker on Linux

set -e

echo "NVIDIA Container Toolkit Setup for Watcher GPU Support"
echo "======================================================="
echo ""

if [ "$EUID" -ne 0 ]; then 
    echo "Error: This script must be run with sudo"
    echo "Run: sudo bash setup-nvidia-gpu.sh"
    exit 1
fi

echo "[1/6] Checking NVIDIA GPU driver..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "Error: nvidia-smi not found. NVIDIA GPU driver is not installed."
    echo "Please install NVIDIA GPU driver first."
    echo "See: https://www.nvidia.com/en-us/drivers/"
    exit 1
fi
echo "NVIDIA GPU driver found:"
nvidia-smi | head -3

echo ""
echo "[2/6] Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Error: Docker not found. Please install Docker first."
    exit 1
fi
echo "Docker is installed"

echo ""
echo "[3/6] Installing prerequisites..."
apt-get update
apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg2
echo "Prerequisites installed"

echo ""
echo "[4/6] Adding NVIDIA Container Toolkit repository..."
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
    gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

echo "Repository added"

echo ""
echo "[5/6] Installing NVIDIA Container Toolkit..."
apt-get update
apt-get install -y nvidia-container-toolkit
echo "NVIDIA Container Toolkit installed"

echo ""
echo "[6/6] Configuring Docker daemon for NVIDIA runtime..."
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker
echo "Docker daemon configured and restarted"

echo ""
echo "Verifying GPU access in Docker..."
if docker run --rm --runtime=nvidia nvidia/cuda:12.0-runtime nvidia-smi > /dev/null 2>&1; then
    echo "GPU access verified successfully"
else
    echo "GPU access verification failed"
    echo "Try restarting Docker: sudo systemctl restart docker"
    exit 1
fi

echo ""
echo "========================================================="
echo "NVIDIA Container Toolkit setup completed successfully"
echo "========================================================="
echo ""
echo "Next steps:"
echo "  1. Edit docker-compose.yml and uncomment: runtime: nvidia"
echo "  2. Run: sudo docker compose up --build"
echo "  3. Verify GPU in container: sudo docker compose exec watcher nvidia-smi"
echo ""

