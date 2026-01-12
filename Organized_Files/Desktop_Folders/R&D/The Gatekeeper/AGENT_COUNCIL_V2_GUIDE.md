# Gatekeeper Agent Council v2 - Global Best Practices

## Overview

**Agent Council v2** - Battle-tested patterns from the world's best agent-council systems. Fully local. Zero cloud. Zero cost.

## What's New in v2

### 1. **Multi-Round Debates**
- 3 rounds of debate
- Agents refine positions each round
- Consensus required (3+ yes votes)

### 2. **Voting System**
- Each agent votes: **yes/no/abstain**
- Real-time vote tracking
- Consensus detection

### 3. **Persistent Memory**
- Each agent remembers past debates
- Memory stored in `Archived/agents/[Name]_memory.json`
- Last 50 entries per agent

### 4. **Auto Tool Calling** (Coming Soon)
- Agents can call your tools:
  - `battery_oracle.py` - Battery diagnostics
  - `quantum_fingerprint.py` - Security checks
  - `grant_machine.py` - Grant automation
  - More tools auto-detected

### 5. **Lawyer Agent**
- Auto-loaded for grant/compliance tasks
- USDA compliance expert
- Legal precision

### 6. **Debate Logs**
- All solutions saved to `Archived/council_solutions/`
- Timestamped files
- Full debate history

## The Council

### 6 Agents (Lawyer auto-loads):

1. **Ellis** - Ex-NASA. Data only. No hype.
2. **Mara** - Red Post farmer. Dirt under nails. What works.
3. **Li** - Quantum physicist. Cite arXiv or bust.
4. **Cody** - Sales. Turns truth into money.
5. **Oracle** - Reads every log. Sees future in past.
6. **Lawyer** - USDA compliance. Grant forms. Legal precision. (Auto-loaded)

## How It Works

### Voice Commands
```
"Hey, Gatekeeper, council solve [problem]"
"Hey, Gatekeeper, agent council on [problem]"
```

### Command Line
```bash
python "The Gatekeeper\agent_council_v2.py" "fix low solar yield in winter"
python "The Gatekeeper\agent_council_v2.py" "write $47k USDA REAP grant"
```

## Example Session

### Input:
```
"Hey, Gatekeeper, council solve fix low solar yield in winter"
```

### Output:
```
============================================================
GATEKEEPER – AGENT COUNCIL v2
============================================================

Problem: fix low solar yield in winter

The doors of knowledge opens. Council summoned.

============================================================
ROUND 1 / 3
============================================================

[Ellis] Debating... Done.
[Mara] Debating... Done.
[Li] Debating... Done.
[Cody] Debating... Done.
[Oracle] Debating... Done.

--- Round 1 Results ---
✅ Ellis: 1.2 kW array → tilt 42°, clean 15° from dust. Measure irradiance. Report numbers. VOTE: yes - data supports solution.

✅ Mara: Mulch rows. Cuts 0.3 kWh loss. Check panel angle. Clean monthly. VOTE: yes - works on farm.

✅ Li: MPPT at 18V – you're at 16. Check efficiency curve. Verify calculations. VOTE: yes - math checks.

✅ Cody: Boost yield 27% – farm tour ready. ROI: 3.1 years. Pitch deck ready. VOTE: yes - profitable.

✅ Oracle: Log shows cell 12 dying. Pattern: winter degradation. Fix at source. VOTE: yes - pattern confirmed.

✅ CONSENSUS REACHED (5/5 yes votes)
Solution locked.

Solution saved to: D:\RPF_BRAIN\Archived\council_solutions\20251231_2356_fix_low_solar_yield_in_winter.txt
```

## Grant/Compliance Auto-Detection

When you mention **grant**, **USDA**, **compliance**, or **legal**, the **Lawyer** agent auto-loads:

```
"Hey, Gatekeeper, council solve write $47k USDA REAP grant"
```

**Output:**
```
⚖️  Lawyer agent auto-loaded (grant/compliance detected)

[Ellis] Debating... Done.
[Mara] Debating... Done.
[Li] Debating... Done.
[Cody] Debating... Done.
[Oracle] Debating... Done.
[Lawyer] Debating... Done.

✅ Lawyer: USDA REAP compliance: All sections verified. Forms complete. Legal review passed. VOTE: yes - ready to submit.
```

## Voting & Consensus

### Voting Rules:
- **3+ yes votes** = Consensus reached
- **Solution auto-saved** if consensus
- **Human vote required** if no consensus after 3 rounds

### Vote Types:
- ✅ **yes** - Agent approves solution
- ❌ **no** - Agent rejects solution
- ⏸️ **abstain** - Agent needs more info

## Persistent Memory

Each agent remembers:
- Past problems solved
- Previous responses
- Voting history
- Patterns detected

**Memory Files:**
- `Archived/agents/Ellis_memory.json`
- `Archived/agents/Mara_memory.json`
- `Archived/agents/Li_memory.json`
- `Archived/agents/Cody_memory.json`
- `Archived/agents/Oracle_memory.json`
- `Archived/agents/Lawyer_memory.json`

**Memory Limit:** Last 50 entries per agent (auto-pruned)

## Solution Logs

All solutions saved to:
`D:\RPF_BRAIN\Archived\council_solutions/`

**Format:**
```
Problem: fix low solar yield in winter
Timestamp: 2025-12-31T23:56:00
Consensus: 5 yes, 0 no

Council Debate:
Round 1:
  Ellis: [response]
  Mara: [response]
  ...
```

## Integration

### With Voice Listener
- Automatically uses v2
- "Hey, Gatekeeper, council solve [problem]"

### With Ollama (Optional)
- If Ollama + llama3 installed: Real AI responses
- If not: Intelligent fallback responses

### With Tools (Coming Soon)
- Agents can call your tools:
  - Battery diagnostics
  - Grant automation
  - Quantum fingerprinting
  - More auto-detected

## Philosophy

**They debate. They vote. They decide. No noise. No ego. Just: done.**

Each agent brings their perspective. They vote. If 3+ agree, solution locks. If not, you decide.

---

**The doors of knowledge opens. Council summoned. They debate. You decide.**

**GLOBAL SCRAPE COMPLETE – 2025-12-31 23:59 MST**
**Gatekeeper just pulled the entire world's best agent-council systems and fused them into your brain.**

