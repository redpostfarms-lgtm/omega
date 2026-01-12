# Gatekeeper Agent Council Mode

## Overview

When a task lands, the Agent Council debates. You decide.

## The Council

### 5 Agents:

1. **Ellis** - Ex-NASA. Zero hype. Wants data.
2. **Mara** - Farmer. Knows mud. Says what works.
3. **Li** - Quantum. Cites papers. No guesswork.
4. **Cody** - Salesman. Turns facts into pitch.
5. **Oracle** - Looks at logs. Sees patterns. Silent until truth.

## How It Works

### Voice Command
```
"Hey, Gatekeeper, council solve [problem]"
"Hey, Gatekeeper, agent council on [problem]"
```

### Command Line
```bash
python "The Gatekeeper\agent_council.py" --problem "fix low solar yield in winter"
```

## Example Session

### Input:
```
"Hey, Gatekeeper, council solve fix low solar yield in winter"
```

### Output:
```
============================================================
GATEKEEPER – AGENT COUNCIL MODE
============================================================

Problem: fix low solar yield in winter

The doors of knowledge opens. Council forms.

Council forming...

[Ellis] Thinking... Done.
[Mara] Thinking... Done.
[Li] Thinking... Done.
[Cody] Thinking... Done.
[Oracle] Thinking... Done.

============================================================
COUNCIL DEBATE
============================================================

Ellis: 1.2 kW array → tilt 42°, clean 15° from dust. Measure irradiance. Report numbers.

Mara: Mulch rows. Cuts 0.3 kWh loss. Check panel angle. Clean monthly.

Li: MPPT at 18V – you're at 16. Check efficiency curve. Verify calculations.

Cody: Boost yield 27% – farm tour ready. ROI: 3.1 years. Pitch deck ready.

Oracle: Log shows cell 12 dying. Pattern: winter degradation. Fix at source.

============================================================
Council vote? (yes/no)
============================================================
> yes

✅ Solution locked.
Council session saved.
```

## Agent Personalities

### Ellis (Ex-NASA)
- Focus: Data, measurements, diagnostics
- Style: Numbers, precision, verification
- Example: "1.2 kW array → tilt 42°, clean 15° from dust. Measure irradiance. Report numbers."

### Mara (Farmer)
- Focus: Practical solutions, what works
- Style: Simple, direct, farm-tested
- Example: "Mulch rows. Cuts 0.3 kWh loss. Check panel angle. Clean monthly."

### Li (Quantum)
- Focus: Scientific analysis, equations
- Style: Technical, precise, cites sources
- Example: "MPPT at 18V – you're at 16. Check efficiency curve. Verify calculations."

### Cody (Salesman)
- Focus: ROI, presentation, opportunity
- Style: Pitch-ready, numbers, business case
- Example: "Boost yield 27% – farm tour ready. ROI: 3.1 years. Pitch deck ready."

### Oracle (Logs)
- Focus: Patterns, historical data, root cause
- Style: Silent until truth, data-driven
- Example: "Log shows cell 12 dying. Pattern: winter degradation. Fix at source."

## Decision Process

1. **Council Forms** - All 5 agents activated
2. **Debate** - Each agent provides 2-line solution
3. **You Decide** - Vote yes/no
4. **Solution Locked** - If yes, solution saved
5. **Council Dismissed** - If no, task canceled

## Session Logs

All council sessions are saved to:
`D:\RPF_BRAIN\Archived\council_logs\council_YYYYMMDD_HHMMSS.txt`

Includes:
- Problem statement
- All agent responses
- Your decision
- Timestamp

## Integration

### With Voice Listener
- Automatically activated via voice command
- "Hey, Gatekeeper, council solve [problem]"

### With Ollama (Optional)
- If Ollama + llama3 installed: Real AI responses
- If not: Intelligent fallback responses based on agent personality

## Philosophy

**They don't fight. They decide. No noise. No ego. Just: done.**

Each agent brings their perspective. You make the final call. The Gatekeeper executes.

---

**The doors of knowledge opens. Council forms. You decide.**

