# TechDraw Workflow - Blueprint-Ready DXF/PDF

## Overview

TechDraw is FreeCAD's technical drawing workbench. It converts 3D models into 2D blueprint drawings with dimensions, views, and annotations.

**Why TechDraw instead of raw edge projection:**
- ✅ Clean 2D views (not messy edges)
- ✅ Proper dimensions
- ✅ Standard drawing format
- ✅ Print-ready PDF
- ✅ Consistent across projects

---

## Workflow

### 1. Create 3D Model First
Run the main FreeCAD macro to generate the 3D solid:
```text
builds\freecad\{name}.py
```text

This creates the 3D geometry (box, lid, holes, etc.)

### 2. Generate TechDraw Drawing
Run the TechDraw macro:
```text
builds\freecad\{name}_techdraw.py
```text

This creates:
- TechDraw page (A4 or specified paper size)
- Standard views (top, front, side, isometric)
- Dimensions (from Blueprint annotations)
- Export-ready drawing

### 3. Export DXF/PDF
TechDraw exports:
- **DXF:** Clean 2D blueprint with views and dimensions
- **PDF:** Print-ready drawing with title block

---

## What TechDraw Creates

### Standard Views
- **Top View:** Projection from above (shows length × width)
- **Front View:** Projection from front (shows length × height)
- **Side View:** Projection from side (shows width × height)
- **Isometric:** 3D reference view (optional)

### Dimensions
- Extracted from `Blueprint.views_2d.annotations`
- Applied to appropriate views
- Uses A-DIM layer (from LAYER_STANDARD.json)

### Export
- **DXF:** TechDraw page → DXF (clean 2D blueprint)
- **PDF:** TechDraw page → PDF (print-ready with title block)

---

## Comparison: Raw Edge vs TechDraw

### Raw Edge Projection (Old Method)
- ❌ Messy edges
- ❌ No dimensions
- ❌ Inconsistent views
- ❌ Not blueprint-ready

### TechDraw (New Method)
- ✅ Clean 2D views
- ✅ Proper dimensions
- ✅ Standard format
- ✅ Blueprint-ready

---

## Expected Outcomes

### STEP Export
- ✅ **Should be:** Solid and clean
- ✅ **Contains:** 3D geometry (box, lid, holes)
- ✅ **Use:** CAD-to-CAD transfer, manufacturing

### DXF Export (TechDraw)
- ✅ **Should be:** Clean 2D blueprint
- ✅ **Contains:** Top/front/side views, dimensions, annotations
- ✅ **Use:** 2D drafting, documentation, printing

### PDF Export (TechDraw)
- ✅ **Should be:** Print-ready drawing
- ✅ **Contains:** All views, dimensions, title block
- ✅ **Use:** Documentation, sharing, printing

---

## Troubleshooting

### TechDraw Views Not Appearing
- **Check:** 3D model exists in document
- **Check:** Source objects are selected correctly
- **Fix:** Run 3D model macro first, then TechDraw macro

### Dimensions Missing
- **Note:** Some dimensions may need manual addition in TechDraw GUI
- **Workaround:** Add dimensions in FreeCAD TechDraw workbench after views are created

### DXF Export Fails
- **Check:** TechDraw page is selected
- **Try:** Manual export: Select page → File → Export → DXF
- **Check:** FreeCAD TechDraw workbench is loaded

---

## Updates

When TechDraw workflow changes:
1. Update this file
2. Update TechDraw prompt template
3. Write change to brain as `type: constraint`

