# Build Log Template

## Build Information

**Blueprint:** `{blueprint_name}.json`
**Date:** {date}
**Build Type:** {2d|3d|mixed}
**Tool:** {FreeCAD|QCAD|Both}

---

## Inputs

- **Blueprint File:** `08_CAD_Orchestrator\blueprints\{name}.json`
- **Standards Reference:** `01_Standards\LAYER_STANDARD.json`
- **Export Pipeline:** `01_Standards\EXPORT_PIPELINE.md`

---

## Outputs

### Generated Files
- **FreeCAD Macro:** `08_CAD_Orchestrator\builds\freecad\{name}.py` (if 3D)
- **QCAD Script:** `08_CAD_Orchestrator\builds\qcad\{name}.js` (if 2D)

### Exports
- [ ] DXF: `05_Exports\DXF\{filename}.dxf`
- [ ] STEP: `05_Exports\STEP\{filename}.step`
- [ ] STL: `05_Exports\STL\{filename}.stl`
- [ ] PDF: `05_Exports\PDF\{filename}.pdf`
- [ ] SVG: `05_Exports\SVG\{filename}.svg`

---

## Decisions Made

1. **Tool Selection:**
   - Why FreeCAD: {reason}
   - Why QCAD: {reason}

2. **Layer Assignment:**
   - {feature} → {layer} (reason: {why})

3. **Export Format:**
   - Selected: {formats}
   - Reason: {why}

---

## Validation Checklist

- [ ] Blueprint validates against BLUEPRINT_SCHEMA.json
- [ ] All layers exist in LAYER_STANDARD.json
- [ ] Units match project standard
- [ ] Export filenames follow convention
- [ ] Macro/script executes without errors
- [ ] Exports open correctly in target software
- [ ] Geometry matches Blueprint specifications

---

## Gotchas / Issues

- {Issue 1}: {Resolution}
- {Issue 2}: {Resolution}

---

## Memory Entries (Written to Brain)

- **Type:** {constraint|decision|gotcha|milestone}
- **Content:** {what was stored}
- **Why:** {reason}

---

## Next Steps

1. {Next action}
2. {Next action}

