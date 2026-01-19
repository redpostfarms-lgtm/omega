# Docker Desktop - First Run Setup

**Status**: Docker Desktop installed ✅
**Next**: Start Docker Desktop and configure

---

## 🚀 **STEP 1: Start Docker Desktop**

### **Method 1: Start Menu**
1. Press Windows key
2. Type "Docker Desktop"
3. Click "Docker Desktop" to launch
4. Wait for Docker Engine to start (30-60 seconds)

### **Method 2: Desktop Icon**
- Double-click Docker Desktop icon on desktop (if available)

### **What to expect**:
- Docker Desktop window will open
- Icon will appear in system tray (bottom-right)
- Icon will be **orange/yellow** while starting
- Icon will turn **green** when ready ✅

---

## ⚙️ **STEP 2: Accept Service Agreement**

When Docker Desktop first starts:
1. You may see a "Service Agreement" popup
2. Read and click "Accept" to continue
3. May ask for admin permissions - click "Yes"

---

## 🔧 **STEP 3: Configure Docker Desktop** (Important!)

### **Enable WSL 2 Backend** (Recommended)

1. Click the ⚙️ **Settings** icon (gear icon in top-right)
2. Go to **General**
3. ✅ Check "**Use the WSL 2 based engine**"
4. Click "**Apply & Restart**"

### **WSL Integration** (If you have Ubuntu installed)

1. In Settings, go to **Resources** → **WSL Integration**
2. ✅ Enable "**Enable integration with my default WSL distro**"
3. ✅ Enable "**Ubuntu-24.04**" (or whichever Ubuntu version you have)
4. Click "**Apply & Restart**"

### **Resource Allocation** (Optional but recommended)

1. In Settings, go to **Resources** → **Advanced**
2. Set recommended values:
   - **CPUs**: 4-6 cores
   - **Memory**: 4-8 GB
   - **Swap**: 1-2 GB
   - **Disk image size**: 64 GB minimum
3. Click "**Apply & Restart**"

---

## ✅ **STEP 4: Verify Docker is Running**

### **Check System Tray**
- Look for Docker icon in system tray (bottom-right)
- Icon should be **green** ✅
- If orange/yellow, wait a bit longer
- If red, there's an issue (see troubleshooting below)

### **Test Docker Commands**

Open PowerShell and run:

```powershell
# Check Docker version
docker --version
# Should output: Docker version 27.x.x or similar

# Check Docker Compose
docker compose version
# Should output: Docker Compose version v2.x.x

# Test Docker is working
docker run hello-world
# Should download and run a test container
```

### **Expected Output**:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

---

## 🐳 **STEP 5: Start Gatekeeper Stack**

Once Docker is verified working:

```powershell
# Navigate to project directory
cd "C:\Users\Drakalich\.claude-worktrees\The Gatekeeper\pedantic-kowalevski"

# Build and start services
.\scripts\utilities\docker-helpers.ps1 dev

# Or manually with Docker Compose
docker-compose --profile development up -d
```

### **Wait for Services to Start** (30-60 seconds)

Check status:
```powershell
# View running containers
docker ps

# View logs
.\scripts\utilities\docker-helpers.ps1 logs
```

---

## 🌐 **STEP 6: Access Your Services**

Once containers are running, open your browser:

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Jupyter Lab** | http://localhost:8888 | Token: `gatekeeper` |
| **Grafana** | http://localhost:3000 | admin / gatekeeper |
| **Prometheus** | http://localhost:9090 | - |

### **Test API**:
```powershell
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

---

## 🔧 **STEP 7: Re-enable Docker in VSCode**

Now that Docker is running, update VSCode settings:

1. Open VSCode
2. Press `Ctrl+,` to open Settings
3. Click "Open Settings (JSON)" icon in top-right
4. Find these commented lines and **uncomment them**:

```json
// Change from:
// "containers.containerClient": "com.microsoft.visualstudio.containers.docker",
// "containers.orchestratorClient": "com.microsoft.visualstudio.orchestrators.dockercompose",

// To:
"containers.containerClient": "com.microsoft.visualstudio.containers.docker",
"containers.orchestratorClient": "com.microsoft.visualstudio.orchestrators.dockercompose",
```

5. Change these settings to `true`:
```json
"docker.showExplorer": true,
"docker.enableDockerComposeLanguageService": true,
```

6. Save the file
7. Reload VSCode: `Ctrl+Shift+P` → "Developer: Reload Window"

### **Verify VSCode**:
- Container panel should now show your running containers ✅
- No more "Failed to connect" errors ✅
- Can view logs, start/stop containers from VSCode ✅

---

## 🐛 **Troubleshooting**

### **Docker Desktop won't start**
```powershell
# Check if WSL is enabled
wsl --status

# Update WSL
wsl --update

# Set WSL 2 as default
wsl --set-default-version 2
```

### **"WSL 2 installation is incomplete"**
- Download WSL 2 kernel update: https://aka.ms/wsl2kernel
- Install and restart
- Restart Docker Desktop

### **"Hyper-V is not enabled"** (Windows Pro/Enterprise)
```powershell
# Run PowerShell as Administrator
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Restart computer
```

### **"Docker daemon is not running"**
1. Close Docker Desktop completely
2. Open Task Manager (Ctrl+Shift+Esc)
3. End any Docker processes
4. Restart Docker Desktop
5. Wait for green icon in system tray

### **Containers fail to start**
```powershell
# Check Docker is running
docker ps

# View container logs
docker-compose logs

# Rebuild containers
.\scripts\utilities\docker-helpers.ps1 rebuild
```

---

## 📋 **Quick Checklist**

- [ ] Docker Desktop installed ✅
- [ ] Docker Desktop started
- [ ] Service agreement accepted
- [ ] WSL 2 backend enabled (recommended)
- [ ] System tray icon is green
- [ ] `docker --version` works in PowerShell
- [ ] `docker run hello-world` succeeds
- [ ] Gatekeeper stack started (`docker-helpers.ps1 dev`)
- [ ] Services accessible in browser
- [ ] VSCode settings updated
- [ ] VSCode reloaded
- [ ] Container panel shows running containers

---

## 🎯 **Current Status**

✅ **Docker Desktop**: Installed
⏳ **Docker Engine**: Needs to be started
⏳ **Containers**: Not yet running

---

## 🚀 **Next Steps**

### **Right Now**:
1. **Start Docker Desktop** from Start Menu
2. Wait for **green icon** in system tray
3. Run `docker --version` in PowerShell to verify
4. Start Gatekeeper: `.\scripts\utilities\docker-helpers.ps1 dev`

### **Then**:
5. Open http://localhost:8888 (Jupyter)
6. Open http://localhost:3000 (Grafana)
7. Open http://localhost:8000/docs (API)

### **Finally**:
8. Update VSCode settings
9. Reload VSCode window
10. Enjoy your full containerized development environment! 🎉

---

**Start Docker Desktop now and follow the steps above!**
