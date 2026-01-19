# Complete Startup Guide - Docker + WSL + Gatekeeper

**Status**: Docker Desktop ✅ | Ubuntu WSL ✅ (downloaded, needs setup)

---

## 🚀 **STEP-BY-STEP STARTUP SEQUENCE**

### **PHASE 1: Enable WSL & Install Ubuntu** (5 minutes)

#### **Step 1.1: Enable WSL**

Open **PowerShell as Administrator**:
- Press **Windows + X**
- Select **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**

Run this command:
```powershell
wsl --install
```

**What this does**:
- Enables WSL feature on Windows
- Installs WSL 2 kernel
- Sets up Ubuntu as default distribution
- **Requires restart** when done

#### **Step 1.2: Restart Computer**

After the WSL installation completes:
```powershell
# Restart computer
shutdown /r /t 0
```

**⚠️ Save all work before restarting!**

---

### **PHASE 2: Setup Ubuntu** (After Restart - 3 minutes)

#### **Step 2.1: Launch Ubuntu**

After computer restarts:
- Press **Windows key**
- Type **"Ubuntu"**
- Click **"Ubuntu 24.04 LTS"** or just **"Ubuntu"**

#### **Step 2.2: Create Ubuntu User**

First time setup will ask for:
```
Enter new UNIX username: [your-username]
New password: [create a password]
Retype new password: [confirm password]
```

**Recommended**:
- Username: Same as your Windows username (lowercase)
- Password: Something you'll remember

#### **Step 2.3: Update Ubuntu**

Once Ubuntu terminal opens, run:
```bash
# Update package lists
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget build-essential
```

This takes 2-3 minutes.

---

### **PHASE 3: Start Docker Desktop** (2 minutes)

#### **Step 3.1: Launch Docker Desktop**

- Press **Windows key**
- Type **"Docker Desktop"**
- Click to launch

**Wait for**:
- Docker Desktop window to open
- Service agreement popup (click **Accept**)
- System tray icon to turn **GREEN** ✅

**First start may take 2-3 minutes!**

#### **Step 3.2: Configure Docker for WSL**

Once Docker Desktop is running:

1. Click **⚙️ Settings** (gear icon, top-right)
2. Go to **General**:
   - ✅ Check "**Use the WSL 2 based engine**"
   - Click **Apply & Restart**

3. Wait for Docker to restart (30 seconds)

4. Go back to **Settings** → **Resources** → **WSL Integration**:
   - ✅ Enable "**Enable integration with my default WSL distro**"
   - ✅ Enable "**Ubuntu-24.04**" (or your Ubuntu version)
   - Click **Apply & Restart**

5. Wait for Docker to restart again (30 seconds)

---

### **PHASE 4: Verify Everything Works** (2 minutes)

#### **Step 4.1: Check Docker in PowerShell**

Open **PowerShell** (doesn't need to be admin):
```powershell
# Check Docker version
docker --version
# Should show: Docker version 27.x.x or similar

# Check Docker Compose
docker compose version
# Should show: Docker Compose version v2.x.x

# Test Docker
docker run hello-world
# Should download and run test container
```

**Expected output**:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

#### **Step 4.2: Check Docker in WSL (Ubuntu)**

Open **Ubuntu** terminal:
```bash
# Check Docker in Ubuntu
docker --version

# Check WSL version
wsl.exe --list --verbose
# Should show Ubuntu with VERSION 2

# Test Docker from Ubuntu
docker ps
# Should show empty list (no error)
```

---

### **PHASE 5: Start Gatekeeper Stack** (3 minutes)

#### **Step 5.1: Navigate to Project**

In **PowerShell**:
```powershell
# Go to project directory
cd "C:\Users\Drakalich\.claude-worktrees\The Gatekeeper\pedantic-kowalevski"

# Verify you're in the right place
ls compose.yaml
# Should show the compose.yaml file
```

#### **Step 5.2: Build & Start Services**

**Option 1: Using Helper Script** (Recommended)
```powershell
.\scripts\utilities\docker-helpers.ps1 dev
```

**Option 2: Direct Docker Compose**
```powershell
docker-compose --profile development up -d
```

**What happens**:
- Downloads base images (first time only - ~2GB, takes 5-10 min)
- Builds Gatekeeper application image
- Starts 5 services:
  - gatekeeper (API)
  - redis
  - prometheus
  - grafana
  - jupyter

**Wait for**: "✓ Development environment running" message

#### **Step 5.3: Check Container Status**

```powershell
# View running containers
docker ps

# Check logs
.\scripts\utilities\docker-helpers.ps1 logs

# Or specific service
docker-compose logs gatekeeper
```

**All containers should show "Up" status**

---

### **PHASE 6: Access Your Services** (1 minute)

#### **Open in Browser**:

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Health Check** | http://localhost:8000/health | - |
| **Jupyter Lab** | http://localhost:8888 | Token: `gatekeeper` |
| **Grafana** | http://localhost:3000 | admin / gatekeeper |
| **Prometheus** | http://localhost:9090 | - |

#### **Test API**:
```powershell
# PowerShell
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"...","service":"gatekeeper","version":"1.0.0"}
```

#### **Open Jupyter**:
1. Go to http://localhost:8888
2. Enter token: `gatekeeper`
3. Navigate to `notebooks/`
4. Open `system_visualizations.ipynb`
5. Click **Run** → **Run All Cells**

---

### **PHASE 7: Update VSCode** (2 minutes)

#### **Step 7.1: Edit Settings**

In VSCode:
1. Press `Ctrl+,` to open Settings
2. Click **"Open Settings (JSON)"** icon (top-right)
3. Find these lines (around line 15-16):

**Change FROM:**
```json
// "containers.containerClient": "com.microsoft.visualstudio.containers.docker",
// "containers.orchestratorClient": "com.microsoft.visualstudio.orchestrators.dockercompose",
"docker.showExplorer": false,
"docker.enableDockerComposeLanguageService": false,
```

**Change TO:**
```json
"containers.containerClient": "com.microsoft.visualstudio.containers.docker",
"containers.orchestratorClient": "com.microsoft.visualstudio.orchestrators.dockercompose",
"docker.showExplorer": true,
"docker.enableDockerComposeLanguageService": true,
```

4. Save the file (`Ctrl+S`)

#### **Step 7.2: Reload VSCode**

1. Press `Ctrl+Shift+P`
2. Type "reload window"
3. Select **"Developer: Reload Window"**

#### **Step 7.3: Verify Container Panel**

After reload:
- Left sidebar should show **CONTAINERS** section
- Should list your running containers:
  - gatekeeper-app
  - gatekeeper-redis
  - gatekeeper-prometheus
  - gatekeeper-grafana
  - gatekeeper-jupyter
- **No errors!** ✅

---

## ✅ **SUCCESS CHECKLIST**

Mark each as you complete:

### **Phase 1: WSL Setup**
- [ ] WSL installed via `wsl --install`
- [ ] Computer restarted
- [ ] Ubuntu launched and user created
- [ ] Ubuntu updated (`apt update && apt upgrade`)

### **Phase 2: Docker Setup**
- [ ] Docker Desktop started
- [ ] Service agreement accepted
- [ ] WSL 2 backend enabled in settings
- [ ] WSL integration enabled for Ubuntu
- [ ] Green icon in system tray ✅

### **Phase 3: Verification**
- [ ] `docker --version` works in PowerShell
- [ ] `docker run hello-world` succeeds
- [ ] `docker --version` works in Ubuntu/WSL
- [ ] `wsl --list --verbose` shows Ubuntu VERSION 2

### **Phase 4: Gatekeeper**
- [ ] Docker images built
- [ ] All services started (5 containers)
- [ ] `docker ps` shows all containers running
- [ ] No errors in logs

### **Phase 5: Access**
- [ ] http://localhost:8000/health returns healthy
- [ ] http://localhost:8000/docs shows API documentation
- [ ] http://localhost:8888 opens Jupyter Lab
- [ ] http://localhost:3000 opens Grafana
- [ ] Jupyter notebook runs successfully

### **Phase 6: VSCode**
- [ ] Settings.json updated (Docker lines uncommented)
- [ ] VSCode reloaded
- [ ] Container panel shows running containers
- [ ] No "Failed to connect" errors

---

## 🐛 **Troubleshooting Common Issues**

### **WSL install fails**
```powershell
# Enable Windows features manually
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer
shutdown /r /t 0
```

### **Docker won't start**
```powershell
# Update WSL
wsl --update

# Set WSL 2 as default
wsl --set-default-version 2

# Restart Docker Desktop
```

### **Containers fail to build**
```powershell
# Clean Docker cache
docker system prune -a -f

# Rebuild without cache
docker-compose build --no-cache

# Try again
.\scripts\utilities\docker-helpers.ps1 dev
```

### **Port already in use**
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Stop other services or change ports in compose.yaml
```

### **"Cannot connect to Docker daemon"**
- Ensure Docker Desktop is running (green icon)
- Restart Docker Desktop
- Check Task Manager - Docker Desktop should be running

---

## ⏱️ **Time Estimates**

| Phase | Time | Notes |
|-------|------|-------|
| WSL Install | 5 min | Includes restart |
| Ubuntu Setup | 3 min | First-time only |
| Docker Config | 2 min | Settings & restart |
| Verify | 2 min | Quick tests |
| Build & Start | 10-15 min | First time (downloads images) |
| Access Services | 1 min | Open in browser |
| VSCode Update | 2 min | Edit & reload |
| **Total** | **25-30 min** | First time setup |

**Subsequent starts**: ~2 minutes (just start Docker + containers)

---

## 📚 **Quick Reference**

### **Start Everything** (Daily Use)
```powershell
# 1. Start Docker Desktop (if not auto-start)
# 2. Wait for green icon
# 3. Start containers
.\scripts\utilities\docker-helpers.ps1 dev

# Access services in browser
```

### **Stop Everything**
```powershell
.\scripts\utilities\docker-helpers.ps1 down
```

### **View Logs**
```powershell
.\scripts\utilities\docker-helpers.ps1 logs
```

### **Restart Services**
```powershell
.\scripts\utilities\docker-helpers.ps1 rebuild
```

---

## 🎯 **CURRENT STATUS**

✅ **Docker Desktop**: Installed (needs to be started)
✅ **Ubuntu WSL**: Downloaded (needs WSL to be enabled)
⏳ **WSL**: Not yet installed (needs `wsl --install`)
⏳ **Containers**: Not yet built
⏳ **Services**: Not yet running

---

## 🚀 **START HERE - DO THIS NOW**

### **Step 1: Open PowerShell as Administrator**
Right-click Start Menu → "Windows PowerShell (Admin)" or "Terminal (Admin)"

### **Step 2: Enable WSL**
```powershell
wsl --install
```

### **Step 3: Restart Computer**
```powershell
shutdown /r /t 0
```

### **Step 4: After Restart, Follow Phases 2-7 Above**

---

**Let's get started! Run `wsl --install` in PowerShell as Administrator now!** 🚀
