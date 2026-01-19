# 🐳 Container Quick Start Guide

**The fastest way to get The Gatekeeper running in containers**

## ⚡ **30-Second Quick Start**

### Windows (PowerShell)
```powershell
# Start everything
.\scripts\utilities\docker-helpers.ps1 dev
```

### Linux/Mac/WSL
```bash
# Make executable
chmod +x scripts/utilities/docker-helpers.sh

# Start everything
./scripts/utilities/docker-helpers.sh dev
```

That's it! Your services are now running:
- **API**: http://localhost:8000
- **Jupyter**: http://localhost:8888 (token: `gatekeeper`)
- **Grafana**: http://localhost:3000 (admin/gatekeeper)

## 📋 **What Gets Started**

| Service | Purpose | Port | Status |
|---------|---------|------|--------|
| 🤖 Gatekeeper | Main AI app | 8000, 8080 | ✅ Auto-starts |
| 🔴 Redis | Cache | 6379 | ✅ Auto-starts |
| 📊 Prometheus | Metrics | 9090 | ✅ Auto-starts |
| 📈 Grafana | Dashboards | 3000 | ✅ Auto-starts |
| 📓 Jupyter | Notebooks | 8888 | ✅ Dev only |

## 🎮 **Common Commands**

### Start Services
```bash
# Development (with Jupyter)
docker-helpers dev

# Production (no Jupyter)
docker-helpers prod

# Everything (including database)
docker-helpers up
```

### Monitor & Debug
```bash
# View all logs
docker-helpers logs

# View specific service logs
docker-helpers logs redis

# Check status
docker-helpers status

# Open shell in container
docker-helpers shell
```

### Stop & Clean
```bash
# Stop services
docker-helpers down

# Stop and delete data
docker-helpers clean

# Clean up Docker entirely
docker-helpers prune
```

## 🔧 **Troubleshooting**

### "Port already in use"
```bash
# Stop all services first
docker-helpers down

# Then start again
docker-helpers dev
```

### "Can't connect to service"
```bash
# Check status
docker-helpers status

# View logs for errors
docker-helpers logs gatekeeper

# Rebuild if needed
docker-helpers rebuild
```

### "Out of disk space"
```bash
# Clean up Docker
docker-helpers prune
```

## 📖 **Full Documentation**

- **Complete Setup Guide**: `DOCKER_SETUP_COMPLETE.md`
- **Helper Commands**: Run `docker-helpers help`
- **Docker Compose**: See `compose.yaml`

## 🚀 **Next Steps**

1. Open Jupyter Lab: http://localhost:8888
2. Open the visualization notebook
3. Check Grafana dashboards: http://localhost:3000
4. Test the API: `curl http://localhost:8000/health`

---

**Need help?** Check `DOCKER_SETUP_COMPLETE.md` for detailed instructions!
