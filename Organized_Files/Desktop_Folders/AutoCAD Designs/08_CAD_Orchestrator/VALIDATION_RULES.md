# Validation Rules - Blueprint Feasibility Checks

## Overview

These rules are automatically checked before generating build code. They ensure designs are manufacturable and feasible.

---

## 1. Hole Placement Validation

### Rules
- **Hole to edge clearance:** Minimum 2 × hole_diameter from any edge
- **Hole to wall clearance:** Minimum 1 × hole_diameter from wall
- **Hole depth:** Must not exceed part thickness
- **Hole diameter:** Must be smaller than smallest wall dimension

### Example
For 0.25in diameter hole:
- Minimum distance from edge: 0.5in
- Minimum distance from wall: 0.25in
- Maximum depth: part thickness

---

## 2. Wall Thickness Validation

### Rules
- **Minimum wall thickness:** 0.1in (2.5mm) for manufacturability
- **Lid thickness:** Must not conflict with cavity (lid should fit opening)
- **Wall consistency:** All walls should have similar thickness (within 20%)

### Checks
- Inner cavity dimensions = outer dimensions - (2 × wall_thickness)
- Lid dimensions ≥ opening dimensions (for fit)
- Wall thickness ≥ minimum manufacturable thickness

---

## 3. Dimension Validation

### Rules
- **All dimensions positive:** No negative or zero dimensions
- **Inner vs outer consistency:** Inner must be smaller than outer
- **Feature bounds:** All features must fit within part bounds

### Checks
- length > 0, width > 0, height > 0
- inner_length < outer_length
- hole_position + hole_radius < part_edge

---

## 4. Layer Compliance

### Rules
- **Layer names:** Must exist in LAYER_STANDARD.json
- **Layer assignments:** Must be appropriate for feature type

### Checks
- All layer names in Blueprint exist in LAYER_STANDARD.json
- Mechanical features use M-* layers
- Architectural features use A-* layers

---

## 5. Export Feasibility

### Rules
- **STEP export:** Requires solid 3D geometry (no open surfaces)
- **DXF export:** Requires 2D projection (may need separate 2D views)
- **Export settings:** Must match geometry type

### Checks
- 3D geometry → STEP export possible
- 2D views defined → DXF export possible
- Export format matches geometry type

---

## Validation Workflow

1. **Read Blueprint** → Parse JSON
2. **Run all checks** → Apply validation rules
3. **Generate report** → List issues and warnings
4. **Decision:**
   - **PASS** → Proceed to build code generation
   - **FAIL** → Fix Blueprint and re-validate
   - **WARNINGS** → Proceed with warnings noted

---

## Example Validation

**Blueprint:** parametric_box_with_lid.json

**Checks:**
- ✅ Hole to edge: 0.5in clearance (0.25in hole × 2) - PASS
- ✅ Wall thickness: 0.125in (1/8in) - PASS (above 0.1in minimum)
- ✅ Hole depth: 0.5in < part height 6in - PASS
- ✅ Inner cavity: 11.75in < 12in outer - PASS
- ✅ Lid dimensions: 12in × 8in matches opening - PASS
- ✅ Layer M-BOLT exists in standard - PASS

**Result:** ✅ **VALIDATION PASSED** - Proceed to build code

---

## Updates

When validation rules change:
1. Update this file
2. Update validation prompt template
3. Write change to brain as `type: constraint`

