# KITT Agent & Omega Mesh Network - Complete Guide

## Architecture Overview

### KITT Agent
**Knight Industries Two Thousand Agent** - Your personal intermediary to Omega.

- **Role**: Go-between interface between user and Omega
- **Access Level**: Full Omega access rights
- **Function**: Protective shield working in tandem with Omega
- **Personality**: Helpful, protective, intelligent, slightly sarcastic, loyal (authentic KITT traits)

### Omega Mesh Network
**Distributed Computing Fleet** - Transform your phone fleet into a silent computing hive.

- **Queen Node**: Main device running at full throttle (100% CPU)
- **Worker Nodes**: 5 phones (labeled 1-5) contributing processing power
- **Worker Rules**:
  - Only active when screen is BLACK and device is IDLE
  - CPU capped at exactly 20% per worker (no more, no less)
  - Silent background processing only
  - No data snooping, no user feedback, just compute power

---

## System Components

### 1. KITT Agent (`kitt_agent.py`)

```python
from kitt_agent import kitt_agent

# Initialize KITT
kitt_agent.initialize()

# Process user command through KITT
response = await kitt_agent.process_user_command("Deploy security scan", user_context={})

# Check shield status
shield_status = kitt_agent.get_shield_status()

# Toggle shield
kitt_agent.toggle_shield(True)  # Activate shield
```

**KITT Features**:
- Command validation and sanitization
- Personality-driven responses
- Conversation history tracking
- Omega relay with full access
- User-friendly response interpretation

### 2. Omega Mesh Network (`omega_mesh_network.py`)

```python
from omega_mesh_network import mesh_network

# Initialize the mesh
mesh_network.initialize_mesh()

# Toggle individual workers
mesh_network.toggle_worker(1, enabled=True)   # Enable Worker-1
mesh_network.toggle_worker(2, enabled=False)  # Disable Worker-2

# Check worker idle state (automatic in production)
mesh_network.check_worker_idle_state(
    worker_id=1,
    screen_on=False,    # Screen must be off
    user_active=False   # No user activity
)

# Assign compute task to worker
task = {
    "id": "task_001",
    "type": "compute",
    "data": {"operation": "matrix_multiply", "size": 1000}
}
mesh_network.assign_task_to_worker(1, task)

# Get complete fleet status
fleet_status = mesh_network.get_fleet_status()
```

**Mesh Features**:
- Queen node coordinator (full throttle)
- 5 worker nodes with 20% CPU cap
- Screen-off idle detection
- Silent background processing
- Real-time fleet monitoring

---

## Web Interface Integration

### PWA Fleet Control Panel

The Omega PWA KITT Interface now includes a **Fleet Control Panel** on the right side:

**Features**:
- 🐝 **SEED MESH** - Initialize the fleet network
- 👑 **Queen Node** - Shows full throttle status (100% CPU)
- 🐝 **Worker Nodes 1-5** - Individual toggle controls for each worker
- **Fleet Power** - Total compute contribution from all nodes
- **Active Workers** - Count of currently active workers (e.g., "3/5")
- **Real-time Status** - Updates every 10 seconds automatically

**Status Colors**:
- 🟢 Green = ACTIVE (contributing compute power)
- 🟡 Yellow = IDLE (waiting for screen-off condition)
- ⚫ Gray = OFFLINE (not connected)
- 🔴 Red = DISABLED (manually turned off)

### API Endpoints

#### Get Fleet Status
```http
GET /api/mesh/status
```
Response:
```json
{
  "status": "success",
  "fleet": {
    "queen": { "id": 0, "name": "QUEEN", "cpu_contribution": 1.0 },
    "workers": {
      "1": { "name": "WORKER-1", "status": "active", "cpu_contribution": 0.20 },
      "2": { "name": "WORKER-2", "status": "idle", "cpu_contribution": 0.0 }
    },
    "mesh_active": true,
    "active_workers": 3,
    "total_workers": 5,
    "fleet_power": 1.6
  }
}
```

#### Toggle Worker
```http
POST /api/mesh/worker/{worker_id}/toggle
Content-Type: application/json

{ "enabled": true }
```

#### Initialize Mesh
```http
POST /api/mesh/initialize
```

#### Get KITT Status
```http
GET /api/kitt/status
```

---

## Usage Workflow

### Phase 1: Initialize KITT Agent
```bash
python kitt_agent.py
```
Output:
```
============================================================
    KITT AGENT - Knight Industries Two Thousand
============================================================

[KITT] Good day. KITT systems online.
[KITT] Establishing connection to Omega core...
[KITT] Shield protocols active. I am ready to assist.

KITT Agent Status:
  • Omega Access: GRANTED
  • Shield Status: ACTIVE
  • Protection: MAXIMUM

I am online and ready to serve as your interface to Omega.
```

### Phase 2: Deploy Fleet Mesh
```bash
python omega_mesh_network.py
```
Output:
```
======================================================================
         OMEGA MESH NETWORK - Distributed Fleet Controller
======================================================================

[MESH] Initializing Omega Fleet Mesh Network...
[MESH] Queen node: QUEEN - Full throttle active
[MESH] Worker nodes: 5 devices
[MESH] Configuration: 20% CPU cap when screen black & idle
[MESH] No snooping, no feedback - silent compute only

Fleet Configuration:
  🔴 QUEEN: Full throttle (100% CPU)
  🐝 WORKER-1: 20% CPU cap (idle only)
  🐝 WORKER-2: 20% CPU cap (idle only)
  🐝 WORKER-3: 20% CPU cap (idle only)
  🐝 WORKER-4: 20% CPU cap (idle only)
  🐝 WORKER-5: 20% CPU cap (idle only)

Mesh Status: ACTIVE
Silent Mode: ENABLED (no snooping, no talking back)
```

### Phase 3: Start Omega PWA
```bash
python omega_pwa_kitt_ui.py
```
Then open browser to: **<http://localhost:5001>**

### Phase 4: Seed the Mesh
1. Click **"⚡ SEED MESH"** button in the fleet panel
2. Workers will show "IDLE" status (waiting for conditions)
3. When phones go screen-off + idle → workers activate automatically
4. Watch CPU contribution rise to 20% per active worker

### Phase 5: Toggle Individual Workers
- Click **🟢 ON** / **🔴 OFF** buttons to enable/disable specific workers
- Useful for:
  - Temporarily disabling a worker (phone needs full battery)
  - Testing with specific worker combinations
  - Maintenance or troubleshooting

---

## Worker Activation Logic

A worker contributes compute power ONLY when:

1. ✅ **Enabled** via toggle (not manually disabled)
2. ✅ **Screen is BLACK** (display off, phone locked)
3. ✅ **Device is IDLE** (no user activity detected)
4. ✅ **CPU cap at 20%** enforced automatically

If ANY condition fails → Worker returns to IDLE state with 0% CPU contribution.

---

## Security & Privacy

### KITT Shield Protection
- All user commands validated by KITT before reaching Omega
- Dangerous patterns flagged for confirmation
- Conversation history logged for audit
- User preferences respected

### Mesh Network Privacy
- **No data snooping**: Workers only receive compute tasks, never user data
- **No feedback**: Workers operate silently without UI notifications
- **No communication**: Workers cannot talk to each other, only to Queen
- **Isolated processing**: Each task runs in sandboxed environment

---

## Performance Metrics

### Fleet Power Calculation
- Queen: 100% (always full throttle)
- Each active worker: +20%
- **Maximum fleet power**: 200% (Queen + 5 workers)

### Example Scenarios

| Active Workers | Queen CPU | Worker Total | Fleet Power |
|---------------|-----------|--------------|-------------|
| 0             | 100%      | 0%           | 100%        |
| 2             | 100%      | 40%          | 140%        |
| 5 (all)       | 100%      | 100%         | 200%        |

### CPU Distribution
```
Queen:     ████████████████████ 100%
Worker-1:  ████                  20%
Worker-2:  ████                  20%
Worker-3:  ████                  20%
Worker-4:  ████                  20%
Worker-5:  ████                  20%
```

---

## Troubleshooting

### KITT Agent Issues
**Problem**: KITT not responding
- Check Omega core connection
- Verify shield status with `kitt_agent.get_shield_status()`
- Restart KITT: `python kitt_agent.py`

**Problem**: Commands not validated
- Check `kitt_agent.omega_access` is `True`
- Ensure shield is active

### Mesh Network Issues
**Problem**: Workers not activating
- Verify screen is OFF and device is IDLE
- Check worker is ENABLED (not manually disabled)
- Review mesh status: `/api/mesh/status`

**Problem**: CPU not capped at 20%
- Check psutil library installed
- Verify worker idle detection logic
- Review worker contribution in fleet status

**Problem**: Fleet power showing incorrect
- Refresh status: `/api/mesh/status`
- Check for stale heartbeats
- Reinitialize mesh: `/api/mesh/initialize`

### PWA Interface Issues
**Problem**: Fleet panel not updating
- Check browser console (F12) for errors
- Verify API endpoints responding
- Check 10-second auto-refresh interval

**Problem**: Worker toggles not working
- Check POST request to `/api/mesh/worker/{id}/toggle`
- Verify worker ID is 1-5
- Check mesh network initialized

---

## Advanced Features

### Custom Task Distribution
```python
# Assign specific task types to specific workers
task_matrix_multiply = {
    "id": "task_001",
    "type": "matrix_multiply",
    "data": {"size": 1000, "iterations": 100}
}
mesh_network.assign_task_to_worker(1, task_matrix_multiply)

task_render = {
    "id": "task_002",
    "type": "render",
    "data": {"frames": [1, 2, 3, 4, 5]}
}
mesh_network.assign_task_to_worker(2, task_render)
```

### KITT Personality Customization
```python
kitt_agent.personality_traits = {
    "helpful": True,
    "protective": True,
    "intelligent": True,
    "slightly_sarcastic": True,  # Adjust as needed
    "loyal": True
}
```

### Fleet Monitoring Dashboard
```python
import asyncio

async def monitor_fleet_live():
    while True:
        status = mesh_network.get_fleet_status()
        print(f"Active Workers: {status['active_workers']}/{status['total_workers']}")
        print(f"Fleet Power: {status['fleet_power'] * 100:.0f}%")
        await asyncio.sleep(5)

asyncio.run(monitor_fleet_live())
```

---

## Next Steps

1. ✅ **Initialize KITT**: Run `python kitt_agent.py`
2. ✅ **Deploy Mesh**: Run `python omega_mesh_network.py`
3. ✅ **Start PWA**: Run `python omega_pwa_kitt_ui.py`
4. ✅ **Seed Fleet**: Click "⚡ SEED MESH" in web interface
5. ✅ **Enable Workers**: Toggle workers 1-5 as needed
6. ✅ **Monitor Fleet**: Watch real-time status updates

---

## System Requirements

- Python 3.11+
- Flask 3.1.2
- Flask-SocketIO
- psutil (for CPU monitoring)
- 5+ devices for full fleet (1 Queen + 5 workers)

---

**OMEGA MESH NETWORK IS NOW OPERATIONAL**

🔴 Queen stays rooted, full throttle.  
🐝 Workers lend cycles when idle.  
🛡️ KITT shields your commands.  
⚡ Silent crunching power for the hive.

---
