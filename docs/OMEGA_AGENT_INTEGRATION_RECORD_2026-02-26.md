# Omega Agent Integration Record

Date: 2026-02-26

This record locks in the named runtime agent integration so the workspace can be resumed without rework.

Integrated named agents:
- Harriet (`harriet_agent`)
- Bob (`bob_agent`)

Integration points:
- Runtime agent modules in `agents/`
- Agent profile identity JSON in `config/agents/profiles/`
- Omega control-panel bootstrap registration in `omega_control_panel_web.py`
- Agent bundle export mapping in `unified_agent_framework.py`
- Named IDs for core agents and reserved summit seats in runtime modules

Persistence notes:
- Agent profiles are loaded by `UnifiedAgent._load_identity()` by `agent_id`.
- Registry activation path now includes Harriet and Bob, so startup restores these agents automatically.

Quick verification command:
```powershell
python -c "import sys; sys.path.insert(0, r'H:\The Gatekeeper'); sys.path.insert(0, r'H:\The Gatekeeper\agents'); from unified_agent_framework import get_agent_registry; from harriet_agent import HarrietAgent; from bob_agent import BobAgent; r=get_agent_registry(); r.register_agent(HarrietAgent()); r.register_agent(BobAgent()); print(r.get_agent('harriet_agent').name, r.get_agent('bob_agent').name)"
```
