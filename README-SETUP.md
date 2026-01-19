# Gatekeeper Docker + WSL Setup

**Quick Start**: Double-click `START-HERE.bat` to begin!

---

## 🚀 **Automated Setup Scripts**

All 7 phases have automated batch scripts that you can run in order:

### **Phase 1: Enable WSL** (5 min + restart)
```
Right-click: PHASE-1-ENABLE-WSL.bat
Select: "Run as Administrator"
```
- Enables WSL feature
- Installs WSL 2 kernel
- Installs Ubuntu
- **Requires restart**

### **Phase 2: Setup Ubuntu** (3 min)
```
Double-click: PHASE-2-SETUP-UBUNTU.bat
```
- Launches Ubuntu
- Guides through user creation
- Updates packages
- Installs development tools

### **Phase 3: Start Docker** (2 min)
```
Double-click: PHASE-3-START-DOCKER.bat
```
- Starts Docker Desktop
- Waits for green icon
- Verifies Docker is running

### **Phase 4: Configure Docker** (2 min)
```
Open: PHASE-4-CONFIGURE-DOCKER.txt
Follow the manual steps
```
- Enable WSL 2 backend in Docker Desktop
- Enable WSL integration with Ubuntu
- **Manual GUI steps required**

### **Phase 5: Verify** (2 min)
```
Double-click: PHASE-5-VERIFY.bat
```
- Checks WSL installation
- Checks Docker version
- Tests Docker daemon
- Runs hello-world container

### **Phase 6: Build Gatekeeper** (10-15 min first time)
```
Double-click: PHASE-6-BUILD-GATEKEEPER.bat
```
- Pulls base images (~2GB)
- Builds Gatekeeper images
- Starts all 5 services
- Verifies containers are running

### **Phase 7: Verify Services** (1 min)
```
Double-click: PHASE-7-VERIFY-SERVICES.bat
```
- Tests all endpoints
- Opens services in browser
- Confirms everything works

---

## 📊 **Status Checker**

**Check current status anytime**:
```
Double-click: START-HERE.bat
```

This will show:
- ✓/✗ WSL installed
- ✓/✗ Docker running
- ✓/✗ Containers running
- What to do next

---

## 🎯 **Service URLs** (After Setup)

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Jupyter Lab**: http://localhost:8888 (token: `gatekeeper`)
- **Grafana**: http://localhost:3000 (admin/gatekeeper)
- **Prometheus**: http://localhost:9090

---

## 🔧 **Daily Usage**

### **Start Services**
```
Double-click: PHASE-6-BUILD-GATEKEEPER.bat
```
(Only takes 1-2 minutes after first build)

### **Stop Services**
```cmd
docker compose down
```

### **View Logs**
```cmd
docker compose logs -f
```

### **Check Status**
```cmd
docker ps
```

---

## 📚 **Documentation**

- **Quick Reference**: `START_NOW.txt`
- **Complete Guide**: `COMPLETE_STARTUP_GUIDE.md`
- **Docker Setup**: `DOCKER_SETUP_COMPLETE.md`
- **Troubleshooting**: `COMPLETE_STARTUP_GUIDE.md` (bottom section)

---

## 🚨 **Troubleshooting**

### **WSL won't install**
```cmd
# Run as Administrator:
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
shutdown /r /t 0
```

### **Docker won't start**
```cmd
wsl --update
wsl --set-default-version 2
# Then restart Docker Desktop
```

### **Containers fail to build**
```cmd
docker system prune -a -f
# Then run PHASE-6-BUILD-GATEKEEPER.bat again
```

### **Port already in use**
```cmd
netstat -ano | findstr :8000
# Stop the process using that port
# Or change ports in compose.yaml
```

---

## ⏱️ **Time Estimates**

| Phase | Time | Notes |
|-------|------|-------|
| Phase 1 | 5 min | + restart (2 min) |
| Phase 2 | 3 min | First time only |
| Phase 3 | 2 min | |
| Phase 4 | 2 min | Manual steps |
| Phase 5 | 2 min | |
| Phase 6 | 10-15 min | First time only! |
| Phase 7 | 1 min | |
| **Total** | **25-30 min** | First time setup |

**Future startups**: ~2 minutes (just start Docker + containers)

---

## ✅ **Success Checklist**

After completing all phases, you should have:

- [x] WSL 2 installed and running
- [x] Ubuntu 24.04 set up with user account
- [x] Docker Desktop running with WSL 2 backend
- [x] 5 containers running (gatekeeper, redis, prometheus, grafana, jupyter)
- [x] All services accessible via browser
- [x] VSCode Docker panel showing containers (no errors)

---

## 🎉 **You're All Set!**

Everything is automated with simple batch scripts.

**Just start with**: `START-HERE.bat`

It will tell you exactly what to do next!

---

## 📞 **Need Help?**

1. Run `START-HERE.bat` to see current status
2. Check `COMPLETE_STARTUP_GUIDE.md` for detailed help
3. Check troubleshooting section above
4. Review logs: `docker compose logs`

---

**Ready to begin? Double-click `START-HERE.bat` now!** 🚀
