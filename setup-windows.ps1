param(
    [switch]$Start
)

$ErrorActionPreference = "Stop"

Write-Host "Watcher Windows setup checks" -ForegroundColor Cyan

function Require-Command {
    param(
        [string]$Name,
        [string]$InstallHint
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name not found. $InstallHint"
    }
}

Require-Command -Name "docker" -InstallHint "Install Docker Desktop and enable WSL2 backend."

try {
    $dockerVersion = docker version --format '{{.Server.Version}}' 2>$null
    if (-not $dockerVersion) {
        throw "Docker daemon is not reachable."
    }
    Write-Host "Docker daemon detected (Server: $dockerVersion)" -ForegroundColor Green
}
catch {
    throw "Docker is installed but not running. Start Docker Desktop, then retry."
}

try {
    $wslStatus = wsl -l -v 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "WSL appears available." -ForegroundColor Green
    }
    else {
        Write-Warning "WSL status check failed. Ensure WSL2 is enabled for Docker Desktop."
    }
}
catch {
    Write-Warning "Could not verify WSL. Ensure WSL2 is enabled for Docker Desktop."
}

if ($Start) {
    Write-Host "Starting Watcher with Docker Compose..." -ForegroundColor Yellow
    docker compose up --build
}
else {
    Write-Host "Checks passed. Run: docker compose up --build" -ForegroundColor Green
}
