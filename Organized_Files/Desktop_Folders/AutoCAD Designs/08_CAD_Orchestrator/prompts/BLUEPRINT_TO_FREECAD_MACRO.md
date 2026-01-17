# Prompt Template: Blueprint → FreeCAD Macro

## Usage

Convert a Blueprint JSON file into a FreeCAD Python macro.

---

## Prompt Structure

```text
TASK: Generate FreeCAD Python macro from Blueprint

BLUEPRINT FILE:
{blueprint_file_path}

REQUIREMENTS:
1) Read Blueprint JSON file
2) Generate FreeCAD Python macro
3) Save to: 08_CAD_Orchestrator\builds\freecad\{name}.py
4) Reference: 06_AutoCAD_Automation\freecad\macros\_macro_template.py
5) Reference: 01_Standards\LAYER_STANDARD.json

MACRO REQUIREMENTS:
- Use units from Blueprint (mm or inches)
- Create all features defined in Blueprint.geometry.features
- Apply layers from LAYER_STANDARD.json
- Include export functions for Blueprint.exports targets
- Follow FreeCAD Python API conventions
- Add comments explaining each feature

OUTPUT:
1) Create the FreeCAD macro file
2) Show build plan (what will be created)
3) List export commands that will be generated
```text

