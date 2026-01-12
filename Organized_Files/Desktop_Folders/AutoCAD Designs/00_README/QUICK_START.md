# Quick Start - Unified CAD Workspace

## Workflow Overview

1. **Pick Project** → Navigate to `04_Projects\` or create new project folder
2. **Apply Standards** → Reference `01_Standards\` for layer rules, units, export formats
3. **Generate Automation** → Use templates in `06_AutoCAD_Automation\` to create macros/scripts
4. **Export** → Use standardized pipeline in `05_Exports\` for consistent output

---

## Tool Stack

### 3D Modeling
- **FreeCAD** (Primary)
  - Python macro API
  - Parametric modeling
  - Automation: `06_AutoCAD_Automation\freecad\macros\`

### 2D Drafting
- **QCAD** (Preferred for scripting)
  - ECMAScript API
  - Automation: `06_AutoCAD_Automation\qcad\scripts\`
- **LibreCAD** (Fallback)
  - Limited automation
  - Manual drafting tool

### Cloud Option
- **Onshape** (Optional)
  - Free plan documents are public
  - API: `06_AutoCAD_Automation\onshape\api\`

---

## First Steps

1. **Install Tools** → Run `03_Tools\installers\INSTALL_CAD_TOOLS.ps1` (prints commands)
2. **Review Standards** → Read `01_Standards\AUTOCAD_STANDARDS.md`
3. **Check Layer Standard** → `01_Standards\LAYER_STANDARD.json`
4. **Understand Export Pipeline** → `01_Standards\EXPORT_PIPELINE.md`

---

## Automation Workflow

### FreeCAD (3D)
1. Start with template: `06_AutoCAD_Automation\freecad\macros\_macro_template.py`
2. Customize for your task
3. Run macro in FreeCAD

### QCAD (2D)
1. Start with template: `06_AutoCAD_Automation\qcad\scripts\_tool_template.js`
2. Customize for your task
3. Load script in QCAD

---

## Standards Enforcement

- **Layer Standards** → Defined in `LAYER_STANDARD.json`
- **Export Formats** → Follow `EXPORT_PIPELINE.md`
- **Units** → Defined in `AUTOCAD_STANDARDS.md`

All standards are centralized and machine-readable for automation.

---

## Memory Integration

See `07_Brain_Link\BRAIN_USAGE.md` for how decisions and constraints are stored in the persistent brain system.

**Never edit** `C:\Users\Drakalich\Desktop\CursorBrain\memory.jsonl` directly.

---

## Project Organization

- **Active Projects** → `04_Projects\`
- **Exports** → `05_Exports\{format}\`
- **Archived** → `99_Archive\`

---

## Getting Help

- Standards questions → `01_Standards\`
- Automation templates → `06_AutoCAD_Automation\{tool}\`
- Export issues → `01_Standards\EXPORT_PIPELINE.md`

