# OMEGA Swarm

A distributed AI assistant where multiple phones work as one mind.

## Architecture

```
     ┌─────────────────┐
     │   QUEEN (0)     │  ← Primary phone, full UI
     │   Gold Crown    │
     └────────┬────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───────┐
│Drone 1│ │Drone 2│ │Drone 3│ │Drone 4│
│ Black │ │ Blue  │ │  Red  │ │ White │
└───────┘ └───────┘ └───────┘ └───────┘
    ↓         ↓         ↓         ↓
  Sip       Sip       Sip       Sip
 (dark)    (dark)    (dark)    (dark)
```

## Roles

| Node | Role | Color | Behavior |
|------|------|-------|----------|
| 0 | Queen | Gold | Full UI, voice, controls swarm |
| 1 | Drone | Black | Background worker |
| 2 | Drone | Blue | Background worker |
| 3 | Drone | Red | Background worker |
| 4 | Drone | White | Background worker |

## States

- **Connected** - Awake, ready to process
- **Sipping** - Screen off, donating 20% compute silently
- **Working** - Actively processing a query
- **Offline** - Not connected to swarm

## Quick Start

```bash
pip install flask --break-system-packages
python server.py
```

### Phone 0 (Queen)
Open `http://localhost:5000/queen.html`

### Phones 1-4 (Drones)
1. On Queen, tap "+ Drone"
2. Select drone number (1-4)
3. Scan QR with drone phone
4. Or open: `http://localhost:5000/drone.html?id=1`

## How It Works

### Communication
- **Same device tabs**: BroadcastChannel API
- **Cross device**: Requires WebSocket server (TODO)

### Sipping Mode
When a drone's screen turns off:
1. Enters "sipping" mode
2. Continues listening for tasks
3. Uses minimal resources (~20% compute cap)
4. No heat, no battery drain
5. Wakes briefly to process, then sleeps

### Query Distribution
1. User speaks/types on Queen
2. Queen broadcasts query to all drones
3. Drones process in parallel
4. Results aggregate back to Queen
5. Single response via Daniels' voice

## Gestures

| Action | Result |
|--------|--------|
| Tap drone grid | Show swarm status |
| Hold anywhere | Hush (silence all) |
| Tap Wake button | Exit sipping mode |

## Files

| File | Purpose |
|------|---------|
| `queen.html` | Queen controller UI |
| `drone.html` | Drone worker UI |
| `manifest.json` | Queen PWA config |
| `manifest-drone.json` | Drone PWA config |
| `sw.js` | Service worker |
| `server.py` | Dev server |

## Brain Tally

Shows total compute power:
- Queen base: 20%
- Each sipping drone: +20%
- 5 nodes max: 100%

## Limitations

- BroadcastChannel only works on same device/origin
- Cross-device requires WebSocket/WebRTC server
- True background compute needs native app wrapper
- PWAs can't run when browser is killed

## Future Enhancements

- [ ] WebSocket relay server for cross-device
- [ ] WebRTC peer-to-peer mesh
- [ ] Actual LLM inference distribution
- [ ] Native wrapper via Capacitor
- [ ] Biometric guest detection
