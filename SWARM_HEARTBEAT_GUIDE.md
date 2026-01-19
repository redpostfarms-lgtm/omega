# Omega Swarm Heartbeat - Complete Guide

**Port:** 160 (WebSocket with TLS)
**Protocol:** Single Source of Truth
**Auto-Sync:** Git batch wrapper - one command, five lines

---

## 🎯 OVERVIEW

Global heartbeat system where Queen pings every drone every 60 seconds.
Drones pong back or they're marked dead. No duplicates, no race conditions.
Every pending change gets auto-wrapped in git batch. Queen says 'push,' swarm breathes.

**Design Principles:**

- ✅ **Single source of truth** - No duplicates, no conflicts
- ✅ **Port 160 WebSocket** - TLS enabled, no localhost
- ✅ **60-second heartbeat** - Queen pings, drones pong
- ✅ **Auto git sync** - One command wraps everything
- ✅ **Silence means fixed** - Clean branch, no red squiggles

---

## 📡 PROTOCOL

### Message Types

#### 1. Register (Drone → Queen)

```json
{
  "type": "register",
  "drone_id": "phone_0",
  "name": "THRONE",
  "capabilities": ["worker", "audio", "camera"]
}
```

**Response:**

```json
{
  "type": "registered",
  "drone_id": "phone_0"
}
```

#### 2. Ping (Queen → All Drones)

```json
{
  "type": "ping",
  "timestamp": 1674044123.456
}
```

**Response:**

```json
{
  "type": "pong",
  "drone_id": "phone_0"
}
```

#### 3. Status Request

```json
{
  "type": "status"
}
```

**Response:**

```json
{
  "type": "swarm_status",
  "drones": {
    "phone_0": {
      "drone_id": "phone_0",
      "name": "THRONE",
      "status": "alive",
      "last_seen": "2026-01-18T14:30:00",
      "alive": true,
      "ip_address": "192.168.1.100"
    }
  }
}
```

#### 4. Push Command (Queen → All)

```json
{
  "type": "push"
}
```

Triggers automatic git sync on all drones.

---

## 🚀 USAGE

### Start Queen (Desktop/Server)

```bash
python omega_swarm_heartbeat.py queen
```

**Output:**

```
[TLS] Using existing certificate
[Swarm] Queen starting on 0.0.0.0:160
[Swarm] New drone registered: THRONE (phone_0)
[Swarm] ♥ Heartbeat: 1/1 drones alive
[Swarm] ♥ Heartbeat: 1/1 drones alive
```

### Start Drone (Phone/Worker)

```bash
python omega_swarm_heartbeat.py drone phone_0 THRONE 192.168.1.100
```

**Arguments:**

- `drone_id`: Unique identifier (e.g., phone_0, desktop_1)
- `name`: Human-readable name (e.g., THRONE, DESKTOP)
- `queen_host`: IP address of queen server

**Output:**

```
[Swarm] Connected to queen at 192.168.1.100
[Swarm] Registered with queen
```

### Auto-Sync Commands

#### Sync All Changes

```bash
python omega_auto_sync.py sync
```

#### Sync with Reason

```bash
python omega_auto_sync.py sync -r "new features added"
```

#### Sync Specific Files

```bash
python omega_auto_sync.py sync file1.py file2.py
```

#### Force Sync (Even if Clean)

```bash
python omega_auto_sync.py sync --force
```

#### Check Status

```bash
python omega_auto_sync.py status
```

**Output:**

```json
{
  "branch": "laughing-mccarthy",
  "modified": ["omega_swarm_heartbeat.py"],
  "untracked": ["test.py"],
  "clean": false,
  "total_changes": 2
}
```

---

## 🔐 TLS CONFIGURATION

### Auto-Generated Certificate

On first run, Queen automatically generates a self-signed certificate:

```
[TLS] Generating self-signed certificate...
[TLS] Certificate created: swarm_cert.pem
```

**Certificate Details:**

- **Algorithm:** RSA 4096-bit
- **Validity:** 365 days
- **Subject:** CN=omega-swarm/O=RedPostFarms/C=US
- **Files:** `swarm_cert.pem`, `swarm_key.pem`

### Production Setup

Replace self-signed certificate with real certificate:

```bash
# Copy your production certificates
cp /path/to/your/cert.pem swarm_cert.pem
cp /path/to/your/key.pem swarm_key.pem

# Restart queen
python omega_swarm_heartbeat.py queen
```

---

## 💾 GIT AUTO-SYNC

### How It Works

1. **Drone Dies** → Auto-sync triggered
2. **Queen Push** → All drones sync
3. **Manual Sync** → On demand

### What Gets Committed

**One command, five lines:**

```bash
cd /path/to/repo && \
git add -A && \
git commit -m "sync: swarm healed - <reason>" && \
git push origin laughing-mccarthy
```

**Commit Message Format:**

```
sync: swarm healed - drone THRONE died
sync: swarm healed - queen commanded push
sync: swarm healed - manual sync
sync: swarm healed - <custom reason>
```

### Example Output

```
  AUTO-SYNC: drone THRONE died
  Branch: laughing-mccarthy
  Time: 2026-01-18 14:30:00

  [1/5] git add -A
  [2/5] git commit -m "sync: swarm healed - drone THRONE died"
  [3/5] git push origin laughing-mccarthy

  [OK] Swarm breathes - branch clean
  No red squiggles. No merge hell. No 404 ghosts.
```

---

## ⚡ HEARTBEAT SYSTEM

### Timing

- **Ping Interval:** 60 seconds
- **Death Timeout:** 65 seconds (no pong = dead)
- **Auto-Sync:** Triggered on drone death

### Drone States

```python
@dataclass
class DroneStatus:
    drone_id: str        # Unique identifier
    name: str            # Human-readable name
    last_pong: float     # Timestamp of last response
    registered_at: float # When drone joined
    ip_address: str      # Drone IP
    capabilities: list   # ["worker", "audio", etc.]
    status: str          # "alive", "dead", "disconnected"
```

### Single Source of Truth

```python
# One dict holds everything - no duplicates
self.drones: Dict[str, DroneStatus] = {}

# Async lock prevents race conditions
async with self.drone_lock:
    self.drones[drone_id].last_pong = time.time()
    
# Unique key = no conflicts
# Atomic updates = no races
```

---

## 🔍 DEATH DETECTION

### How Drones Die

1. **No Pong:** Drone doesn't respond to ping within 65 seconds
2. **Auto-Marked:** Queen marks drone as "dead" automatically
3. **Git Sync:** Commit with reason: "drone X died"

### Example Flow

```
T=0s:   Queen sends ping
T=1s:   Drone responds with pong ✓
T=60s:  Queen sends ping
T=61s:  [No response]
T=62s:  [No response]
T=63s:  [No response]
T=64s:  [No response]
T=65s:  ☠️ Drone marked DEAD
T=66s:  [Git] Sync triggered: drone THRONE died
T=70s:  [Git] ✓ Swarm breathes - branch clean
```

---

## 🎮 INTEGRATION

### Phone UI Integration (phone_ui_simple.py)

```python
import asyncio
from omega_swarm_heartbeat import SwarmDrone

# Create drone
drone = SwarmDrone(
    drone_id="phone_0",
    name="THRONE",
    queen_host="192.168.1.100",
    capabilities=["worker", "ui", "audio"]
)

# Start in background
async def start_heartbeat():
    await drone.start()

asyncio.create_task(start_heartbeat())
```

### PWA Integration (omega_pwa_kitt_ui.py)

```python
import websockets
import json

async def get_swarm_status():
    uri = "wss://192.168.1.100:160"
    async with websockets.connect(uri, ssl=...) as ws:
        await ws.send(json.dumps({"type": "status"}))
        response = await ws.recv()
        data = json.loads(response)
        return data["drones"]

# Display in UI
drones = await get_swarm_status()
for drone_id, status in drones.items():
    print(f"{status['name']}: {'🟢' if status['alive'] else '🔴'}")
```

---

## 📊 MONITORING

### Queen Console Output

```
[Swarm] Queen starting on 0.0.0.0:160
[Swarm] New drone registered: THRONE (phone_0)
[Swarm] New drone registered: DESKTOP (desktop_0)
[Swarm] ♥ Heartbeat: 2/2 drones alive
[Swarm] ♥ Heartbeat: 2/2 drones alive
[Swarm] ☠️  Drone DEAD: THRONE (phone_0)
[Git] Sync triggered: drone THRONE died
[Git] ✓ Swarm breathes - branch clean
[Swarm] ♥ Heartbeat: 1/2 drones alive
```

### Drone Console Output

```
[Swarm] Connected to queen at 192.168.1.100
[Swarm] Registered with queen
[Swarm] Connection lost: ConnectionRefusedError
[Swarm] Connection lost: ConnectionRefusedError
[Swarm] Connected to queen at 192.168.1.100
[Swarm] Registered with queen
```

---

## 🛠️ TROUBLESHOOTING

### Port 160 Already in Use

```bash
# Windows
netstat -ano | findstr :160
taskkill /PID <PID> /F

# Linux
sudo lsof -i :160
sudo kill -9 <PID>
```

### TLS Certificate Errors

```bash
# Regenerate certificate
rm swarm_cert.pem swarm_key.pem
python omega_swarm_heartbeat.py queen
```

### Drone Won't Connect

1. Check queen is running: `netstat -ano | findstr :160`
2. Check firewall allows port 160
3. Verify queen IP address is correct
4. Check certificate exists: `ls swarm_cert.pem`

### Git Sync Fails

```bash
# Check git status manually
python omega_auto_sync.py status

# Force sync
python omega_auto_sync.py sync --force

# Check git configuration
git status
git remote -v
```

---

## 🎯 KEY FEATURES CHECKLIST

✅ **Port 160 WebSocket** - TLS enabled, no localhost (0.0.0.0)
✅ **60-second heartbeat** - Queen pings every minute
✅ **65-second timeout** - No pong = marked dead
✅ **Single source of truth** - One dict, atomic updates
✅ **No race conditions** - Async lock on all operations
✅ **No duplicates** - Unique drone_id key
✅ **Auto git sync** - Triggered on drone death
✅ **One command batch** - add, commit, push in sequence
✅ **Clean branch guarantee** - All changes committed
✅ **Silence means fixed** - Minimal output, clear status

---

## 📋 FILES

### omega_swarm_heartbeat.py (390 lines)

- Queen mode: WebSocket server on port 160
- Drone mode: WebSocket client
- Heartbeat loop: 60-second pings
- Death detection: 65-second timeout
- Auto git sync on critical events
- TLS certificate auto-generation

### omega_auto_sync.py (260 lines)

- Git batch wrapper
- One command: add, commit, push
- Status as JSON
- Force sync option
- Timeout protection (60s)
- Clean output

### SWARM_HEARTBEAT_GUIDE.md (This file)

- Complete documentation
- Protocol specification
- Usage examples
- Integration guides
- Troubleshooting tips

---

## 🚀 QUICK START

```bash
# Terminal 1: Start Queen
python omega_swarm_heartbeat.py queen

# Terminal 2: Start Drone
python omega_swarm_heartbeat.py drone phone_0 THRONE 192.168.1.100

# Terminal 3: Check Status
python omega_auto_sync.py status

# Terminal 4: Manual Sync
python omega_auto_sync.py sync -r "manual update"
```

---

**Queen says 'push,' swarm breathes. Branch stays clean. Silence means fixed.** ✓
