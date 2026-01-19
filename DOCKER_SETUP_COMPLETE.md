# Docker & Container Setup Complete

**Date:** 2026-01-18
**Status:** ✅ All container configurations completed

## 📦 **Files Created**

### Docker Configuration
- ✅ `Dockerfile.python` - Production-optimized Python container
- ✅ `compose.yaml` - Complete Docker Compose stack
- ✅ `config/prometheus.yml` - Prometheus monitoring configuration
- ✅ `azure-container-app.yaml` - Azure Container Apps deployment
- ✅ `.dockerignore` - Optimized build context

### Helper Scripts
- ✅ `scripts/utilities/docker-helpers.sh` - Bash helper commands
- ✅ `scripts/utilities/docker-helpers.ps1` - PowerShell helper commands

## 🐳 **Docker Compose Services**

Your stack includes:

### **Core Services**
1. **gatekeeper** - Main AI application
   - Ports: 8000 (API), 8080 (Web UI)
   - Multi-stage build for optimal size
   - Health checks enabled
   - Auto-restart configured

2. **redis** - Caching layer
   - Port: 6379
   - Persistent storage
   - Memory limit: 512MB
   - LRU eviction policy

3. **prometheus** - Metrics collection
   - Port: 9090
   - 15s scrape interval
   - Monitors all services

4. **grafana** - Visualization dashboards
   - Port: 3000
   - Default credentials: admin/gatekeeper
   - Pre-configured data sources

### **Development Services** (Optional)
5. **jupyter** - Jupyter Lab
   - Port: 8888
   - Token: gatekeeper
   - Access notebooks, data, reports
   - Enabled with `--profile development`

6. **postgres** - Database (Optional)
   - Port: 5432
   - Credentials: gatekeeper/gatekeeper_secure_password
   - Enabled with `--profile database`

## 🚀 **Quick Start**

### **Option 1: Using Helper Scripts (Recommended)**

#### Windows (PowerShell):
```powershell
# Start development environment
.\scripts\utilities\docker-helpers.ps1 dev

# Start production environment
.\scripts\utilities\docker-helpers.ps1 prod

# View logs
.\scripts\utilities\docker-helpers.ps1 logs gatekeeper

# Check status
.\scripts\utilities\docker-helpers.ps1 status

# Stop all services
.\scripts\utilities\docker-helpers.ps1 down
```

#### Linux/Mac/WSL (Bash):
```bash
# Make script executable
chmod +x scripts/utilities/docker-helpers.sh

# Start development environment
./scripts/utilities/docker-helpers.sh dev

# Start production environment
./scripts/utilities/docker-helpers.sh prod

# View logs
./scripts/utilities/docker-helpers.sh logs gatekeeper

# Check status
./scripts/utilities/docker-helpers.sh status
```

### **Option 2: Using Docker Compose Directly**

```bash
# Build images
docker-compose build

# Start production stack
docker-compose up -d

# Start with development tools (Jupyter)
docker-compose --profile development up -d

# Start with all services (including database)
docker-compose --profile development --profile database up -d

# View logs
docker-compose logs -f gatekeeper

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 📊 **Access Your Services**

Once running, access services at:

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **Web UI** | http://localhost:8080 | - |
| **Jupyter Lab** | http://localhost:8888 | Token: `gatekeeper` |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin / gatekeeper |
| **Redis** | localhost:6379 | - |
| **PostgreSQL** | localhost:5432 | gatekeeper / gatekeeper_secure_password |

## 🛠️ **Helper Commands Reference**

### Build Commands
```bash
build              # Build the Gatekeeper image
build-all          # Build all services
```

### Run Commands
```bash
dev                # Start development environment (with Jupyter)
prod               # Start production environment
up                 # Start all services
```

### Stop Commands
```bash
down               # Stop all services
clean              # Stop services and remove volumes
```

### Utility Commands
```bash
logs [service]     # Show logs (default: gatekeeper)
status             # Show container status and resource usage
shell [service]    # Open shell in container (default: gatekeeper)
rebuild            # Rebuild and restart all services
prune              # Clean up Docker resources
```

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                       │
│                  (gatekeeper-network)                   │
│                                                         │
│  ┌──────────┐    ┌───────┐    ┌────────────┐          │
│  │Gatekeeper├───►│ Redis │    │ PostgreSQL │          │
│  │   App    │    └───────┘    └────────────┘          │
│  └────┬─────┘                                          │
│       │                                                 │
│       ▼                                                 │
│  ┌──────────┐    ┌─────────┐                          │
│  │Prometheus├───►│ Grafana │                          │
│  └──────────┘    └─────────┘                          │
│                                                         │
│  ┌──────────┐                                          │
│  │ Jupyter  │  (Development only)                      │
│  └──────────┘                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔐 **Security Features**

- ✅ Non-root user in container (user: gatekeeper, uid: 1000)
- ✅ Multi-stage build (smaller attack surface)
- ✅ Health checks enabled
- ✅ Read-only config mounts
- ✅ Secrets management ready
- ✅ Network isolation

## 📈 **Monitoring & Metrics**

Prometheus automatically scrapes metrics from:
- Gatekeeper app at `/metrics` endpoint (every 10s)
- Redis instance
- Container metrics (if cAdvisor enabled)

View metrics in:
- **Prometheus UI**: http://localhost:9090
- **Grafana Dashboards**: http://localhost:3000

## 🌐 **Azure Deployment**

Deploy to Azure Container Apps:

```bash
# Login to Azure
az login

# Create resource group
az group create --name gatekeeper-rg --location eastus

# Create container app environment
az containerapp env create \
  --name gatekeeper-env \
  --resource-group gatekeeper-rg \
  --location eastus

# Deploy from configuration
az containerapp create \
  --name gatekeeper-app \
  --resource-group gatekeeper-rg \
  --environment gatekeeper-env \
  --yaml azure-container-app.yaml
```

## 🐛 **Troubleshooting**

### Container won't start
```bash
# Check logs
docker-compose logs gatekeeper

# Check container status
docker-compose ps

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use
```bash
# Find process using port 8000
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Stop other containers
docker-compose down
```

### Out of disk space
```bash
# Clean up Docker resources
docker system prune -a -f --volumes

# Or use helper script
.\docker-helpers.ps1 prune
```

## 📝 **Next Steps**

1. **Configure Environment Variables**
   - Create `.env` file for secrets
   - Update database passwords
   - Add API keys

2. **Set Up Grafana Dashboards**
   - Import pre-built dashboards
   - Configure alerts
   - Set up notification channels

3. **Enable CI/CD**
   - GitHub Actions for automated builds
   - Automated testing in containers
   - Deploy to Azure on merge

4. **Production Checklist**
   - [ ] Update default passwords
   - [ ] Configure TLS/SSL
   - [ ] Set up backup strategy
   - [ ] Configure logging aggregation
   - [ ] Set resource limits
   - [ ] Enable container scanning

## ✅ **Verification**

Test your setup:

```bash
# 1. Build and start services
docker-compose build
docker-compose up -d

# 2. Wait for services to be healthy (30-60 seconds)
docker-compose ps

# 3. Test API endpoint
curl http://localhost:8000/health

# 4. Open Grafana
# Visit http://localhost:3000
# Login: admin / gatekeeper

# 5. View metrics in Prometheus
# Visit http://localhost:9090
```

---

**Setup Complete!** 🎉

Your containerized environment is ready for development and production deployment.
