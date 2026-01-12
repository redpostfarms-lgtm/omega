# Title Block Template

## Overview

Title blocks are required for all blueprint-ready drawings (DXF/PDF exports).

---

## Template Location

**File:** `01_Standards\TITLE_BLOCK.svg` (to be created)

**Usage:** Referenced in: `08_CAD_Orchestrator\prompts\SYSTEM_PROMPT.md`

---

## Required Fields

### Standard Fields
- **Project Name:** From Blueprint.metadata.name
- **Drawn By:** "CADForge AI" (or actual designer name)
- **Date:** Current date (ISO format: YYYY-MM-DD)
- **Scale:** From Blueprint.views_2d.scale
- **Material:** From Blueprint (if specified)
- **Units:** From Blueprint.units.system (mm or in)
- **Revision:** From Blueprint.metadata.version

### Optional Fields
- **Drawing Number:** From Blueprint.metadata.name or custom
- **Sheet:** 1 of 1 (or sheet number if multi-sheet)
- **Checked By:** (if applicable)
- **Approved By:** (if applicable)

---

## FreeCAD TechDraw Integration

### Using Template
1. Create SVG template file: `01_Standards\TITLE_BLOCK.svg`
2. Reference in TechDraw macro:
   ```python
   page.Template = "01_Standards/TITLE_BLOCK.svg"
   ```

### Populating Fields
TechDraw templates use editable text fields:
- `<<TITLE>>` - Project name
- `<<DATE>>` - Current date
- `<<SCALE>>` - Drawing scale
- `<<MATERIAL>>` - Material specification

---

## Template Creation

### Option 1: Use FreeCAD Default
- FreeCAD includes default templates (A4_Landscape.svg, etc.)
- Can be customized

### Option 2: Create Custom Template
1. Open FreeCAD
2. TechDraw → Insert Template
3. Edit template in SVG editor
4. Save to: `01_Standards\TITLE_BLOCK.svg`

### Option 3: Use Existing Template
- Copy from company standard
- Place in `01_Standards\`
- Reference in macros

---

## Standards Compliance

Title blocks must:
- Match paper size (A4, A3, etc.)
- Include all required fields
- Use consistent formatting
- Be readable at print scale

---

## Updates

When title block changes:
1. Update template file
2. Update SYSTEM_PROMPT.md if field requirements change
3. Write change to brain as `type: constraint`

