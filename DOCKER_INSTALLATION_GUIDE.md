# Docker Installation Guide

**Issue**: Docker is not currently installed on your system, which is why the VSCode Container Tools walkthrough is showing errors.

## 🐳 **Option 1: Install Docker Desktop (Recommended)**

### **Windows Installation**

1. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop
   - Click "Download for Windows"
   - Or direct link: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

2. **System Requirements**
   - Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
   - OR Windows 11 64-bit
   - WSL 2 feature enabled
   - Hyper-V and Containers Windows features enabled

3. **Installation Steps**
   ```powershell
   # Run the installer
   # Follow the installation wizard
   # Enable WSL 2 when prompted (recommended)
   # Restart your computer when complete
   ```

4. **After Installation**
   ```powershell
   # Verify installation
   docker --version
   docker compose version

   # Test Docker
   docker run hello-world
   ```

5. **Start Docker Desktop**
   - Open Docker Desktop from Start Menu
   - Wait for Docker Engine to start (icon in system tray will turn green)
   - Accept the service agreement if prompted

### **Enable WSL 2 (if not already enabled)**

```powershell
# Open PowerShell as Administrator

# Enable WSL
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer

# After restart, set WSL 2 as default
wsl --set-default-version 2

# Install Ubuntu (optional but recommended)
wsl --install -d Ubuntu
```

---

## 🔧 **Option 2: Use Podman (Docker Alternative)**

If you can't install Docker Desktop, you can use Podman:

### **Install Podman Desktop**

1. Download from: https://podman-desktop.io/downloads
2. Install and restart
3. Podman is Docker-compatible

### **Use Podman with Docker commands**
```powershell
# Podman is compatible with Docker commands
podman --version

# Use podman-compose instead of docker-compose
pip install podman-compose

# Run containers
podman-compose up -d
```

---

## 🚀 **Option 3: Run Without Docker (Local Development)**

You can run The Gatekeeper directly without containers:

### **Setup Virtual Environment**

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (Git Bash/WSL)
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### **Start Individual Services**

```powershell
# Terminal 1: Redis (if installed)
redis-server

# Terminal 2: Prometheus (if installed)
prometheus --config.file=config/prometheus.yml

# Terminal 3: Jupyter Lab
jupyter lab

# Terminal 4: Main Application
python main.py
```

### **Install Redis on Windows**

1. **Using WSL**
   ```bash
   wsl
   sudo apt update
   sudo apt install redis-server
   redis-server
   ```

2. **Using Chocolatey**
   ```powershell
   choco install redis-64
   redis-server
   ```

3. **Using Memurai (Redis alternative)**
   - Download: https://www.memurai.com/
   - Install and start service

---

## ✅ **After Docker is Installed**

Once Docker Desktop is running:

### **1. Verify Docker**
```powershell
docker --version
docker compose version
docker ps
```

### **2. Build The Gatekeeper Image**
```powershell
# Build the image
docker build -f Dockerfile.python -t gatekeeper:latest .

# Or use the helper script
.\scripts\utilities\docker-helpers.ps1 build
```

### **3. Start Services**
```powershell
# Start all services
.\scripts\utilities\docker-helpers.ps1 dev

# Or manually
docker-compose up -d
```

### **4. Verify Services Running**
```powershell
# Check running containers
docker ps

# Check logs
docker logs gatekeeper-app

# Test API
curl http://localhost:8000/health
```

---

## 🔍 **Troubleshooting**

### **"Docker daemon is not running"**
```powershell
# Start Docker Desktop
# Wait for icon in system tray to turn green
# Check Docker Desktop settings → Resources → WSL Integration
```

### **"WSL 2 installation is incomplete"**
```powershell
# Download and install WSL 2 kernel update
# https://aka.ms/wsl2kernel

# Or update WSL
wsl --update
```

### **"Hyper-V is not enabled"**
```powershell
# Enable Hyper-V (requires Windows Pro/Enterprise)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Restart computer
```

### **"Cannot start Docker Desktop"**
- Check Windows version (must be Win 10 19041+ or Win 11)
- Ensure virtualization is enabled in BIOS
- Check Windows Defender/Antivirus isn't blocking
- Try "Reset to factory defaults" in Docker Desktop settings

---

## 📋 **Quick Fix for VSCode Container Tools**

### **Temporary Workaround (Until Docker is Installed)**

1. **Mark walkthrough steps as done**
   - Click "Mark Done" on the problematic steps
   - Continue with other VSCode features

2. **Use Jupyter directly instead of containers**
   ```powershell
   jupyter lab
   # Open: notebooks/system_visualizations.ipynb
   ```

3. **Skip Azure deployment for now**
   - Azure Container Apps requires Azure subscription
   - Can deploy later once Docker is set up
   - Local development works without Azure

---

## 🎯 **Recommended Path Forward**

### **Immediate** (Today)
1. ✅ Use Jupyter Lab locally (no Docker needed)
   ```powershell
   jupyter lab
   ```

2. ✅ Mark VSCode walkthrough steps as done
   - You have all the config files ready
   - They'll work once Docker is installed

### **Next** (This Week)
1. Install Docker Desktop
2. Restart computer
3. Build containers
4. Test the full stack

### **Later** (Optional)
1. Set up Azure subscription
2. Deploy to Azure Container Apps
3. Set up CI/CD pipeline

---

## 📞 **Installation Help Resources**

- **Docker Desktop Docs**: https://docs.docker.com/desktop/install/windows-install/
- **WSL 2 Setup**: https://docs.microsoft.com/en-us/windows/wsl/install
- **Docker Forums**: https://forums.docker.com/
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/docker

---

## ✅ **Summary**

**Current Status**: Docker not installed, but everything else is ready

**Your Options**:
1. Install Docker Desktop (best option)
2. Use Podman instead
3. Run locally without containers (works now)

**What Works Now**:
- ✅ Jupyter Lab visualization notebook
- ✅ GitLens in VSCode
- ✅ All configuration files ready
- ✅ Local Python development

**What Needs Docker**:
- ⏳ Container deployment
- ⏳ Full stack with Redis/Prometheus/Grafana
- ⏳ Azure Container Apps deployment

---

**Recommendation**: Start with Jupyter Lab locally while you install Docker Desktop in the background!

```powershell
# Start now (no Docker needed)
jupyter lab
# Open: notebooks/system_visualizations.ipynb

# Install Docker Desktop later
# Download from: https://www.docker.com/products/docker-desktop
```
