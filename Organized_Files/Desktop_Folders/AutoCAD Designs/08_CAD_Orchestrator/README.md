# CAD Orchestrator - Blueprint → Build → Export Pipeline

## Overview

The CAD Orchestrator provides a **deterministic, repeatable pipeline** for CAD work:

1. **Blueprint** (JSON spec) - Machine-readable specification
2. **Build Code** (FreeCAD/QCAD scripts) - Generated from Blueprint
3. **Execute** (Run in CAD tool) - Or print commands
4. **Export** (Standardized outputs) - To `05_Exports\{format}\`
5. **Memory** (Decisions/constraints) - Written to MCP brain

---

## Workflow

### Step 1: Create Blueprint

Use prompt: `prompts\CAD_REQUEST_TO_BLUEPRINT.md`

**Input:** User request (e.g., "Design a 3D worm-tea agitator tank stand")
**Output:** `blueprints\{name}.json`

### Step 2: Generate Build Code

Use prompts:
- `prompts\BLUEPRINT_TO_FREECAD_MACRO.md` (for 3D)
- `prompts\BLUEPRINT_TO_QCAD_SCRIPT.md` (for 2D)

**Input:** Blueprint JSON
**Output:** 
- `builds\freecad\{name}.py` (3D model)
- `builds\qcad\{name}.js` (2D drafting)

### Step 2b: Generate TechDraw Drawing (for Blueprint-Ready DXF/PDF)

Use prompt: `prompts\BLUEPRINT_TO_TECHDRAW.md`

**Input:** Blueprint JSON + 3D model macro
**Output:** 
- `builds\freecad\{name}_techdraw.py` (TechDraw views)

**This creates:**
- TechDraw page with standard views (top, front, side)
- Dimensions (from Blueprint annotations)
- Blueprint-ready DXF/PDF exports

### Step 3: Run Build

Use: `runners\run_build.ps1 -BlueprintFile {name}.json`

**Output:** Commands printed (user runs manually)

**Execution Order:**
1. Run 3D model macro first: `builds\freecad\{name}.py`
2. Then run TechDraw macro: `builds\freecad\{name}_techdraw.py` (for DXF/PDF)

### Step 4: Export

Exports automatically go to `05_Exports\{format}\` per Blueprint.exports settings

### Step 5: Log & Memory

- Create log: `logs\{name}_build_log.md`
- Write to brain: Decisions/constraints/gotchas (via MCP)

---

## File Structure

```
08_CAD_Orchestrator\
├── BLUEPRINT_SCHEMA.json       # JSON Schema for blueprints
├── blueprints\                 # Blueprint JSON files
├── builds\
│   ├── freecad\                # Generated FreeCAD macros
│   └── qcad\                   # Generated QCAD scripts
├── runners\
│   └── run_build.ps1          # Build execution script
├── logs\                       # Build logs
├── prompts\                    # Prompt templates
│   ├── CAD_REQUEST_TO_BLUEPRINT.md
│   ├── BLUEPRINT_TO_FREECAD_MACRO.md
│   └── BLUEPRINT_TO_QCAD_SCRIPT.md
└── references\
    └── REFERENCE_POLICY.md     # Web research guidelines
```

---

## Quick Start

**Example Request:**
"Design a 3D worm-tea agitator tank stand, 55-gal drum, include bolt pattern, export STEP + DXF + PDF."

**Cursor will:**
1. Create Blueprint: `blueprints\worm_tea_stand.json`
2. Generate FreeCAD macro: `builds\freecad\worm_tea_stand.py`
3. Print run commands
4. Export to: `05_Exports\{STEP,DXF,PDF}\`
5. Write decisions to brain

---

## Rules

- **All CAD work goes through orchestrator** (no direct file editing)
- **Blueprints are single source of truth** for each part/drawing
- **Exports must land in** `05_Exports\{format}\` by type
- **Memory stores decisions/constraints**, not raw geometry or code

---

## See Also

- `BLUEPRINT_SCHEMA.json` - Blueprint format specification
- `prompts\` - Prompt templates for each stage
  - `SYSTEM_PROMPT.md` - Master system prompt for Cursor integration
- `references\REFERENCE_POLICY.md` - Safe web research guidelines
- `CURSOR_INTEGRATION.md` - How to use Cursor with this orchestrator
- `TECHDRAW_WORKFLOW.md` - TechDraw drawing generation guide

