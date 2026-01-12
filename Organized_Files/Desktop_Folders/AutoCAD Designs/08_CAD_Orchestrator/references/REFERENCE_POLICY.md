# Reference Policy - Web Research for CAD Work

## Overview

When Cursor needs to gather reference information (dimensions, standards, tutorials), use web browsing responsibly.

---

## Safe Reference Sources

### Preferred Sources
- **Official Documentation:** Tool vendor docs (FreeCAD, QCAD, etc.)
- **Standards Organizations:** ISO, ANSI, DIN standards
- **CC-Licensed Content:** Creative Commons images/drawings
- **Public Domain:** Government standards, expired patents

### Acceptable Uses
- **Dimensions/Standards:** Look up standard bolt sizes, thread pitches
- **Tutorials:** Learn tool APIs, scripting conventions
- **Specifications:** Material properties, tolerance standards
- **Reference Images:** CC-licensed or public domain only

---

## What NOT to Do

❌ **Never copy proprietary drawings verbatim**
- Don't scrape copyrighted CAD files
- Don't reproduce trademarked designs
- Don't use proprietary images without permission

❌ **Never store copyrighted content in memory**
- Only store decisions/constraints derived from references
- Store "use M6 bolts per ISO 4014" not the actual drawing

❌ **Never bypass attribution**
- If using CC-licensed content, attribute properly
- Document source of standards/specifications

---

## Reference Workflow

1. **Identify Need:** What information is needed?
2. **Find Source:** Official docs, standards, CC-licensed content
3. **Extract Facts:** Dimensions, standards, specifications
4. **Store Decision:** Write to brain as constraint/decision (not raw content)
5. **Document Source:** Note where information came from

---

## Example: Safe Reference Use

**Need:** Standard bolt pattern for 55-gallon drum

**Safe Approach:**
1. Look up ISO/ANSI standards for drum dimensions
2. Extract: "Standard 55-gallon drum diameter: 584mm"
3. Store in brain: `type: constraint, content: "55-gallon drum diameter: 584mm per ISO standard"`
4. Use in Blueprint parameters

**Unsafe Approach:**
1. Scrape proprietary drum manufacturer CAD file
2. Copy entire drawing
3. Store raw geometry in memory

---

## Browser Tool Usage

When using Cursor's Browser tool:

- **Purpose:** Gather specifications, standards, API docs
- **Output:** Facts and decisions, not raw content
- **Storage:** Write derived constraints to brain, not scraped content

---

## Attribution

When referencing external sources:
- Document source in Blueprint metadata
- Note standard/specification number
- Include date of reference

---

## Updates

If reference policy changes:
1. Update this file
2. Write change to brain as `type: constraint`
3. Update affected automation scripts

