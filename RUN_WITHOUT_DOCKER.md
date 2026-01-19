# Run The Gatekeeper Without Docker

**Quick start guide for running the system locally without Docker**

## ⚡ **30-Second Quick Start**

```powershell
# 1. Start Jupyter Lab
jupyter lab

# 2. Open the visualization notebook
# Navigate to: notebooks/system_visualizations.ipynb

# 3. Run all cells
# Press Shift+Enter through each cell
```

That's it! You're up and running!

---

## 🚀 **Full Local Setup (No Docker Required)**

### **Start Services Individually**

#### **1. Main Application (FastAPI)**
```powershell
# Terminal 1
python main.py

# Access at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### **2. Jupyter Lab**
```powershell
# Terminal 2
jupyter lab

# Access at: http://localhost:8888
# Open: notebooks/system_visualizations.ipynb
```

#### **3. Optional: Redis (if you have it installed)**
```powershell
# Terminal 3 (if Redis is installed)
redis-server

# Or use WSL
wsl redis-server
```

---

## 📊 **What Works Without Docker**

### ✅ **Fully Functional**
- Jupyter Lab with all visualizations
- Interactive widgets
- Data analytics dashboards
- Network graph visualizations
- Export to PNG/PDF/HTML
- Main FastAPI application
- Health check endpoints
- API documentation

### ⚠️ **Limited (needs Docker)**
- Prometheus metrics collection
- Grafana dashboards
- Redis caching (unless installed separately)
- Full containerized stack

---

## 🎯 **Recommended Workflow (No Docker)**

### **For Visualization & Analysis**
```powershell
# Start Jupyter
jupyter lab

# Work in notebooks:
# - notebooks/system_visualizations.ipynb
# - notebooks/analysis/ (your custom notebooks)
# - notebooks/experiments/ (prototypes)

# Export results to reports/
```

### **For API Development**
```powershell
# Start FastAPI server
python main.py

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status

# View docs
# Open: http://localhost:8000/docs
```

### **For Data Processing**
```powershell
# Create scripts in scripts/utilities/
python scripts/utilities/your_script.py

# Process data
# - Read from data/raw/
# - Process and save to data/processed/
# - Generate reports to reports/
```

---

## 🔧 **VSCode Container Tools - What To Do**

Since Docker isn't installed yet, here's how to handle the walkthrough:

### **1. Mark Steps as Done**
- Click "Mark Done" on each step
- The configuration files are ready
- They'll work when you install Docker later

### **2. Skip Azure Deployment**
- Requires Azure subscription
- Can set up later if needed
- Not required for local development

### **3. Use Git Integration Instead**
- VSCode GitLens is fully configured ✅
- Source control panel works perfectly ✅
- Commit, push, pull all work ✅

---

## 📦 **Alternative: Install Docker Later**

When you're ready to use containers:

1. **Install Docker Desktop**
   - Download: https://www.docker.com/products/docker-desktop
   - Install and restart
   - Start Docker Desktop

2. **Build and Run**
   ```powershell
   # Build image
   .\scripts\utilities\docker-helpers.ps1 build

   # Start services
   .\scripts\utilities\docker-helpers.ps1 dev
   ```

3. **Access Services**
   - API: http://localhost:8000
   - Jupyter: http://localhost:8888
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

---

## ✅ **Current Status Summary**

### **What You Have Now (Working)**
```
✅ Jupyter Lab with visualizations
✅ VSCode with GitLens configured
✅ Organized project structure
✅ Complete documentation
✅ Python development environment
✅ Main FastAPI application
✅ Helper scripts ready
```

### **What Needs Docker (For Later)**
```
⏳ Containerized deployment
⏳ Redis caching
⏳ Prometheus metrics
⏳ Grafana dashboards
⏳ Production stack
```

---

## 🎉 **You're All Set for Local Development!**

Start with:
```powershell
jupyter lab
```

Then open: `notebooks/system_visualizations.ipynb`

Install Docker later when you're ready for containers!
