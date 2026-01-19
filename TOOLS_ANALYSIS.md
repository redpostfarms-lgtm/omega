# Development Tools Analysis & Installation Guide

**Date**: 2026-01-18
**Source**: Microsoft Store / Windows Package Manager

---

## 📦 **Tools Identified for Installation**

### **1. Docker Desktop** ⭐ (Currently Downloading)
**Status**: ✅ Downloading (100% - 585.1 MB)

**What it is**:
- Container platform for running and managing Docker containers
- Includes Docker Engine, Docker CLI, Docker Compose
- Required for running the containerized Gatekeeper stack

**Why you need it**:
- Runs the complete 6-service Docker stack we configured
- Enables Redis, Prometheus, Grafana, PostgreSQL
- Production-ready deployment
- Fixes VSCode Container Tools errors

**After installation**:
```powershell
# Verify installation
docker --version
docker compose version

# Test Docker
docker run hello-world

# Start Gatekeeper stack
.\scripts\utilities\docker-helpers.ps1 dev
```

**Configuration needed**:
- Enable WSL 2 integration
- Start Docker Desktop from system tray
- Re-enable Docker settings in VSCode (see VSCODE_DOCKER_FIX.md)

---

### **2. Dockerun** 🐳
**Status**: Available (Free)

**What it is**:
- Docker container management UI
- Visual interface for managing Docker containers, images, and volumes
- Alternative/complement to Docker Desktop GUI

**Why you might want it**:
- Easier visual management of containers
- Quick overview of running services
- Monitor resource usage
- Manage networks and volumes

**Recommendation**:
- ⚠️ Wait until Docker Desktop is fully installed first
- Optional enhancement - not required
- Docker Desktop already includes a GUI

**Installation** (optional, later):
```powershell
# Via Microsoft Store or
winget install Dockerun
```

---

### **3. Container Desktop** 📦
**Status**: Available (Free)

**What it is**:
- Another container management desktop application
- Alternative UI for Docker/Podman containers
- Cross-platform container management

**Why you might want it**:
- Alternative to Docker Desktop GUI
- Manage multiple container runtimes
- Different UI preferences

**Recommendation**:
- ⚠️ Optional - Docker Desktop already provides this functionality
- Only install if you prefer its UI over Docker Desktop
- Not needed for basic usage

**Installation** (optional):
```powershell
winget install ContainerDesktop
```

---

### **4. OctoEverywhere Plugin Manager** 🚀
**Status**: Available (Free)

**What it is**:
- Plugin manager for 3D printing (OctoPrint/Klipper)
- Remote access and management for 3D printers
- Cloud-based printer monitoring

**Why you might want it**:
- Only if you have 3D printers running OctoPrint/Klipper
- Remote printer access and monitoring
- Plugin ecosystem management

**Recommendation**:
- ❌ Not relevant for The Gatekeeper project
- Only install if you have 3D printing needs
- Skip for now

**Relevance to project**: None (3D printing specific)

---

### **5. XPipe** 🔗
**Status**: Available (Free)

**What it is**:
- Connection manager for shells, databases, and remote systems
- SSH/terminal connection management
- Database connection management
- Remote system access

**Why you might want it**:
- Manage multiple SSH connections
- Database connections (PostgreSQL, Redis, etc.)
- Remote server management
- Organized connection profiles

**Recommendation**:
- ⚠️ Optional - useful for managing remote connections
- Good if you'll be connecting to remote servers/databases
- Can help manage Docker containers on remote hosts

**Installation** (optional):
```powershell
winget install XPipe
```

**Use case for Gatekeeper**:
- Connect to remote PostgreSQL databases
- Manage Redis connections
- SSH into production servers
- Monitor containerized services remotely

---

### **6. Ubuntu 24.04.1 LTS** 🐧
**Status**: Available (Free)

**What it is**:
- Ubuntu Linux distribution for WSL (Windows Subsystem for Linux)
- Full Ubuntu environment running on Windows
- Required for Docker Desktop WSL 2 backend

**Why you need it**:
- ✅ **HIGHLY RECOMMENDED** for Docker Desktop
- Docker Desktop runs best with WSL 2
- Provides Linux environment on Windows
- Run Linux tools and scripts natively

**Recommendation**:
- ✅ **INSTALL THIS** - Essential for optimal Docker performance
- Docker Desktop requires WSL 2
- Enables running Linux containers
- Better performance than Hyper-V

**Installation**:
```powershell
# Install WSL if not already installed
wsl --install

# Or install Ubuntu specifically
wsl --install -d Ubuntu-24.04
```

**After installation**:
```bash
# Access Ubuntu
wsl

# Update Ubuntu
sudo apt update && sudo apt upgrade -y

# Install useful tools
sudo apt install -y git curl wget build-essential
```

**Docker Desktop integration**:
- Enable "Use the WSL 2 based engine" in Docker Desktop settings
- Enable "Ubuntu-24.04" in Resources → WSL Integration

---

### **7. DevToys** 🛠️
**Status**: Available (Free)

**What it is**:
- Swiss Army knife for developers
- Collection of developer utilities in one app
- JSON formatter, encoder/decoder, regex tester, etc.

**Features**:
- JSON/YAML/XML formatter
- Base64 encoder/decoder
- Hash generator (MD5, SHA, etc.)
- UUID generator
- Regex tester
- Color picker
- Markdown preview
- And many more tools

**Why you might want it**:
- Quick access to common dev tools
- No need for online converters
- Offline utility collection
- Fast and convenient

**Recommendation**:
- ✅ **RECOMMENDED** - Very useful for daily development
- Lightweight and handy
- Great for debugging and data manipulation
- Free and open source

**Installation**:
```powershell
# Via Microsoft Store or
winget install DevToys
```

**Use cases for Gatekeeper**:
- Format JSON API responses
- Test regex patterns for data processing
- Generate UUIDs for database entries
- Hash sensitive data
- Debug JWT tokens
- Format configuration files

---

## 🎯 **Installation Priority & Recommendations**

### **MUST INSTALL** (Do Now):
1. ✅ **Docker Desktop** - Already downloading (585 MB)
2. ✅ **Ubuntu 24.04 LTS** - Essential for Docker WSL 2 backend

### **HIGHLY RECOMMENDED** (Install Soon):
3. ⭐ **DevToys** - Very useful developer utilities

### **OPTIONAL** (Consider Later):
4. ⚠️ **XPipe** - If you need connection management
5. ⚠️ **Dockerun** - If you want alternative Docker UI
6. ⚠️ **Container Desktop** - If you prefer different UI

### **SKIP** (Not Relevant):
7. ❌ **OctoEverywhere** - 3D printing only, not needed

---

## 📋 **Step-by-Step Installation Plan**

### **Phase 1: Docker Setup** (Now)
```powershell
# 1. Wait for Docker Desktop download to complete
# 2. Install Docker Desktop when download finishes
# 3. Restart computer
# 4. Install Ubuntu 24.04 LTS for WSL 2
wsl --install -d Ubuntu-24.04

# 5. Start Docker Desktop
# 6. Enable WSL 2 integration in Docker Desktop settings
```

### **Phase 2: Verify Docker** (After restart)
```powershell
# Check Docker version
docker --version
docker compose version

# Test Docker
docker run hello-world

# Check WSL
wsl -l -v
# Should show Ubuntu-24.04 with VERSION 2
```

### **Phase 3: Configure VSCode** (After Docker works)
```powershell
# Re-enable Docker in VSCode settings.json
# Uncomment these lines:
# "containers.containerClient": "com.microsoft.visualstudio.containers.docker"
# "containers.orchestratorClient": "com.microsoft.visualstudio.orchestrators.dockercompose"

# Change:
"docker.showExplorer": true
"docker.enableDockerComposeLanguageService": true

# Reload VSCode
# Ctrl+Shift+P → "Developer: Reload Window"
```

### **Phase 4: Start Gatekeeper Stack** (Once Docker is ready)
```powershell
# Build and start services
.\scripts\utilities\docker-helpers.ps1 dev

# Verify services
docker ps

# Access services
# - API: http://localhost:8000
# - Jupyter: http://localhost:8888 (token: gatekeeper)
# - Grafana: http://localhost:3000 (admin/gatekeeper)
# - Prometheus: http://localhost:9090
```

### **Phase 5: Optional Tools** (Anytime)
```powershell
# Install DevToys (recommended)
winget install DevToys

# Install XPipe (if needed)
winget install XPipe

# Install others only if you want them
```

---

## ⚙️ **Post-Installation Configuration**

### **Docker Desktop Settings**:
1. **General**:
   - ✅ Use the WSL 2 based engine
   - ✅ Start Docker Desktop when you sign in (optional)

2. **Resources → WSL Integration**:
   - ✅ Enable integration with default WSL distro
   - ✅ Enable "Ubuntu-24.04"

3. **Resources → Advanced**:
   - CPUs: 4-6 (recommended)
   - Memory: 4-8 GB (recommended)
   - Swap: 1-2 GB
   - Disk image size: 64 GB (minimum)

### **WSL Configuration**:
```bash
# In Ubuntu WSL terminal
wsl

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker CLI in WSL (optional, for convenience)
# Docker commands will work from WSL automatically

# Test Docker from WSL
docker ps
```

---

## 🔍 **Tool Comparison**

| Tool | Purpose | Size | Priority | Notes |
|------|---------|------|----------|-------|
| Docker Desktop | Container platform | 585 MB | **MUST** | Core requirement |
| Ubuntu 24.04 | WSL Linux | ~500 MB | **MUST** | Docker backend |
| DevToys | Dev utilities | ~50 MB | **HIGH** | Very useful |
| XPipe | Connection manager | ~100 MB | Medium | For remote access |
| Dockerun | Docker UI | ~50 MB | Low | Alternative UI |
| Container Desktop | Container UI | ~100 MB | Low | Alternative UI |
| OctoEverywhere | 3D printing | ~50 MB | **SKIP** | Not relevant |

---

## ✅ **Installation Checklist**

Track your installations:

- [ ] Docker Desktop installed (currently downloading)
- [ ] Computer restarted after Docker install
- [ ] Docker Desktop started and running
- [ ] Ubuntu 24.04 LTS installed via WSL
- [ ] WSL 2 enabled and configured
- [ ] Docker WSL integration enabled
- [ ] Docker tested (`docker run hello-world`)
- [ ] VSCode settings updated for Docker
- [ ] VSCode reloaded
- [ ] Gatekeeper stack tested (`docker-helpers.ps1 dev`)
- [ ] DevToys installed (optional but recommended)
- [ ] XPipe installed (if needed)

---

## 🚨 **Common Issues & Solutions**

### **"WSL 2 installation is incomplete"**
```powershell
# Install WSL 2 kernel update
# Download from: https://aka.ms/wsl2kernel

# Or update WSL
wsl --update
wsl --set-default-version 2
```

### **"Docker daemon is not running"**
- Start Docker Desktop from Start Menu
- Wait for icon in system tray to turn green
- Check Docker Desktop settings

### **"Hyper-V is not enabled"**
```powershell
# Enable Hyper-V (Windows Pro/Enterprise only)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Restart computer
```

### **"Cannot start containers"**
- Ensure virtualization is enabled in BIOS
- Check Windows version (Win 10 19041+ or Win 11)
- Try "Reset to factory defaults" in Docker Desktop

---

## 📚 **Resources**

- **Docker Desktop**: https://docs.docker.com/desktop/install/windows-install/
- **WSL 2**: https://docs.microsoft.com/en-us/windows/wsl/install
- **DevToys**: https://devtoys.app/
- **XPipe**: https://xpipe.io/

---

## 🎉 **Expected Outcome**

After completing all installations:

1. ✅ Docker Desktop running with WSL 2 backend
2. ✅ Ubuntu Linux available via WSL
3. ✅ Complete Gatekeeper stack running in containers
4. ✅ All services accessible (API, Jupyter, Grafana, Prometheus)
5. ✅ VSCode Container Tools working without errors
6. ✅ DevToys available for development utilities
7. ✅ Full development environment ready

---

**Total download size**: ~1.2 GB (Docker + Ubuntu + optional tools)
**Total installation time**: ~30-45 minutes (including restarts)
**Difficulty**: Easy (mostly automated)

---

**Next**: Wait for Docker Desktop download to complete, then follow Phase 1 installation steps!
