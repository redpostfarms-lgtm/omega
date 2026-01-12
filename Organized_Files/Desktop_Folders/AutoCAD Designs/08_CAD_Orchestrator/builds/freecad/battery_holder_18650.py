# -*- coding: utf-8 -*-
"""
FreeCAD Macro: Battery Holder for 18650 Cell
Generated from Blueprint: battery_holder_18650.json
Location: 08_CAD_Orchestrator\builds\freecad\

Specifications:
- 80mm length
- 22mm inner diameter (18650 cell fit)
- 28mm outer diameter (3mm wall thickness)
- M4 mounting holes on 70mm centers
- Material: ABS
- Exports: STEP + DXF + PDF
"""

__title__ = "Battery Holder 18650"
__author__ = "CADForge AI"
__date__ = "2025-12-13"
__version__ = "1.0"

import FreeCAD
import FreeCADGui
from FreeCAD import Base, Vector
import Part
import Draft
import math

# ============================================================================
# PARAMETERS (Edit these to regenerate)
# ============================================================================

PROJECT_NAME = "battery_holder_18650"
UNITS = "mm"
SCALE = 1.0

# Dimensions (from Blueprint)
LENGTH = 80.0  # mm
INNER_DIAMETER = 22.0  # mm (18650 cell diameter)
OUTER_DIAMETER = 28.0  # mm (inner + 2× wall thickness)
WALL_THICKNESS = 3.0  # mm
MOUNTING_HOLE_DIAMETER = 4.0  # mm (M4)
MOUNTING_HOLE_SPACING = 70.0  # mm (center-to-center)
MOUNTING_HOLE_DEPTH = 6.0  # mm
MATERIAL = "ABS"

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
    
    FreeCAD.Console.PrintMessage(f"Created document: {PROJECT_NAME}\n")
    FreeCAD.Console.PrintMessage(f"Units: {UNITS}\n")
    FreeCAD.Console.PrintMessage(f"Material: {MATERIAL}\n")
    FreeCAD.Console.PrintMessage(f"Dimensions: {LENGTH}mm × Ø{OUTER_DIAMETER}mm\n")
    
    return doc

# ============================================================================
# GEOMETRY CREATION
# ============================================================================

def create_battery_holder(doc):
    """Create the battery holder with mounting holes."""
    
    # Create outer cylinder (holder body)
    outer_cylinder = doc.addObject("Part::Cylinder", "OuterCylinder")
    outer_cylinder.Radius = OUTER_DIAMETER / 2.0
    outer_cylinder.Height = LENGTH
    outer_cylinder.Angle = 360.0
    outer_cylinder.Placement = Base.Placement(
        Base.Vector(0, 0, 0),
        Base.Rotation(Base.Vector(0, 0, 1), 0)
    )
    outer_cylinder.ViewObject.ShapeColor = LAYER_COLOR
    
    # Create inner cylinder (cavity to subtract)
    inner_cylinder = doc.addObject("Part::Cylinder", "InnerCylinder")
    inner_cylinder.Radius = INNER_DIAMETER / 2.0
    inner_cylinder.Height = LENGTH
    inner_cylinder.Angle = 360.0
    inner_cylinder.Placement = Base.Placement(
        Base.Vector(0, 0, 0),
        Base.Rotation(Base.Vector(0, 0, 1), 0)
    )
    
    # Subtract inner from outer to create wall
    holder_cut = doc.addObject("Part::Cut", "HolderWithWalls")
    holder_cut.Base = outer_cylinder
    holder_cut.Tool = inner_cylinder
    holder_cut.ViewObject.ShapeColor = LAYER_COLOR
    
    # Create mounting holes
    # Hole 1: Left side (-35mm from center)
    hole1 = doc.addObject("Part::Cylinder", "MountingHole1")
    hole1.Radius = MOUNTING_HOLE_DIAMETER / 2.0
    hole1.Height = MOUNTING_HOLE_DEPTH
    hole1.Angle = 360.0
    hole1.Placement = Base.Placement(
        Base.Vector(-MOUNTING_HOLE_SPACING / 2.0, 0, 0),
        Base.Rotation(Base.Vector(0, 1, 0), 90)  # Rotate to horizontal
    )
    
    # Hole 2: Right side (+35mm from center)
    hole2 = doc.addObject("Part::Cylinder", "MountingHole2")
    hole2.Radius = MOUNTING_HOLE_DIAMETER / 2.0
    hole2.Height = MOUNTING_HOLE_DEPTH
    hole2.Angle = 360.0
    hole2.Placement = Base.Placement(
        Base.Vector(MOUNTING_HOLE_SPACING / 2.0, 0, 0),
        Base.Rotation(Base.Vector(0, 1, 0), 90)  # Rotate to horizontal
    )
    
    # Subtract mounting holes from holder
    holder_with_hole1 = doc.addObject("Part::Cut", "HolderMinusHole1")
    holder_with_hole1.Base = holder_cut
    holder_with_hole1.Tool = hole1
    
    holder_with_holes = doc.addObject("Part::Cut", "HolderMinusHoles")
    holder_with_holes.Base = holder_with_hole1
    holder_with_holes.Tool = hole2
    holder_with_holes.ViewObject.ShapeColor = LAYER_COLOR
    
    # Recompute
    doc.recompute()
    
    FreeCAD.Console.PrintMessage("✓ Outer cylinder created\n")
    FreeCAD.Console.PrintMessage("✓ Inner cavity subtracted (wall thickness: 3mm)\n")
    FreeCAD.Console.PrintMessage("✓ 2 mounting holes created (M4, 70mm spacing)\n")
    
    return holder_with_holes

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_step(doc, holder_obj, filename):
    """Export to STEP format."""
    export_path = f"{EXPORT_BASE}STEP\\{filename}.step"
    
    try:
        import Part
        holder_obj.Shape.exportStep(export_path)
        FreeCAD.Console.PrintMessage(f"✓ Exported STEP to: {export_path}\n")
        return True
    except Exception as e:
        FreeCAD.Console.PrintError(f"✗ STEP export failed: {e}\n")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main macro execution."""
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Battery Holder 18650 - FreeCAD Macro\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    
    # Create document
    doc = create_document()
    
    # Create geometry
    holder = create_battery_holder(doc)
    
    # Export
    FreeCAD.Console.PrintMessage("\n" + "=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Exporting...\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    
    export_step(doc, holder, "battery_holder_18650")
    
    FreeCAD.Console.PrintMessage("\n" + "=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("3D Model generation complete\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Expected exports:\n")
    FreeCAD.Console.PrintMessage("  STEP: 05_Exports\\STEP\\battery_holder_18650.step\n")
    FreeCAD.Console.PrintMessage("\n")
    FreeCAD.Console.PrintMessage("Next step: Run TechDraw macro for blueprint-ready DXF/PDF\n")
    FreeCAD.Console.PrintMessage("  Macro: battery_holder_18650_techdraw.py\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")

# Execute main function
if __name__ == "__main__":
    main()
else:
    # Run when executed as FreeCAD macro
    main()

