# Cursor Integration Guide - CAD Automation

## Overview

This guide explains how to use Cursor (cursor.com) as your AI brain for AutoCAD/FreeCAD automation within this orchestrator system.

---

## Why Cursor for CAD Automation

- **Sees your whole project** - Multi-file edits, context across entire workspace
- **Agent-style coding** - Composer mode plans, edits, and runs commands
- **Built-in Claude 3.5/Opus** - Excellent for engineering code
- **One window** - Write, debug, and test in same interface
- **Project rules** - Enforce CAD standards automatically

---

## Setup Steps

### 1. Download Cursor
- Visit: https://cursor.com
- Free tier: Solid for daily use
- Pro: $20/month for unlimited fast Claude calls

### 2. Open AutoCAD Designs as Project
- Open folder: `C:\Users\Drakalich\Desktop\AutoCAD Designs\`
- Cursor will see entire orchestrator structure

### 3. Configure Model
- Cursor → Settings → Model
- Set to: **Claude 3.5 Sonnet** or **Opus**
- These models excel at engineering code

### 4. Use Composer Mode
- **Mac:** ⌘+L
- **Windows:** Ctrl+L
- This is the agent that plans, edits multiple files, and runs commands

### 5. Add Project Rules
- Cursor → Settings → Rules
- Paste contents of: `08_CAD_Orchestrator\prompts\SYSTEM_PROMPT.md`
- Or reference it in your rules

---

## Using the System Prompt

### Option A: Add to Cursor Rules
1. Cursor → Settings → Rules
2. Copy contents of `SYSTEM_PROMPT.md`
3. Paste into Rules field
4. Save

### Option B: Reference in Composer
1. Open Composer (⌘+L or Ctrl+L)
2. Say: "From now on, act as my full-time AutoCAD/FreeCAD parametric specialist using the system prompt in `08_CAD_Orchestrator\prompts\SYSTEM_PROMPT.md`"

### Option C: Use as Context
- Keep `SYSTEM_PROMPT.md` open in Cursor
- Reference it when starting new projects

---

## Workflow with Cursor

### Starting a New Project

1. **Open Composer** (⌘+L / Ctrl+L)
2. **Say:** "New project: {description}" or paste blueprint
3. **Cursor will:**
   - Ask clarifying questions (tolerances, material, fits)
   - Create folder structure
   - Generate Blueprint JSON
   - Generate 3D model macro
   - Generate TechDraw macro
   - Create test template
   - Output execution steps

### Example Prompt

```text
New project: parametric enclosure from this sketch
[attach image or describe]

Follow the orchestrator workflow:
1. Create Blueprint
2. Validate Blueprint
3. Generate 3D model macro
4. Generate TechDraw macro
5. Output execution steps
```text

---

## Integration with Existing Orchestrator

The SYSTEM_PROMPT.md works seamlessly with:

- **Blueprint Schema:** `BLUEPRINT_SCHEMA.json`
- **Validation:** `VALIDATION_RULES.md`
- **Prompts:** `prompts\BLUEPRINT_TO_FREECAD_MACRO.md`, `prompts\BLUEPRINT_TO_TECHDRAW.md`
- **Testing:** `logs\TEST_RESULT_TEMPLATE.md`

Cursor will automatically:
- Reference these files
- Follow the orchestrator workflow
- Maintain folder structure
- Generate compliant code

---

## Cursor-Specific Features

### Multi-File Edits
Cursor can edit multiple files simultaneously:
- Blueprint JSON
- FreeCAD macro
- TechDraw macro
- Test template
All in one Composer session

### Project Context
Cursor sees:
- Existing standards (`01_Standards\`)
- Previous blueprints (`blueprints\`)
- Previous builds (`builds\`)
- Test results (`logs\`)

This enables:
- Consistent naming
- Layer compliance
- Export pipeline adherence

### Agent Mode
Composer mode can:
- Plan the entire workflow
- Generate all files
- Run validation
- Output test checklist

---

## Best Practices

### 1. Use Project Rules
Add to Cursor Settings → Rules:
```text
Always reference:
- 01_Standards\LAYER_STANDARD.json for layers
- 01_Standards\EXPORT_PIPELINE.md for exports
- 08_CAD_Orchestrator\VALIDATION_RULES.md for checks
```text

### 2. Start with Blueprint
Always create Blueprint first:
- Ensures single source of truth
- Enables validation
- Makes regeneration easy

### 3. Split Macros
Always separate:
- 3D model macro
- TechDraw macro
- Makes debugging easier
- Allows independent regeneration

### 4. Test Template
Always fill out:
- `logs\TEST_RESULT_TEMPLATE.md`
- Helps improve orchestrator
- Documents what works/doesn't

---

## Example: Full Workflow in Cursor

### Step 1: Open Composer
⌘+L (Mac) or Ctrl+L (Win)

### Step 2: Give Blueprint
```text
Create a parametric mounting bracket:
- Base: 4in × 3in × 0.25in
- Vertical plate: 3in × 2in × 0.25in
- 4 mounting holes: 0.25in diameter, 0.5in from edges
- Export: STEP + DXF + PDF
```text

### Step 3: Cursor Executes
Cursor will:
1. Ask clarifying questions (material? tolerances?)
2. Create Blueprint JSON
3. Validate Blueprint
4. Generate FreeCAD macro
5. Generate TechDraw macro
6. Output execution steps
7. Create test template

### Step 4: Run & Test
1. Run macros in FreeCAD
2. Fill out test template
3. Report results back to Cursor
4. Cursor improves templates

---

## Advanced: Custom Rules

Add to Cursor Settings → Rules for AutoCAD-specific work:

```text
AutoCAD Rules:
- Always use (vl-load-com) for ActiveX
- Never use entmake for blocks
- Prefer ActiveX over entmod
- Comment every function
- Target AutoCAD 2024+
```text

---

## Status

- **SYSTEM_PROMPT.md:** Created and ready
- **Integration:** Works with existing orchestrator
- **Cursor Setup:** Documented above

**You're ready to use Cursor as your CAD automation brain!**

