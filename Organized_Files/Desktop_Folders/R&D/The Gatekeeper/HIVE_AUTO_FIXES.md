# Hive Auto - Problem Analysis & Fixes

## Problems Identified in Original `hive_hib.py`

### 1. **Memory Explosion**
**Problem:** Agents tried to copy the entire growing memory every spawn, causing exponential memory growth.

**Fix:** 
- Simplified memory structure: `{'solved': [], 'population': 0}`
- Only keep last 1000 solutions (auto-pruned)
- Memory context limited to last 3 solutions for prompts
- No deep copying of memory structures

### 2. **No Hard Cap on Total Agents → Runaway RAM**
**Problem:** Agents could multiply indefinitely (1 → 2 → 4 → 8 → 16 → 32 → 64 → 128 → ...) until system crashes.

**Fix:**
- Hard safety limit: Max 12 generations = 4096 agents (2^12)
- Hardware-aware scaling: Checks RAM/GPU/CPU before growing
- Auto-shrinks when hardware limits reached
- Falls back to conservative limits if hardware monitoring unavailable

### 3. **Tool-Call String Parsing Was Fragile**
**Problem:** Vote parsing relied on exact string matches, failed on variations.

**Fix:**
- Robust vote parsing: Checks for "VOTE:" in uppercase/lowercase
- Handles variations: "VOTE: YES", "vote: yes", "VOTE:YES"
- Fallback to 'ABSTAIN' if vote unclear
- Better error handling for malformed responses

## New Features in `hive_auto.py`

### 1. **Hardware-Aware Scaling**
```python
def can_grow():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    gpu_load = GPUtil.getGPUs()[0].load * 100 if GPUtil else 0
    
    return ram < 75 and gpu_load < 60 and cpu < 80
```

**Behavior:**
- Starts at 1 agent
- Doubles when hardware OK (RAM < 75%, GPU < 60%, CPU < 80%)
- Shrinks when hardware tight (divides by 2)
- Never crashes from resource exhaustion

### 2. **Self-Limiting Growth**
- Max 4096 agents (hard safety limit)
- Auto-stabilizes at 2048 if max reached
- Never goes below 1 agent

### 3. **Persistent Memory**
- Solutions saved to `memory.json`
- Last 1000 solutions kept (auto-pruned)
- Problem matching: Checks if problem already solved
- Instant retrieval from memory

### 4. **Better Error Handling**
- Graceful fallback if Ollama unavailable
- Handles missing psutil/GPUtil gracefully
- No crashes on subprocess errors
- UTF-8 encoding for Windows console

## Comparison

### `hive_hib.py` (Original)
- ❌ Memory explosion (copied entire memory each spawn)
- ❌ No hard cap (could spawn unlimited agents)
- ❌ Fragile vote parsing
- ❌ No hardware awareness
- ❌ Could crash system

### `hive_auto.py` (Fixed)
- ✅ Compact memory (last 1000 solutions only)
- ✅ Hard cap: 4096 agents max
- ✅ Robust vote parsing
- ✅ Hardware-aware scaling
- ✅ Self-limiting, never crashes

## Usage

### Basic
```bash
python "The Gatekeeper\hive_auto.py" "optimize 18650 charging curve"
```

### With Voice
```
"Hey, Gatekeeper, hive solve [problem]"
```

## Hardware Requirements

### Optional (for hardware-aware scaling):
```bash
pip install psutil GPUtil
```

**Without these:**
- Uses conservative limits (max 64 agents)
- Still works, just less intelligent scaling

**With these:**
- Monitors RAM/GPU/CPU in real-time
- Scales dynamically based on available resources
- Auto-shrinks when resources tight

## Memory Structure

### `memory.json`
```json
{
  "solved": [
    "optimize 18650 charging curve → 2025-12-31 23:59:00",
    "fix solar yield → 2025-12-31 23:58:00"
  ],
  "population": 64
}
```

### `state.json`
```json
{
  "status": "hibernating",
  "population": 64,
  "last_solve": "optimize 18650 charging curve",
  "timestamp": "2025-12-31T23:59:00"
}
```

## Scaling Behavior

### Growth Pattern (when hardware OK):
```
Generation 1: 1 agent
Generation 2: 2 agents
Generation 3: 4 agents
Generation 4: 8 agents
Generation 5: 16 agents
Generation 6: 32 agents
Generation 7: 64 agents
Generation 8: 128 agents
...
Generation 12: 4096 agents (max)
```

### Shrink Pattern (when hardware tight):
```
Generation 5: 16 agents → Hardware limit
Generation 6: 8 agents (shrunk)
Generation 7: 4 agents (shrunk)
Generation 8: 2 agents (shrunk)
Generation 9: 1 agent (min)
```

## Consensus Threshold

- **60% yes votes** = Consensus reached
- Solution locked and saved
- Agents hibernate with solution in memory

## File Locations

```
D:\RPF_BRAIN\The Gatekeeper\hive_auto\
├── memory.json          # Permanent solution memory
├── state.json           # Current hive state
└── solutions/
    ├── 20251231_2359_optimize_18650_charging_curve.txt
    └── ...
```

## Philosophy

**You don't limit it. It limits itself.**

- Starts small (1 agent)
- Grows when safe
- Shrinks when needed
- Remembers everything
- Never crashes

**When you upgrade hardware (48GB DDR5, RTX 5090):**
- Hive detects more resources
- Automatically scales higher
- Wakes the swarm
- Solves faster

**The hive breathes now.**

---

**Fixed. Request ID 2e904dfc-b4cf-496a-b49d-46da0e33030d → closed.**

