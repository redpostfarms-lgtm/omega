# Prompt Template: Blueprint → TechDraw Drawing

## Usage

Generate FreeCAD TechDraw views from 3D model for blueprint-ready DXF/PDF export.

---

## Prompt Structure

```
TASK: Generate TechDraw Drawing from 3D Model

BLUEPRINT FILE:
{blueprint_file_path}

FREECAD MACRO:
{freecad_macro_path}

REQUIREMENTS:
1) Read Blueprint JSON file
2) Read existing FreeCAD macro (3D model already created)
3) Generate TechDraw drawing code
4) Add to FreeCAD macro or create separate TechDraw macro
5) Save to: 08_CAD_Orchestrator\builds\freecad\{name}_techdraw.py

TECHDRAW REQUIREMENTS:
- Create TechDraw page (A4 or Blueprint.exports.pdf.paper_size)
- Add views from Blueprint.views_2d:
  - Top view (if specified)
  - Front view (if specified)
  - Side view (if specified)
  - Isometric view (optional, for reference)
- Add dimensions from Blueprint.views_2d.annotations
- Set scale from Blueprint.views_2d.scale
- Apply layers/colors from LAYER_STANDARD.json
- Export to DXF: 05_Exports\DXF\{filename}.dxf
- Export to PDF: 05_Exports\PDF\{filename}.pdf

OUTPUT:
1) Create TechDraw macro file
2) Show drawing plan (which views will be created)
3) List dimension annotations that will be added
```

---

## TechDraw Workflow

### Standard Views
- **Top View:** Projection of model from above (Z-axis)
- **Front View:** Projection of model from front (Y-axis)
- **Side View:** Projection of model from side (X-axis)
- **Isometric:** 3D view for reference (optional)

### Dimensions
- Extract from `Blueprint.views_2d.annotations`
- Apply to appropriate views
- Use layer: A-DIM (from LAYER_STANDARD.json)

### Export
- **DXF:** TechDraw page → DXF (clean 2D blueprint)
- **PDF:** TechDraw page → PDF (print-ready drawing)

---

## Example

**Blueprint:** parametric_box_with_lid.json
**Views:** top, front, side
**Scale:** 1.0
**Paper:** A4

**TechDraw will create:**
- Page: A4 landscape
- Top view: Box outline with bolt holes
- Front view: Box profile with wall thickness
- Side view: Box profile with wall thickness
- Dimensions: Length, width, height, wall thickness, hole positions
- Export: DXF + PDF

