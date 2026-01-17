# AutoCAD Standards - Central Drafting/Modeling Rules

## Units

**Default:** Millimeters (mm)
**Alternative:** Inches (in) - specify per project

**Note:** Always verify unit settings before starting new project. Unit mismatches cause export failures.

---

## Layers

**Standard:** See `LAYER_STANDARD.json` for machine-readable layer definitions.

### Layer Naming Convention
- Prefix: `A-` (Architecture), `M-` (Mechanical), `E-` (Electrical), `P-` (Piping)
- Suffix: Object type (WALL, DOOR, WINDOW, etc.)

**Examples:**
- `A-WALL` - Architectural walls
- `M-BOLT` - Mechanical fasteners
- `E-WIRE` - Electrical wiring

### Layer Properties
- **Color:** Defined in `LAYER_STANDARD.json`
- **Linetype:** Continuous, Dashed, Dotted (as defined)
- **Lineweight:** 0.13mm (thin), 0.25mm (medium), 0.50mm (thick)

---

## Lineweights

| Type | Weight | Usage |
| ------ | -------- | ------- |
| Thin | 0.13mm | Construction lines, dimensions |
| Medium | 0.25mm | Standard geometry, annotations |
| Thick | 0.50mm | Outlines, important features |

---

## Title Blocks

**Location:** `02_Templates\`

**Required Fields:**
- Project name
- Drawing number
- Revision
- Date
- Scale
- Units

**Template Format:** Use FreeCAD/QCAD title block templates from `02_Templates\`

---

## Dimension Standards

- **Text Height:** 2.5mm (model space)
- **Arrow Size:** 2.5mm
- **Extension Lines:** 1.0mm offset from geometry
- **Units Display:** Match project units (mm or in)

---

## Export Standards

See `EXPORT_PIPELINE.md` for detailed export procedures.

**Key Points:**
- DXF: Layer names preserved, units specified
- STEP: 3D geometry only, units critical
- STL: Mesh export, resolution specified
- PDF: Paper space, scale maintained
- SVG: 2D only, layer colors preserved

---

## Drawing Scale

**Standard Scales:**
- 1:1 (Full scale - preferred)
- 1:10, 1:20, 1:50, 1:100 (Reduced scale)
- 10:1, 2:1, 5:1 (Enlarged scale)

**Note:** Always document scale in title block.

---

## Text Standards

- **Font:** Arial or similar sans-serif
- **Height:** 2.5mm (model space)
- **Width Factor:** 0.8 (condensed for readability)

---

## Hatching Patterns

**Standard Patterns:**
- Solid fill: Material indication
- ANSI31: Steel
- ANSI37: Concrete
- User-defined: Custom materials

---

## Revision Control

**File Naming:**
- `ProjectName_RevA.dxf`
- `ProjectName_RevB.dxf`
- Archive old revisions to `99_Archive\`

---

## Automation Compliance

All macros and scripts must:
1. Apply layer standards from `LAYER_STANDARD.json`
2. Follow export pipeline from `EXPORT_PIPELINE.md`
3. Document units and scale
4. Preserve layer structure in exports

---

## Updates

When standards change:
1. Update this file
2. Update `LAYER_STANDARD.json` if layers change
3. Write decision to brain (via MCP) as `type: constraint`
4. Update affected templates in `02_Templates\`

