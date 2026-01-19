# ═══════════════════════════════════════════════════════════════
# Docker Helper Scripts for The Gatekeeper (PowerShell)
# ═══════════════════════════════════════════════════════════════

param(
    [Parameter(Position=0)]
    [string]$Command = "help",

    [Parameter(Position=1)]
    [string]$Service = "gatekeeper"
)

# ──────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────

function Print-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Print-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Yellow
}

# ──────────────────────────────────────────────────────────────
# Build Functions
# ──────────────────────────────────────────────────────────────

function Build-Image {
    Print-Info "Building Gatekeeper Docker image..."
    docker build -f Dockerfile.python -t gatekeeper:latest .
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Image built successfully"
    } else {
        Print-Error "Build failed"
        exit 1
    }
}

function Build-All {
    Print-Info "Building all services..."
    docker-compose build
    if ($LASTEXITCODE -eq 0) {
        Print-Success "All services built"
    } else {
        Print-Error "Build failed"
        exit 1
    }
}

# ──────────────────────────────────────────────────────────────
# Run Functions
# ──────────────────────────────────────────────────────────────

function Start-Dev {
    Print-Info "Starting development environment..."
    docker-compose --profile development up -d
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Development environment running"
        Print-Info "Jupyter Lab: http://localhost:8888 (token: gatekeeper)"
        Print-Info "API: http://localhost:8000"
        Print-Info "Grafana: http://localhost:3000 (admin/gatekeeper)"
    }
}

function Start-Prod {
    Print-Info "Starting production environment..."
    docker-compose up -d gatekeeper redis prometheus grafana
    if ($LASTEXITCODE -eq 0) {
        Print-Success "Production environment running"
        Print-Info "API: http://localhost:8000"
        Print-Info "Prometheus: http://localhost:9090"
        Print-Info "Grafana: http://localhost:3000"
    }
}

function Start-All {
    Print-Info "Starting all services..."
    docker-compose --profile development --profile database up -d
    if ($LASTEXITCODE -eq 0) {
        Print-Success "All services running"
    }
}

# ──────────────────────────────────────────────────────────────
# Stop Functions
# ──────────────────────────────────────────────────────────────

function Stop-All {
    Print-Info "Stopping all services..."
    docker-compose down
    Print-Success "All services stopped"
}

function Stop-AndClean {
    Print-Info "Stopping and cleaning all services..."
    docker-compose down -v
    Print-Success "All services stopped and volumes removed"
}

# ──────────────────────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────────────────────

function Show-Logs {
    param([string]$ServiceName = "gatekeeper")
    docker-compose logs -f $ServiceName
}

function Show-Status {
    Print-Info "Container status:"
    docker-compose ps
    Write-Host ""
    Print-Info "Resource usage:"
    docker stats --no-stream
}

function Enter-Shell {
    param([string]$ServiceName = "gatekeeper")
    Print-Info "Opening shell in $ServiceName..."
    docker-compose exec $ServiceName /bin/bash
}

function Rebuild-All {
    Print-Info "Rebuilding and restarting services..."
    docker-compose down
    docker-compose build
    docker-compose up -d
    Print-Success "Services rebuilt and restarted"
}

function Remove-All {
    Print-Info "Cleaning up Docker resources..."
    docker system prune -a -f --volumes
    Print-Success "Docker cleanup complete"
}

# ──────────────────────────────────────────────────────────────
# Help Function
# ──────────────────────────────────────────────────────────────

function Show-Help {
    Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║         The Gatekeeper - Docker Helper Commands              ║
╚═══════════════════════════════════════════════════════════════╝

Build Commands:
  build              Build the Gatekeeper image
  build-all          Build all services

Run Commands:
  dev                Start development environment (with Jupyter)
  prod               Start production environment
  up                 Start all services

Stop Commands:
  down               Stop all services
  clean              Stop services and remove volumes

Utility Commands:
  logs [service]     Show logs (default: gatekeeper)
  status             Show container status and resource usage
  shell [service]    Open shell in container (default: gatekeeper)
  rebuild            Rebuild and restart all services
  prune              Clean up Docker resources

Examples:
  .\docker-helpers.ps1 dev          # Start dev environment
  .\docker-helpers.ps1 logs redis   # View Redis logs
  .\docker-helpers.ps1 shell        # Open shell in gatekeeper

"@
}

# ──────────────────────────────────────────────────────────────
# Main Script
# ──────────────────────────────────────────────────────────────

switch ($Command.ToLower()) {
    "build" {
        Build-Image
    }
    "build-all" {
        Build-All
    }
    "dev" {
        Start-Dev
    }
    "prod" {
        Start-Prod
    }
    "up" {
        Start-All
    }
    "down" {
        Stop-All
    }
    "clean" {
        Stop-AndClean
    }
    "logs" {
        Show-Logs -ServiceName $Service
    }
    "status" {
        Show-Status
    }
    "shell" {
        Enter-Shell -ServiceName $Service
    }
    "rebuild" {
        Rebuild-All
    }
    "prune" {
        Remove-All
    }
    default {
        if ($Command -ne "help") {
            Print-Error "Unknown command: $Command"
            Write-Host ""
        }
        Show-Help
    }
}
