# Omega Autopilot - VS Code Extension

**Auto-loads Omega resource optimizer with brain/memory core and intelligent predictive autocomplete**

## Features

### 🔧 Automatic Resource Optimization
- Auto-runs Omega resource optimizer when VS Code starts
- Enforces GPU (60%) + CPU (40%) priority processing
- Monitors and optimizes memory every 20 minutes (configurable)
- Real-time system metrics in status bar

### 🧠 Brain & Memory Core
- Loads configuration and strategies automatically
- Persistent memory across sessions
- GPU/CPU priority management
- RAM cache limiting (512 MB default)

### ⚡ Predictive Autocomplete
- Context-aware code completion similar to Cursor
- Analyzes surrounding code for intelligent suggestions
- Language-specific patterns (Python, JavaScript, TypeScript, etc.)
- Predictive algorithms based on:
  - Current line context
  - Function/class scope
  - Imports and dependencies
  - Previous code patterns
  - Confidence scoring

### 📊 Status Bar Integration
- Real-time memory and CPU usage
- Color-coded alerts (green/yellow/red)
- Click to view detailed system status
- Omega symbol (Ω) indicator

## Commands

| Command | Description |
|---------|-------------|
| `Omega: Run Resource Optimization` | Manually trigger optimization |
| `Omega: Show System Status` | Display detailed resource metrics |
| `Omega: Configure GPU/CPU Priority` | Adjust processing priorities |
| `Omega: Load Brain & Memory Core` | Reload brain configuration |

## Configuration

Access settings via `File > Preferences > Settings` and search for "Omega"

```json
{
  "omega.autoStart": true,
  "omega.optimizationInterval": 20,
  "omega.gpuPriority": 60,
  "omega.cpuPriority": 40,
  "omega.ramCacheLimit": 512,
  "omega.memoryThreshold": 85,
  "omega.enableAutocomplete": true,
  "omega.showStatusBar": true,
  "omega.pythonPath": "C:\\Users\\Drakalich\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
  "omega.optimizerScript": "H:\\The Gatekeeper\\omega_resource_optimizer.py"
}
```

## Installation

1. Open VS Code
2. Press `Ctrl+Shift+X` to open Extensions
3. Search for "Omega Autopilot"
4. Click Install

## Manual Installation (Development)

```bash
cd "H:\The Gatekeeper\omega-vscode-extension"
npm install
npm run compile
```

Then press `F5` in VS Code to launch Extension Development Host.

## Autocomplete Features

The Omega predictive autocomplete system provides:

### Context Analysis
- **Language Detection**: Automatically adapts to Python, JavaScript, TypeScript, etc.
- **Scope Awareness**: Understands function and class context
- **Import Analysis**: Suggests completions based on imported modules
- **Pattern Recognition**: Learns from surrounding code patterns

### Prediction Algorithms
1. **Context Scoring**: Analyzes relevance based on cursor position
2. **Confidence Ranking**: Sorts suggestions by prediction confidence
3. **Pattern Matching**: Identifies common code structures
4. **Smart Snippets**: Generates context-aware code templates

### Examples

**Python Function Docstring:**
```python
def calculate_total(items):
    # Type "doc" → suggests full docstring template with Args/Returns
```

**JavaScript Async Error Handling:**
```javascript
async function fetchData() {
    // Type "try" → suggests async try-catch pattern
}
```

**Python Exception Handling:**
```python
try:
    risky_operation()
except  # → suggests "Exception as e" with error handling
```

## How It Works

1. **Activation**: Extension activates when VS Code starts (`onStartupFinished`)
2. **Brain Load**: Loads configuration from settings
3. **Optimization**: Runs Python optimizer script every N minutes
4. **Status Updates**: Monitors system resources every 10 seconds
5. **Autocomplete**: Provides real-time code suggestions as you type

## Status Bar Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 Ω: 65% RAM \| 25% CPU | Optimal (< 75% memory) |
| 🟡 Ω: 78% RAM \| 45% CPU | Warning (75-85% memory) |
| 🔴 Ω: 90% RAM \| 70% CPU | Critical (> 85% memory) |

## Requirements

- VS Code 1.85.0 or higher
- Python 3.11+ with omega_resource_optimizer.py
- Node.js 18+ (for development)

## Troubleshooting

**Optimization not running:**
- Check Python path in settings
- Verify omega_resource_optimizer.py exists
- Check Output panel (View > Output > Omega Autopilot)

**Status bar not showing:**
- Enable in settings: `omega.showStatusBar: true`
- Check if extension is activated

**Autocomplete not working:**
- Enable in settings: `omega.enableAutocomplete: true`
- Restart VS Code

## License

MIT

## Author

The Gatekeeper

---

**Ω Omega Autopilot - Intelligent Resource Management & Predictive Code Completion**
