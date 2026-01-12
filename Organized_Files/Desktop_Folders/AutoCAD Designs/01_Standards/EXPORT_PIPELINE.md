# Export Pipeline - Standardized CAD Export Procedures

## Overview

This document defines the exact procedures for exporting CAD files in consistent formats. All exports go to `05_Exports\{format}\` with standardized naming.

---

## Export Formats

### DXF (Drawing Exchange Format)
**Location:** `05_Exports\DXF\`
**Use Case:** 2D drawings, layer-based geometry, cross-platform compatibility

**Procedure:**
1. Verify units (mm or inches) match project standard
2. Ensure all layers follow `LAYER_STANDARD.json`
3. Export settings:
   - Version: DXF R2018 (or latest compatible)
   - Units: Match project units
   - Layer names: Preserved
   - Colors: Preserved
4. File naming: `{ProjectName}_{DrawingNumber}_Rev{Revision}.dxf`

**Tools:**
- FreeCAD: File → Export → DXF
- QCAD: File → Export → DXF
- LibreCAD: File → Save As → DXF

---

### STEP (3D Geometry Exchange)
**Location:** `05_Exports\STEP\`
**Use Case:** 3D parametric models, manufacturing, CAD-to-CAD transfer

**Procedure:**
1. Verify 3D geometry is complete
2. Check units (mm standard, inches if specified)
3. Export settings:
   - Format: STEP AP214 (preferred) or AP203
   - Units: Millimeters (or Inches if project standard)
   - Tolerance: 0.001mm (default)
4. File naming: `{ProjectName}_{PartName}_Rev{Revision}.step`

**Tools:**
- FreeCAD: File → Export → STEP

**Note:** STEP is 3D only. 2D drawings use DXF.

---

### STL (Stereolithography)
**Location:** `05_Exports\STL\`
**Use Case:** 3D printing, rapid prototyping, mesh export

**Procedure:**
1. Convert solid geometry to mesh (if needed)
2. Set mesh resolution:
   - High quality: 0.1mm deviation
   - Standard: 0.5mm deviation
   - Draft: 1.0mm deviation
3. Export settings:
   - Format: ASCII or Binary (Binary preferred for size)
   - Units: Millimeters
4. File naming: `{ProjectName}_{PartName}_STL_{Quality}.stl`

**Tools:**
- FreeCAD: File → Export → STL

**Note:** STL is mesh-only. Parametric data is lost.

---

### PDF (Portable Document Format)
**Location:** `05_Exports\PDF\`
**Use Case:** Documentation, printing, sharing drawings

**Procedure:**
1. Set up paper space/layout view
2. Verify scale in title block
3. Export settings:
   - Paper size: A4, A3, or project-specific
   - Scale: Match title block scale
   - Vector graphics: Enabled (not rasterized)
   - Layers: All visible layers included
4. File naming: `{ProjectName}_{DrawingNumber}_Rev{Revision}.pdf`

**Tools:**
- FreeCAD: File → Export → PDF
- QCAD: File → Print → PDF
- LibreCAD: File → Print → PDF

---

### SVG (Scalable Vector Graphics)
**Location:** `05_Exports\SVG\`
**Use Case:** Web graphics, 2D vector illustrations, presentations

**Procedure:**
1. Export 2D view only (top, front, side)
2. Export settings:
   - Units: Millimeters or pixels
   - Layer colors: Preserved
   - Background: Transparent or white
3. File naming: `{ProjectName}_{ViewName}.svg`

**Tools:**
- FreeCAD: File → Export → SVG (2D views only)
- QCAD: File → Export → SVG

**Note:** SVG is 2D only. 3D geometry must be projected to 2D first.

---

## Export Checklist

Before exporting, verify:

- [ ] Units match project standard (mm or in)
- [ ] Layer names follow `LAYER_STANDARD.json`
- [ ] Title block information is complete
- [ ] Scale is documented
- [ ] File naming follows convention
- [ ] Export destination is `05_Exports\{format}\`

---

## Automation Integration

All export macros/scripts must:

1. **Read standards** from `LAYER_STANDARD.json`
2. **Apply units** from project settings
3. **Use file naming** convention above
4. **Write to** `05_Exports\{format}\`
5. **Log export** details (date, format, version)

**Example automation flow:**
```
1. Load project file
2. Apply layer standards
3. Verify units
4. Execute export with standardized settings
5. Save to 05_Exports\{format}\
6. Log export metadata
```

---

## Quality Checks

After export, verify:

- **DXF:** Open in target CAD software, check layers
- **STEP:** Import into target CAD, verify geometry
- **STL:** Check mesh quality, verify scale
- **PDF:** Verify print scale, check text readability
- **SVG:** Open in browser/viewer, check vector quality

---

## Troubleshooting

### Units Mismatch
**Symptom:** Imported file is wrong size
**Solution:** Verify export units match import expectations

### Missing Layers
**Symptom:** Layers not present in exported file
**Solution:** Check layer visibility, ensure all layers are exportable

### Scale Issues
**Symptom:** Drawing appears at wrong scale
**Solution:** Verify paper space scale matches export scale setting

---

## Updates

When export procedures change:
1. Update this file
2. Update affected automation scripts
3. Write change to brain (via MCP) as `type: constraint`

