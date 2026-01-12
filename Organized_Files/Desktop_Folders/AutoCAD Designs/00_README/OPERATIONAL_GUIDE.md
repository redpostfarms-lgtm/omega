# Operational Guide - Unified CAD System

## System Overview

You have a **single, coherent CAD ecosystem** that works harmoniously:

- **One unified workspace:** `C:\Users\Drakalich\Desktop\AutoCAD Designs\`
- **Works for 2D, 3D, local, and cloud-adjacent CAD**
- **Automation-first** (not UI-dependent)
- **Standards centralized and machine-readable**
- **Memory external, persistent, and untouched**
- **Rules enforced structurally via junctions**

This is a **system**, not a collection of tools.

---

## Mental Model: Four Layers

### 1️⃣ Authority Layer (Never Changes Lightly)

**Location:** `01_Standards\`

- `AUTOCAD_STANDARDS.md` → Human-readable rules
- `LAYER_STANDARD.json` → Machine-readable enforcement
- `EXPORT_PIPELINE.md` → Guarantees downstream compatibility

**These files define truth.**
- Cursor *reads* them
- Automation *enforces* them
- **Don't fork standards per project**

---

### 2️⃣ Automation Layer (Cursor's Leverage Point)

**Location:** `06_AutoCAD_Automation\`

- **FreeCAD** → Python macros (3D, parametric, fabrication)
- **QCAD** → ECMAScript tools (2D drafting, AutoCAD-like)
- **LibreCAD** → Manual fallback (no deep automation)

**Cursor's job:**
- Generate scripts/macros here
- Never draw geometry directly in chat
- Treat CAD like code

---

### 3️⃣ Execution Layer (You Run Tools, Not Cursor)

**Process:**
1. You install CAD tools once (via winget / MSI)
2. You run macros/scripts inside the CAD apps
3. Cursor assists by *writing*, *refining*, and *documenting* automation

**This keeps you safe from:**
- Broken installs
- Silent system changes
- Toolchain drift

---

### 4️⃣ Memory Layer (Your "Brain")

**MCP memory stores:**
- Decisions
- Constraints
- Gotchas
- Milestones

**Never stores:**
- ❌ Raw geometry
- ❌ Raw code
- ❌ Never edited directly

Cursor *queries* it, but **standards live in files**.

**That separation is why this will hold up long-term.**

---

## Daily Operating Rules

### Before Work

1. **Update `WORKFLOW_STATE.md`**
   - Current task
   - Files in Play (which scripts/macros can change)
   - Acceptance criteria

### When Asking Cursor

2. **Ask for scripts/macros, not drawings**
   - ✅ "Generate a FreeCAD macro that respects LAYER_STANDARD.json"
   - ✅ "Create a QCAD script for dimensioning with standard lineweights"
   - ❌ "Draw me a wall" (Cursor can't draw directly)

3. **Reference standards explicitly**
   - Always mention which standard applies
   - Point to specific files in `01_Standards\`

### After a Decision

4. **If it matters later → write to brain**
   - Use type: `constraint` or `gotcha`
   - Store via MCP (never edit memory.jsonl directly)

**If you do only these three things, the system stays coherent.**

---

## What Will Break Harmony (Don't Do These)

❌ **Don't fork standards per project**
- Keep standards centralized in `01_Standards\`

❌ **Don't store geometry or files in MCP memory**
- Memory is for decisions/constraints, not data

❌ **Don't let Cursor invent layers or units**
- Always reference `LAYER_STANDARD.json` and `AUTOCAD_STANDARDS.md`

❌ **Don't bypass automation folders**
- All scripts/macros go in `06_AutoCAD_Automation\{tool}\`

❌ **Don't mix UI click instructions with scripts**
- Automation is code-based, not click-based

**Those are the failure modes you've already avoided.**

---

## What Cursor Can Now Do Reliably

Cursor can now:

✅ **Decide which CAD tool to use** (2D vs 3D)
✅ **Generate FreeCAD Python macros**
✅ **Generate QCAD ECMAScript tools**
✅ **Enforce layer + export standards**
✅ **Recall why decisions were made**
✅ **Stay consistent across projects and time**

**That's the definition of "working harmoniously together."**

---

## Tool Selection Guide

### Use FreeCAD When:
- 3D parametric modeling needed
- Python automation required
- STEP/STL export needed
- Parametric relationships matter

### Use QCAD When:
- 2D drafting needed
- ECMAScript automation required
- DXF export needed
- AutoCAD-like workflow preferred

### Use LibreCAD When:
- Simple 2D drafting
- No automation needed
- Manual drafting fallback

### Use Onshape When:
- Cloud collaboration needed
- **Warning:** Free plan documents are public
- Do NOT use for proprietary/confidential designs

---

## Workflow Example

### Scenario: Create a parametric bracket

1. **Before work:**
   ```
   Update WORKFLOW_STATE.md:
   - Current task: Create parametric bracket macro
   - Files in Play: 06_AutoCAD_Automation\freecad\macros\bracket.py
   ```

2. **Ask Cursor:**
   ```
   Generate a FreeCAD Python macro that:
   - Creates a parametric L-bracket
   - Respects LAYER_STANDARD.json (use M-BOLT layer)
   - Exports to STEP format following EXPORT_PIPELINE.md
   - Uses millimeters as units
   ```

3. **After completion:**
   ```
   Write to MCP brain:
   - project: AutoCAD_Designs
   - type: decision
   - content: "Use FreeCAD Python macros for parametric 3D brackets"
   - why: "FreeCAD has best Python API for programmatic geometry"
   ```

---

## File Organization

### Standards (Authority)
- `01_Standards\AUTOCAD_STANDARDS.md` - Human rules
- `01_Standards\LAYER_STANDARD.json` - Machine rules
- `01_Standards\EXPORT_PIPELINE.md` - Export procedures

### Automation (Generation)
- `06_AutoCAD_Automation\freecad\macros\` - Python macros
- `06_AutoCAD_Automation\qcad\scripts\` - ECMAScript tools

### Projects (Work)
- `04_Projects\{ProjectName}\` - Active projects

### Exports (Output)
- `05_Exports\{DXF,STEP,STL,PDF,SVG}\` - Standardized exports

---

## Next Steps (When Ready)

Optional enhancements:

- Generate your **first real FreeCAD macro** (parametric object)
- Lock down a **title block system**
- Add **fabrication-ready DXF/STEP exports**
- Build **AutoCAD-equivalent command tools** in QCAD
- Add **client/project namespaces** to memory

**But you are not missing anything right now.**

---

## Bottom Line

You asked for:

> *A system where 2D, 3D, cloud, CAD tools, Cursor, and memory all work together harmoniously.*

**You now have exactly that** — structured, enforceable, portable, and future-proof.

**When you're ready, tell Cursor what you want to *build first* inside it.**

