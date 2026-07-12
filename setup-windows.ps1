param(
    [switch]$Start
)

$ErrorActionPreference = "Stop"
$gpuOverridePath = Join-Path (Get-Location) "docker-compose.gpu.override.yml"

if (Test-Path $gpuOverridePath) { Remove-Item -LiteralPath $gpuOverridePath -Force }

Write-Host "Watcher Windows setup" -ForegroundColor Cyan

function Require-Command {
    param([string]$Name, [string]$InstallHint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name not found. $InstallHint"
    }
}

#docker check

Require-Command -Name "docker" -InstallHint "Install Docker Desktop and enable WSL2 backend."

try {
    $dockerVersion = docker version --format "{{.Server.Version}}" 2>$null
    if (-not $dockerVersion) { throw "Docker daemon is not reachable." }
    Write-Host "  Docker daemon detected (Server: $dockerVersion)" -ForegroundColor Green
}
catch {
    throw "Docker is installed but not running. Start Docker Desktop, then retry."
}

#wsl check

try {
    $wslStatus = wsl -l -v 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  WSL is available." -ForegroundColor Green
    }
    else {
        Write-Warning "  WSL status check failed. Ensure WSL2 is enabled for Docker Desktop."
    }
}
catch {
    Write-Warning "  Could not verify WSL. Ensure WSL2 is enabled for Docker Desktop."
}

#wsl backend check

$dockerSettingsPath = "$env:USERPROFILE\.docker\settings.json"
if (Test-Path $dockerSettingsPath) {
    $dockerSettings = Get-Content $dockerSettingsPath | ConvertFrom-Json
    if ($dockerSettings.wslEngineEnabled -eq $true) {
        Write-Host "  Docker Desktop WSL2 backend is enabled." -ForegroundColor Green
    }
    elseif ($dockerSettings.wslEngineEnabled -eq $false) {
        Write-Warning "  Docker Desktop is using Hyper-V backend. Switch to WSL2 backend for better GPU support."
    }
}
else {
    Write-Warning "  Could not read Docker Desktop settings."
    Write-Warning "  Ensure Docker Desktop is configured with WSL2 backend."
}

#gpu detection

function Get-GPUProvider {
    $nvidiaSmi = Get-Command "nvidia-smi" -ErrorAction SilentlyContinue
    if ($nvidiaSmi) { return "nvidia" }

    $rocmsmi = Get-Command "rocm-smi" -ErrorAction SilentlyContinue
    if ($rocmsmi) { return "amd" }

    try {
        $adapters = Get-CimInstance -ClassName Win32_VideoController -ErrorAction Stop
        $names = ($adapters | ForEach-Object { $_.Name }) -join " "
        if ($names -match "(?i)amd|radeon|ryzen") { return "amd" }
        if ($names -match "(?i)intel") { return "intel" }
        if ($names -match "(?i)acer|predator|nitro") { return "acer" }
    }
    catch {}

    return "none"
}

$gpuProvider = Get-GPUProvider

switch ($gpuProvider) {
    "nvidia" {
        Write-Host "  GPU detected: NVIDIA" -ForegroundColor Green
        Write-Host "  Watcher will read live GPU metrics via nvidia-smi." -ForegroundColor Green
        $envProvider = "nvidia"
    }
    "amd" {
        Write-Host "  GPU detected: AMD" -ForegroundColor Green
        Write-Host "  Watcher will read GPU metrics via ROCm (rocm-smi)." -ForegroundColor Green
        $envProvider = "amd"
    }
    "intel" {
        Write-Host "  GPU detected: Intel" -ForegroundColor Green
        Write-Host "  Watcher will read GPU metrics via intel_gpu_top." -ForegroundColor Green
        $envProvider = "intel"
    }
    "acer" {
        Write-Host "  GPU detected: Acer" -ForegroundColor Yellow
        Write-Host "  Basic GPU identification only." -ForegroundColor Yellow
        $envProvider = "acer"
    }
    default {
        Write-Host "  No supported GPU detected." -ForegroundColor Yellow
        Write-Host "  Watcher will run in mock mode." -ForegroundColor Yellow
        Write-Host "  For NVIDIA: install NVIDIA Container Toolkit in WSL" -ForegroundColor Yellow
        Write-Host "  Run: wsl -d Ubuntu sudo bash setup-nvidia-gpu.sh" -ForegroundColor Yellow
        $envProvider = "mock"
    }
}

if ($gpuProvider -eq "nvidia") {
    @"
services:
  watcher:
    runtime: nvidia
    environment:
      NVIDIA_VISIBLE_DEVICES: all
"@ | Set-Content -Path $gpuOverridePath -Encoding UTF8
    Write-Host "  Generated GPU override for NVIDIA passthrough." -ForegroundColor Green
    $composeFiles = @("-f", "docker-compose.yml", "-f", "docker-compose.gpu.override.yml")
}
elseif ($gpuProvider -eq "amd") {
    @"
services:
  watcher:
    devices:
      - /dev/kfd
      - /dev/dri
"@ | Set-Content -Path $gpuOverridePath -Encoding UTF8
    Write-Host "  Generated GPU override for AMD passthrough." -ForegroundColor Green
    $composeFiles = @("-f", "docker-compose.yml", "-f", "docker-compose.gpu.override.yml")
}
elseif ($gpuProvider -eq "intel") {
    @"
services:
  watcher:
    devices:
      - /dev/dri
"@ | Set-Content -Path $gpuOverridePath -Encoding UTF8
    Write-Host "  Generated GPU override for Intel passthrough." -ForegroundColor Green
    $composeFiles = @("-f", "docker-compose.yml", "-f", "docker-compose.gpu.override.yml")
}
else {
    $composeFiles = @("-f", "docker-compose.yml")
}

$composeCmd = $null
$dockerV2 = docker compose version 2>$null
if ($dockerV2) {
    $composeCmd = "docker compose"
}
elseif (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    $composeCmd = "docker-compose"
}
if (-not $composeCmd) {
    throw "Neither 'docker compose' (V2) nor 'docker-compose' (V1) is available."
}

Write-Host "  Using: $composeCmd" -ForegroundColor Green


$env:GPU_PROVIDER = $envProvider
Write-Host "  GPU_PROVIDER=$envProvider" -ForegroundColor Cyan

if ($Start) {
    try {
        if ($composeCmd -eq "docker compose") {
            docker compose @composeFiles up --build
        }
        else {
            & $composeCmd @composeFiles up --build
        }
    }
    finally {
        if (Test-Path $gpuOverridePath) { Remove-Item -LiteralPath $gpuOverridePath -Force }
    }
}
else {
    Write-Host "Checks passed. Run:" -ForegroundColor Green
    Write-Host "  $composeCmd $($composeFiles -join ' ') up --build" -ForegroundColor Green
    if (Test-Path $gpuOverridePath) { Remove-Item -LiteralPath $gpuOverridePath -Force }
}
