# WORKFLOW_STATE.md (Short-Term)

## Current Task
- Setting up unified CAD workspace structure
- Creating standards and automation templates

## Files in Play
- `01_Standards\AUTOCAD_STANDARDS.md`
- `01_Standards\LAYER_STANDARD.json`
- `01_Standards\EXPORT_PIPELINE.md`
- `06_AutoCAD_Automation\freecad\macros\_macro_template.py`
- `06_AutoCAD_Automation\qcad\scripts\_tool_template.js`
- `MEMORY.md`
- `WORKFLOW_STATE.md`

## Do-Not-Touch
- `C:\Users\Drakalich\Desktop\CursorBrain\memory.jsonl` (never edit directly)
- `C:\Users\Drakalich\Desktop\CursorBrain\` folder structure
- Canonical rules in `CursorBrain\PROJECT_RULES\`

## Acceptance Criteria
- [x] Folder structure created
- [x] Standards files created (AUTOCAD_STANDARDS.md, LAYER_STANDARD.json, EXPORT_PIPELINE.md)
- [x] Automation templates created (FreeCAD, QCAD)
- [x] Install script created (prints commands, doesn't execute)
- [x] Brain integration documented
- [x] MEMORY.md and WORKFLOW_STATE.md created
- [ ] CAD tools installed (user action required)
- [ ] First test project created

## Next Actions (max 5)
1) Run `03_Tools\installers\INSTALL_CAD_TOOLS.ps1` to see installation commands
2) Install CAD tools (FreeCAD, QCAD, LibreCAD) using printed commands
3) Test automation templates with sample geometry
4) Create first project in `04_Projects\`
5) Write initial standards to brain (via MCP) as constraints

