# -*- coding: utf-8 -*-
"""
FreeCAD Macro: Parametric Box with Lid
Generated from Blueprint: parametric_box_with_lid.json
Location: 08_CAD_Orchestrator\builds\freecad\

Specifications:
- 12in × 8in × 6in outer dimensions
- 1/8in (0.125in) wall thickness
- 4 corner bolt holes (0.25in diameter, 0.5in depth)
- Lid included
- Exports: STEP + DXF
"""

__title__ = "Parametric Box with Lid"
__author__ = "AutoCAD Designs"
__date__ = "2025-12-13"
__version__ = "1.0"

import FreeCAD
import FreeCADGui
from FreeCAD import Base, Vector
import Part
import Draft
import math

# ============================================================================
# CONFIGURATION (from Blueprint)
# ============================================================================

PROJECT_NAME = "parametric_box_with_lid"
UNITS = "in"  # Inches (converted to mm for FreeCAD)
SCALE = 1.0

# Parameters (in inches, converted to mm)
INCH_TO_MM = 25.4
LENGTH = 12.0 * INCH_TO_MM  # 304.8 mm
WIDTH = 8.0 * INCH_TO_MM     # 203.2 mm
HEIGHT = 6.0 * INCH_TO_MM    # 152.4 mm
WALL_THICKNESS = 0.125 * INCH_TO_MM  # 3.175 mm
BOLT_HOLE_DIAMETER = 0.25 * INCH_TO_MM  # 6.35 mm
BOLT_HOLE_DEPTH = 0.5 * INCH_TO_MM  # 12.7 mm
CORNER_OFFSET = 0.5 * INCH_TO_MM  # 12.7 mm

# Layer standards (M-BOLT: Orange)
LAYER_COLOR = (1.0, 0.5, 0.0)  # Orange (RGB normalized)

# Export paths
EXPORT_BASE = "C:\\Users\\Drakalich\\Desktop\\AutoCAD Designs\\05_Exports\\"

# ============================================================================
# DOCUMENT SETUP
# ============================================================================

def create_document():
    """Create a new FreeCAD document with project settings."""
    doc = FreeCAD.newDocument(PROJECT_NAME)
    
    # Set units to inches (FreeCAD internal: 1 = 1mm, so we work in mm)
    # User sees inches in Blueprint, but FreeCAD works in mm
    FreeCAD.Console.PrintMessage(f"Created document: {PROJECT_NAME}\n")
    FreeCAD.Console.PrintMessage(f"Units: {UNITS} (working in mm internally)\n")
    FreeCAD.Console.PrintMessage(f"Dimensions: {LENGTH/INCH_TO_MM}\" × {WIDTH/INCH_TO_MM}\" × {HEIGHT/INCH_TO_MM}\"\n")
    
    return doc

# ============================================================================
# GEOMETRY CREATION
# ============================================================================

def create_box_with_lid(doc):
    """Create the parametric box with lid and bolt holes."""
    
    # Create outer box
    outer_box = doc.addObject("Part::Box", "OuterBox")
    outer_box.Length = LENGTH
    outer_box.Width = WIDTH
    outer_box.Height = HEIGHT
    outer_box.Placement = Base.Placement(Base.Vector(0, 0, 0), Base.Rotation())
    outer_box.ViewObject.ShapeColor = LAYER_COLOR
    
    # Create inner cavity (to subtract for walls)
    inner_box = doc.addObject("Part::Box", "InnerBox")
    inner_box.Length = LENGTH - (2 * WALL_THICKNESS)
    inner_box.Width = WIDTH - (2 * WALL_THICKNESS)
    inner_box.Height = HEIGHT - WALL_THICKNESS  # Bottom wall remains
    inner_box.Placement = Base.Placement(
        Base.Vector(WALL_THICKNESS, WALL_THICKNESS, WALL_THICKNESS),
        Base.Rotation()
    )
    
    # Subtract inner from outer to create walls
    box_cut = doc.addObject("Part::Cut", "BoxWithWalls")
    box_cut.Base = outer_box
    box_cut.Tool = inner_box
    box_cut.ViewObject.ShapeColor = LAYER_COLOR
    
    # Create lid
    lid = doc.addObject("Part::Box", "Lid")
    lid.Length = LENGTH
    lid.Width = WIDTH
    lid.Height = WALL_THICKNESS
    lid.Placement = Base.Placement(
        Base.Vector(0, 0, HEIGHT),
        Base.Rotation()
    )
    lid.ViewObject.ShapeColor = LAYER_COLOR
    
    # Create 4 corner bolt holes
    bolt_holes = []
    positions = [
        (CORNER_OFFSET, CORNER_OFFSET, 0),  # Front-left
        (LENGTH - CORNER_OFFSET, CORNER_OFFSET, 0),  # Front-right
        (CORNER_OFFSET, WIDTH - CORNER_OFFSET, 0),  # Back-left
        (LENGTH - CORNER_OFFSET, WIDTH - CORNER_OFFSET, 0)  # Back-right
    ]
    
    for i, pos in enumerate(positions):
        hole = doc.addObject("Part::Cylinder", f"BoltHole_{i+1}")
        hole.Radius = BOLT_HOLE_DIAMETER / 2.0
        hole.Height = BOLT_HOLE_DEPTH
        hole.Placement = Base.Placement(
            Base.Vector(pos[0], pos[1], pos[2]),
            Base.Rotation(Base.Vector(0, 0, 1), 0)
        )
        bolt_holes.append(hole)
    
    # Subtract bolt holes from box
    box_with_holes = box_cut
    for hole in bolt_holes:
        new_cut = doc.addObject("Part::Cut", f"BoxMinusHole_{hole.Label}")
        new_cut.Base = box_with_holes
        new_cut.Tool = hole
        box_with_holes = new_cut
    
    # Final box (with walls and holes)
    final_box = box_with_holes
    final_box.ViewObject.ShapeColor = LAYER_COLOR
    
    # Recompute
    doc.recompute()
    
    FreeCAD.Console.PrintMessage("✓ Box with walls created\n")
    FreeCAD.Console.PrintMessage("✓ Lid created\n")
    FreeCAD.Console.PrintMessage("✓ 4 corner bolt holes created\n")
    
    return final_box, lid

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_step(doc, box_obj, lid_obj, filename):
    """Export to STEP format."""
    export_path = f"{EXPORT_BASE}STEP\\{filename}.step"
    
    try:
        # Combine box and lid into a compound for export
        import Part
        compound = Part.Compound([box_obj.Shape, lid_obj.Shape])
        compound.exportStep(export_path)
        FreeCAD.Console.PrintMessage(f"✓ Exported STEP to: {export_path}\n")
        return True
    except Exception as e:
        FreeCAD.Console.PrintError(f"✗ STEP export failed: {e}\n")
        return False

def export_dxf(doc, filename):
    """Export to DXF format (2D views)."""
    export_path = f"{EXPORT_BASE}DXF\\{filename}.dxf"
    
    try:
        # FreeCAD DXF export requires Draft workbench
        # Export top view as DXF
        import Draft
        
        # Get all Part objects
        part_objects = [obj for obj in doc.Objects if hasattr(obj, "Shape")]
        
        if part_objects:
            # Create 2D projection (top view)
            # Note: FreeCAD DXF export may need additional setup
            # This is a simplified approach
            FreeCAD.Console.PrintMessage(f"Note: DXF export may require Draft workbench setup\n")
            FreeCAD.Console.PrintMessage(f"Target: {export_path}\n")
            FreeCAD.Console.PrintMessage(f"Manual export: File → Export → DXF\n")
            return True
    except Exception as e:
        FreeCAD.Console.PrintError(f"✗ DXF export note: {e}\n")
        FreeCAD.Console.PrintMessage(f"Use FreeCAD GUI: File → Export → DXF\n")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main macro execution."""
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Parametric Box with Lid - FreeCAD Macro\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    
    # Create document
    doc = create_document()
    
    # Create geometry
    box, lid = create_box_with_lid(doc)
    
    # Export
    FreeCAD.Console.PrintMessage("\n" + "=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Exporting...\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    
    export_step(doc, box, lid, "parametric_box_with_lid")
    export_dxf(doc, "parametric_box_with_lid")
    
    FreeCAD.Console.PrintMessage("\n" + "=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("3D Model generation complete\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Expected exports:\n")
    FreeCAD.Console.PrintMessage("  STEP: 05_Exports\\STEP\\parametric_box_with_lid.step\n")
    FreeCAD.Console.PrintMessage("\n")
    FreeCAD.Console.PrintMessage("Next step: Run TechDraw macro for blueprint-ready DXF/PDF\n")
    FreeCAD.Console.PrintMessage("  Macro: parametric_box_with_lid_techdraw.py\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")

# Execute main function
if __name__ == "__main__":
    main()
else:
    # Run when executed as FreeCAD macro
    main()

