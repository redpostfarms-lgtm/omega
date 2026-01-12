# Prompt Template: Blueprint → QCAD Script

## Usage

Convert a Blueprint JSON file into a QCAD ECMAScript tool.

---

## Prompt Structure

```
TASK: Generate QCAD ECMAScript script from Blueprint

BLUEPRINT FILE:
{blueprint_file_path}

REQUIREMENTS:
1) Read Blueprint JSON file
2) Generate QCAD ECMAScript script
3) Save to: 08_CAD_Orchestrator\builds\qcad\{name}.js
4) Reference: 06_AutoCAD_Automation\qcad\scripts\_tool_template.js
5) Reference: 01_Standards\LAYER_STANDARD.json

SCRIPT REQUIREMENTS:
- Use units from Blueprint (mm or inches)
- Create all 2D features defined in Blueprint.geometry.features
- Apply layers from LAYER_STANDARD.json
- Include export functions for Blueprint.exports.dxf/pdf/svg
- Follow QCAD ECMAScript API conventions
- Register as menu tool if needed

OUTPUT:
1) Create the QCAD script file
2) Show build plan (what will be created)
3) List export commands that will be generated
```

