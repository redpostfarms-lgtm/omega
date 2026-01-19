# 🚀 OMEGA SYSTEM - COMPLETE SETUP GUIDE

## What is Omega?

**Omega Autopilot** is your intelligent VS Code companion that:
- ✅ Auto-optimizes system resources (GPU 60% + CPU 40% priority)
- 🧠 Loads brain & memory core on startup
- ⚡ Provides predictive autocomplete like Cursor
- 📊 Monitors resources in real-time
- 🔄 Runs optimization every 20 minutes automatically

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install the VS Code Extension

#### Option A: From Extension Folder (Development Mode)
```bash
# Open the extension folder in VS Code
code "H:\The Gatekeeper\omega-vscode-extension"

# Press F5 to launch Extension Development Host
# The extension will activate automatically
```

#### Option B: Package and Install
```bash
cd "H:\The Gatekeeper\omega-vscode-extension"

# Install VSCE (if not installed)
npm install -g @vscode/vsce

# Package the extension
vsce package

# Install the .vsix file
code --install-extension omega-autopilot-1.0.0.vsix
```

### Step 2: Configure Extension

Open VS Code Settings (`Ctrl+,`) and search for "Omega":

```json
{
  "omega.autoStart": true,
  "omega.optimizationInterval": 20,
  "omega.pythonPath": "C:\\Users\\Drakalich\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
  "omega.optimizerScript": "H:\\The Gatekeeper\\omega_resource_optimizer.py"
}
```

### Step 3: Verify It's Working

1. **Check Status Bar**: Look for `$(pulse) Ω: XX% RAM | XX% CPU` in bottom-right
2. **Run Command**: Press `Ctrl+Shift+P` → Type "Omega: Show System Status"
3. **View Output**: Check `View > Output > Omega Autopilot` for logs

---

## 📋 Complete Feature List

### 🔧 Resource Optimization

| Feature | Description | Default |
|---------|-------------|---------|
| Auto-start | Runs on VS Code startup | Enabled |
| Optimization Interval | How often to optimize | 20 minutes |
| GPU Priority | GPU processing priority | 60% |
| CPU Priority | CPU processing priority | 40% |
| RAM Cache Limit | Maximum RAM cache | 512 MB |
| Memory Threshold | Cleanup trigger | 85% |

### 🧠 Brain & Memory Core
- Persistent configuration across sessions
- GPU/CPU priority enforcement
- Smart memory management
- Aggressive cleanup at 80%+ memory

### ⚡ Predictive Autocomplete
- **Context-Aware**: Analyzes current function/class scope
- **Language-Specific**: Python, JavaScript, TypeScript patterns
- **Smart Snippets**: Docstrings, error handling, loops
- **Confidence Scoring**: Best suggestions shown first

### 📊 Status Bar
- Real-time memory percentage
- Real-time CPU usage
- Color-coded alerts:
  - 🟢 Green: < 75% memory (Optimal)
  - 🟡 Yellow: 75-85% memory (Warning)
  - 🔴 Red: > 85% memory (Critical)

---

## 🎮 Commands Reference

Press `Ctrl+Shift+P` and type:

| Command | Shortcut | Description |
|---------|----------|-------------|
| `Omega: Run Resource Optimization` | - | Manual optimization |
| `Omega: Show System Status` | Click status bar | Detailed metrics |
| `Omega: Configure GPU/CPU Priority` | - | Adjust priorities |
| `Omega: Load Brain & Memory Core` | - | Reload configuration |

---

## 🔍 Autocomplete Examples

### Python Docstring
```python
def calculate_total(items):
    """  # ← Type "doc" here
    # Omega suggests full docstring template:
    Description
    
    Args:
        param: description
    
    Returns:
        return_type: description
    """
```

### JavaScript Async Error Handling
```javascript
async function fetchData() {
    try  // ← Omega suggests async try-catch
    try {
        // await operation
    } catch (error) {
        console.error('Error:', error);
    }
}
```

### Python Exception Handling
```python
try:
    risky_operation()
except  # ← Omega suggests "Exception as e"
except Exception as e:
    print(f"Error: {e}")
```

---

## 🛠️ Manual Resource Optimizer (Without Extension)

If you want to run optimization without the extension:

```powershell
# Run once manually
python "H:\The Gatekeeper\omega_resource_optimizer.py"

# Install scheduled task (requires admin)
Right-click: H:\The Gatekeeper\INSTALL_OPTIMIZER_TASK.bat
Select: "Run as administrator"
```

---

## 📊 What Gets Optimized?

1. **Memory Management**
   - Clears Python cache
   - Runs garbage collection
   - Closes memory-hogging processes (optional)

2. **CPU Allocation**
   - Reserves 2 cores for system
   - Uses 10 cores for applications
   - Sets process affinity automatically

3. **GPU Priority** (if available)
   - Prioritizes GPU processing
   - Reduces CPU fallback
   - Optimizes CUDA operations

---

## 🔧 Troubleshooting

### Extension Not Activating
```bash
# Check if compiled
cd "H:\The Gatekeeper\omega-vscode-extension"
npm run compile

# Check VS Code output
View > Output > Select "Omega Autopilot"
```

### Optimizer Script Fails
```bash
# Verify Python path
C:\Users\Drakalich\AppData\Local\Programs\Python\Python311\python.exe --version

# Test script manually
python "H:\The Gatekeeper\omega_resource_optimizer.py"
```

### Autocomplete Not Working
1. Check setting: `omega.enableAutocomplete: true`
2. Restart VS Code
3. Check that extension is activated (green in Extensions panel)

### Status Bar Not Showing
1. Enable: `omega.showStatusBar: true`
2. Check if other extensions are hiding it
3. Adjust status bar alignment in settings

---

## 📁 File Locations

| File | Location |
|------|----------|
| Extension | `H:\The Gatekeeper\omega-vscode-extension\` |
| Optimizer Script | `H:\The Gatekeeper\omega_resource_optimizer.py` |
| Logs | `H:\The Gatekeeper\system_monitor_reports\resource_optimizer_log.txt` |
| Config | `H:\The Gatekeeper\resource_config.json` |
| Rules Document | `H:\The Gatekeeper\OMEGA_ACTIVE_RULES.md` |

---

## 🎯 Expected Results

After installation:
- ✅ Memory stays below 85%
- ✅ CPU usage optimized (40% priority)
- ✅ GPU prioritized when available (60%)
- ✅ Autocomplete suggestions appear instantly
- ✅ Status bar shows real-time metrics
- ✅ System runs smoothly with 10 of 12 cores active

---

## 🚀 Next Steps

1. **Install Extension**: Press `F5` in extension folder or package it
2. **Configure Settings**: Set Python path and optimizer script path
3. **Verify Status Bar**: Should show Ω symbol with metrics
4. **Test Autocomplete**: Start typing code and see predictions
5. **Monitor Logs**: Check Output panel for optimization activity

---

## 💡 Tips

- **Performance**: Keep optimization interval at 20 minutes for balance
- **Battery**: Extension respects power settings, runs on battery too
- **Multi-Monitor**: Status bar appears on all VS Code windows
- **Customization**: All settings are adjustable via VS Code Settings

---

**Ω Omega Autopilot - Your Intelligent VS Code Companion**

Need help? Check [README.md](H:\The Gatekeeper\omega-vscode-extension\README.md) or run `Omega: Show System Status`
