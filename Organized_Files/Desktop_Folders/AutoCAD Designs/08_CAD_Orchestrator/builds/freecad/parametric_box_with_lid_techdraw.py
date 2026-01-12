# -*- coding: utf-8 -*-
"""
FreeCAD TechDraw Macro: Parametric Box with Lid - Drawing Generation
Generated from Blueprint: parametric_box_with_lid.json
Location: 08_CAD_Orchestrator\builds\freecad\

This macro creates TechDraw views from the 3D model for blueprint-ready DXF/PDF export.
Run this AFTER the main 3D model macro has been executed.
"""

__title__ = "Parametric Box with Lid - TechDraw"
__author__ = "AutoCAD Designs"
__date__ = "2025-12-13"
__version__ = "1.0"

import FreeCAD
import FreeCADGui
from FreeCAD import Base, Vector
import TechDraw
import Part

# ============================================================================
# CONFIGURATION (from Blueprint)
# ============================================================================

PROJECT_NAME = "parametric_box_with_lid"
PAPER_SIZE = "A4"  # or from Blueprint.exports.pdf.paper_size
SCALE = 1.0  # from Blueprint.views_2d.scale

# Export paths
EXPORT_BASE = "C:\\Users\\Drakalich\\Desktop\\AutoCAD Designs\\05_Exports\\"

# ============================================================================
# TECHDRAW CREATION
# ============================================================================

def create_techdraw_page(doc, paper_size="A4"):
    """Create a TechDraw page for the drawing."""
    
    # Create page
    page = doc.addObject("TechDraw::DrawPage", "DrawingPage")
    page.Template = "A4_Landscape.svg"  # FreeCAD default template
    
    # Set scale
    page.Scale = SCALE
    
    FreeCAD.Console.PrintMessage(f"✓ Created TechDraw page: {paper_size}\n")
    
    return page

def create_views(doc, page, box_obj, lid_obj):
    """Create TechDraw views from 3D model."""
    
    views = []
    
    # Top View
    top_view = doc.addObject("TechDraw::DrawViewPart", "TopView")
    top_view.Source = [box_obj, lid_obj]
    top_view.Direction = (0, 0, 1)  # Looking down Z-axis
    top_view.Rotation = 0
    top_view.Scale = SCALE
    page.addView(top_view)
    views.append(top_view)
    FreeCAD.Console.PrintMessage("✓ Created Top View\n")
    
    # Front View
    front_view = doc.addObject("TechDraw::DrawViewPart", "FrontView")
    front_view.Source = [box_obj, lid_obj]
    front_view.Direction = (0, -1, 0)  # Looking along Y-axis
    front_view.Rotation = 0
    front_view.Scale = SCALE
    page.addView(front_view)
    views.append(front_view)
    FreeCAD.Console.PrintMessage("✓ Created Front View\n")
    
    # Side View
    side_view = doc.addObject("TechDraw::DrawViewPart", "SideView")
    side_view.Source = [box_obj, lid_obj]
    side_view.Direction = (-1, 0, 0)  # Looking along X-axis
    side_view.Rotation = 0
    side_view.Scale = SCALE
    page.addView(side_view)
    views.append(side_view)
    FreeCAD.Console.PrintMessage("✓ Created Side View\n")
    
    # Isometric View (optional, for reference)
    iso_view = doc.addObject("TechDraw::DrawViewPart", "IsometricView")
    iso_view.Source = [box_obj, lid_obj]
    iso_view.Direction = (1, 1, 1)  # Isometric direction
    iso_view.Rotation = 0
    iso_view.Scale = SCALE * 0.5  # Smaller for reference
    page.addView(iso_view)
    views.append(iso_view)
    FreeCAD.Console.PrintMessage("✓ Created Isometric View\n")
    
    return views

def add_dimensions(doc, page, views):
    """Add dimensions to views."""
    
    # Get top view for dimensions
    top_view = views[0]  # Top view
    
    # Note: TechDraw dimensions require specific setup
    # This is a placeholder - actual dimension creation may need manual setup
    # or more complex geometry analysis
    
    FreeCAD.Console.PrintMessage("Note: Dimensions may need manual addition in TechDraw\n")
    FreeCAD.Console.PrintMessage("Recommended: Add dimensions in TechDraw GUI after views are created\n")
    
    # Example dimension (if geometry allows):
    # dim_length = doc.addObject("TechDraw::DrawViewDimension", "LengthDimension")
    # dim_length.Type = "Distance"
    # dim_length.References2D = [(top_view, "Edge1"), (top_view, "Edge2")]
    # page.addView(dim_length)

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_dxf_from_techdraw(page, filename):
    """Export TechDraw page to DXF format."""
    export_path = f"{EXPORT_BASE}DXF\\{filename}.dxf"
    
    try:
        # TechDraw DXF export
        page.exportPageAsDXF(export_path)
        FreeCAD.Console.PrintMessage(f"✓ Exported DXF to: {export_path}\n")
        return True
    except Exception as e:
        FreeCAD.Console.PrintError(f"✗ DXF export failed: {e}\n")
        FreeCAD.Console.PrintMessage("Try: Select page -> File -> Export -> DXF\n")
        return False

def export_pdf_from_techdraw(page, filename):
    """Export TechDraw page to PDF format."""
    export_path = f"{EXPORT_BASE}PDF\\{filename}.pdf"
    
    try:
        # TechDraw PDF export
        page.exportPageAsPdf(export_path)
        FreeCAD.Console.PrintMessage(f"✓ Exported PDF to: {export_path}\n")
        return True
    except Exception as e:
        FreeCAD.Console.PrintError(f"✗ PDF export failed: {e}\n")
        FreeCAD.Console.PrintMessage("Try: Select page -> File -> Export -> PDF\n")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main TechDraw macro execution."""
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("TechDraw Drawing Generation\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    
    # Get active document (should have 3D model from previous macro)
    doc = FreeCAD.ActiveDocument
    if doc is None:
        FreeCAD.Console.PrintError("✗ No active document. Run 3D model macro first.\n")
        return
    
    # Find box and lid objects
    box_obj = None
    lid_obj = None
    
    for obj in doc.Objects:
        if "Box" in obj.Label and "Cut" in obj.TypeId:
            box_obj = obj
        elif "Lid" in obj.Label:
            lid_obj = obj
    
    if box_obj is None or lid_obj is None:
        FreeCAD.Console.PrintError("✗ Box or Lid objects not found. Run 3D model macro first.\n")
        return
    
    FreeCAD.Console.PrintMessage("✓ Found 3D model objects\n")
    
    # Create TechDraw page
    page = create_techdraw_page(doc, PAPER_SIZE)
    
    # Create views
    views = create_views(doc, page, box_obj, lid_obj)
    
    # Add dimensions (placeholder - may need manual setup)
    add_dimensions(doc, page, views)
    
    # Recompute
    doc.recompute()
    
    # Export
    FreeCAD.Console.PrintMessage("\n" + "=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Exporting...\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    
    export_dxf_from_techdraw(page, "parametric_box_with_lid")
    export_pdf_from_techdraw(page, "parametric_box_with_lid")
    
    FreeCAD.Console.PrintMessage("\n" + "=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("TechDraw generation complete\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Expected exports:\n")
    FreeCAD.Console.PrintMessage("  DXF: 05_Exports\\DXF\\parametric_box_with_lid.dxf\n")
    FreeCAD.Console.PrintMessage("  PDF: 05_Exports\\PDF\\parametric_box_with_lid.pdf\n")
    FreeCAD.Console.PrintMessage("\nNote: You may need to add dimensions manually in TechDraw GUI\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")

# Execute main function
if __name__ == "__main__":
    main()
else:
    # Run when executed as FreeCAD macro
    main()

