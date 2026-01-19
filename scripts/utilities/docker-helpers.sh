#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Docker Helper Scripts for The Gatekeeper
# ═══════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ──────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# ──────────────────────────────────────────────────────────────
# Build Functions
# ──────────────────────────────────────────────────────────────

build_image() {
    print_info "Building Gatekeeper Docker image..."
    docker build -f Dockerfile.python -t gatekeeper:latest .
    print_success "Image built successfully"
}

build_all() {
    print_info "Building all services..."
    docker-compose build
    print_success "All services built"
}

# ──────────────────────────────────────────────────────────────
# Run Functions
# ──────────────────────────────────────────────────────────────

run_dev() {
    print_info "Starting development environment..."
    docker-compose --profile development up -d
    print_success "Development environment running"
    print_info "Jupyter Lab: http://localhost:8888 (token: gatekeeper)"
    print_info "API: http://localhost:8000"
    print_info "Grafana: http://localhost:3000 (admin/gatekeeper)"
}

run_prod() {
    print_info "Starting production environment..."
    docker-compose up -d gatekeeper redis prometheus grafana
    print_success "Production environment running"
    print_info "API: http://localhost:8000"
    print_info "Prometheus: http://localhost:9090"
    print_info "Grafana: http://localhost:3000"
}

run_all() {
    print_info "Starting all services..."
    docker-compose --profile development --profile database up -d
    print_success "All services running"
}

# ──────────────────────────────────────────────────────────────
# Stop Functions
# ──────────────────────────────────────────────────────────────

stop_all() {
    print_info "Stopping all services..."
    docker-compose down
    print_success "All services stopped"
}

stop_and_clean() {
    print_info "Stopping and cleaning all services..."
    docker-compose down -v
    print_success "All services stopped and volumes removed"
}

# ──────────────────────────────────────────────────────────────
# Utility Functions
# ──────────────────────────────────────────────────────────────

show_logs() {
    service=${1:-gatekeeper}
    docker-compose logs -f "$service"
}

show_status() {
    print_info "Container status:"
    docker-compose ps
    echo ""
    print_info "Resource usage:"
    docker stats --no-stream
}

exec_shell() {
    service=${1:-gatekeeper}
    print_info "Opening shell in $service..."
    docker-compose exec "$service" /bin/bash
}

rebuild() {
    print_info "Rebuilding and restarting services..."
    docker-compose down
    docker-compose build
    docker-compose up -d
    print_success "Services rebuilt and restarted"
}

prune_all() {
    print_info "Cleaning up Docker resources..."
    docker system prune -a -f --volumes
    print_success "Docker cleanup complete"
}

# ──────────────────────────────────────────────────────────────
# Main Menu
# ──────────────────────────────────────────────────────────────

show_help() {
    cat << EOF
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
  ./docker-helpers.sh dev          # Start dev environment
  ./docker-helpers.sh logs redis   # View Redis logs
  ./docker-helpers.sh shell        # Open shell in gatekeeper

EOF
}

# ──────────────────────────────────────────────────────────────
# Main Script
# ──────────────────────────────────────────────────────────────

case "${1:-help}" in
    build)
        build_image
        ;;
    build-all)
        build_all
        ;;
    dev)
        run_dev
        ;;
    prod)
        run_prod
        ;;
    up)
        run_all
        ;;
    down)
        stop_all
        ;;
    clean)
        stop_and_clean
        ;;
    logs)
        show_logs "$2"
        ;;
    status)
        show_status
        ;;
    shell)
        exec_shell "$2"
        ;;
    rebuild)
        rebuild
        ;;
    prune)
        prune_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
