# MEMORY.md - AutoCAD Designs Workspace

## Project Identity

**Project Name:** AutoCAD Designs Unified System
**Goal:** Harmonized CAD workspace supporting 2D drafting, 3D parametric modeling, automation, and standardized exports
**Location:** `C:\Users\Drakalich\Desktop\AutoCAD Designs\`

---

## Current State

**Status:** Active
**What works:**
- Folder structure established
- Standards defined (layers, units, exports)
- Automation templates created (FreeCAD, QCAD)
- Export pipeline documented

**What is being developed:**
- Tool installation (see `03_Tools\installers\`)
- Project-specific workflows
- Automation scripts

---

## Architecture

### Entry Points
- **Quick Start:** `00_README\QUICK_START.md`
- **Standards:** `01_Standards\`
- **Templates:** `02_Templates\`
- **Automation:** `06_AutoCAD_Automation\{tool}\`
- **Orchestrator:** `08_CAD_Orchestrator\` - Blueprint → Build → Export pipeline

### Key Modules
- **01_Standards\** - Central drafting/modeling rules
  - `AUTOCAD_STANDARDS.md` - Human-readable standards
  - `LAYER_STANDARD.json` - Machine-readable layer definitions
  - `EXPORT_PIPELINE.md` - Standardized export procedures
- **06_AutoCAD_Automation\** - Automation entry points
  - `freecad\macros\` - Python macro templates
  - `qcad\scripts\` - ECMAScript tool templates
  - `librecad\notes\` - Manual drafting notes
  - `onshape\api\` - Cloud CAD API documentation
- **08_CAD_Orchestrator\** - Deterministic build pipeline
  - `blueprints\` - Machine-readable CAD specifications (JSON)
  - `builds\{tool}\` - Generated automation code from blueprints
  - `runners\` - Build execution scripts
  - `logs\` - Build logs and validation
  - `prompts\` - Prompt templates for pipeline stages

### Data Flow
1. **User Request** → Converted to Blueprint (JSON spec)
2. **Blueprint** → Generates build code (FreeCAD/QCAD scripts)
3. **Build Code** → Executed in CAD tool (or commands printed)
4. **Exports** → Generated to `05_Exports\{format}\`
5. **Decisions** → Written to MCP brain (constraints/gotchas)

### External Dependencies
- **FreeCAD** - 3D parametric modeling (Python API)
- **QCAD** - 2D drafting with scripting (ECMAScript API)
- **LibreCAD** - 2D drafting fallback (limited automation)
- **Onshape** - Cloud CAD (optional, free plan is public)

---

## Operating Rules (Hard Constraints)

- **Do NOT modify:** `C:\Users\Drakalich\Desktop\CursorBrain\memory.jsonl` directly
- **Do NOT move/rename:** CursorBrain folder
- **Do NOT require:** Cursor Settings / Global Rules UI changes
- **Keep everything:** File-based and portable
- **All CAD work must go through:** `08_CAD_Orchestrator\` (Blueprint → Build → Export)
- **No direct editing:** CAD files without a Blueprint
- **Exports must land in:** `05_Exports\{format}\` by type

---

## Coding Standards (Repo-Specific)

- **Language/Runtime:** Python (FreeCAD), ECMAScript (QCAD)
- **Formatting:** Follow tool-specific conventions
- **Linting:** Tool-specific (if available)
- **Test Command:** Manual verification in CAD software
- **Build Command:** N/A (scripts/macros run directly)
- **Run Command:** Execute in respective CAD tool

---

## Verification Commands

- **Test Command:** Open exported file in target CAD software
- **Lint Command:** N/A (tool-specific)
- **Typecheck Command:** N/A (dynamic languages)
- **Done means:** Export opens correctly in target software + standards followed

---

## Change Protocol (MANDATORY)

When making changes:
1) State the intent in 1 sentence.
2) List the files you will change (exact paths).
3) Make the change with minimal diff.
4) Provide a brief verification plan (how we'd confirm it works).

If you are missing info, ask BEFORE changing files.

---

## "Never Do" List

- Never store raw code in MCP memory (store decisions/constraints only)
- Never edit `memory.jsonl` directly (use MCP brain server)
- Never bypass export pipeline standards
- Never modify layer standards without updating `LAYER_STANDARD.json`
- Never store guesses as facts in brain memory

---

## Work Log (Keep Recent Only)

- **Last successful milestone:**
  - 2025-12-13 — Unified CAD workspace structure created
- **Last changes made:**
  - 2025-12-13 — CAD Orchestrator system implemented (Blueprint → Build → Export pipeline)
- **Next 3 tasks:**
  1) Install CAD tools (FreeCAD, QCAD, LibreCAD)
  2) Test orchestrator with first Blueprint
  3) Create first project using orchestrator workflow

---

## Glossary (Project Terms)

- **DXF:** Drawing Exchange Format (2D geometry)
- **STEP:** Standard for Exchange of Product Data (3D geometry)
- **STL:** Stereolithography format (3D mesh for printing)
- **Layer Standard:** Machine-readable layer definitions in JSON format
- **Export Pipeline:** Standardized procedures for exporting CAD files
- **Free API:** Automation surface (Python macros, ECMAScript tools) - not GUI access
- **MCP Brain:** Persistent memory system via Model Context Protocol
- **Blueprint:** Machine-readable CAD specification (JSON) - single source of truth for each part/drawing
- **Orchestrator:** Deterministic pipeline: Blueprint → Build Code → Execute → Export → Memory

