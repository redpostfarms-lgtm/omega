# -*- coding: utf-8 -*-
"""
FreeCAD TechDraw Macro: Battery Holder 18650 - Drawing Generation
Generated from Blueprint: battery_holder_18650.json
Location: 08_CAD_Orchestrator\builds\freecad\

This macro creates TechDraw views from the 3D model for blueprint-ready DXF/PDF export.
Run this AFTER the main 3D model macro has been executed.
"""

__title__ = "Battery Holder 18650 - TechDraw"
__author__ = "CADForge AI"
__date__ = "2025-12-13"
__version__ = "1.0"

# FreeCAD Python API imports
# These modules are only available when running inside FreeCAD's Python interpreter
# The type: ignore comments suppress linter warnings for modules that exist at runtime
import FreeCAD  # type: ignore
import FreeCADGui  # type: ignore
from FreeCAD import Base, Vector  # type: ignore
import TechDraw  # type: ignore
import Part  # type: ignore
from datetime import datetime

# ============================================================================
# CONFIGURATION (from Blueprint)
# ============================================================================

PROJECT_NAME = "battery_holder_18650"
PAPER_SIZE = "A4"
SCALE = 1.0
MATERIAL = "ABS"

# Title block fields
TITLE = "Battery Holder 18650"
DRAWN_BY = "CADForge AI"
DATE = datetime.now().strftime("%Y-%m-%d")
SCALE_VALUE = "1:1"
MATERIAL_SPEC = "ABS"

# Export paths
EXPORT_BASE = "C:\\Users\\Drakalich\\Desktop\\AutoCAD Designs\\05_Exports\\"

# Convert to Path object and ensure export directories exist
from pathlib import Path
EXPORT_BASE_PATH = Path(EXPORT_BASE)
(EXPORT_BASE_PATH / "DXF").mkdir(parents=True, exist_ok=True)
(EXPORT_BASE_PATH / "PDF").mkdir(parents=True, exist_ok=True)

# ============================================================================
# TECHDRAW CREATION
# ============================================================================

def create_techdraw_page(doc, paper_size="A4"):
    """Create a TechDraw page for the drawing."""
    
    # Create page
    page = doc.addObject("TechDraw::DrawPage", "DrawingPage")
    # Use default template (can be customized to use 01_Standards\TITLE_BLOCK.svg)
    page.Template = "A4_Landscape.svg"  # FreeCAD default template
    
    # Set scale
    page.Scale = SCALE
    
    FreeCAD.Console.PrintMessage(f"✓ Created TechDraw page: {paper_size}\n")
    FreeCAD.Console.PrintMessage(f"  Title: {TITLE}\n")
    FreeCAD.Console.PrintMessage(f"  Drawn by: {DRAWN_BY}\n")
    FreeCAD.Console.PrintMessage(f"  Date: {DATE}\n")
    FreeCAD.Console.PrintMessage(f"  Material: {MATERIAL_SPEC}\n")
    
    return page

def create_views(doc, page, holder_obj):
    """Create TechDraw views from 3D model."""
    
    views = []
    
    # Top View (shows circular cross-section with mounting holes)
    top_view = doc.addObject("TechDraw::DrawViewPart", "TopView")
    top_view.Source = [holder_obj]
    top_view.Direction = (0, 0, 1)  # Looking down Z-axis
    top_view.Rotation = 0
    top_view.Scale = SCALE
    page.addView(top_view)
    views.append(top_view)
    FreeCAD.Console.PrintMessage("✓ Created Top View\n")
    
    # Front View (shows length and diameter)
    front_view = doc.addObject("TechDraw::DrawViewPart", "FrontView")
    front_view.Source = [holder_obj]
    front_view.Direction = (0, -1, 0)  # Looking along Y-axis
    front_view.Rotation = 0
    front_view.Scale = SCALE
    page.addView(front_view)
    views.append(front_view)
    FreeCAD.Console.PrintMessage("✓ Created Front View\n")
    
    # Side View (shows length and mounting hole positions)
    side_view = doc.addObject("TechDraw::DrawViewPart", "SideView")
    side_view.Source = [holder_obj]
    side_view.Direction = (-1, 0, 0)  # Looking along X-axis
    side_view.Rotation = 0
    side_view.Scale = SCALE
    page.addView(side_view)
    views.append(side_view)
    FreeCAD.Console.PrintMessage("✓ Created Side View\n")
    
    # Isometric View (optional, for reference)
    iso_view = doc.addObject("TechDraw::DrawViewPart", "IsometricView")
    iso_view.Source = [holder_obj]
    iso_view.Direction = (1, 1, 1)  # Isometric direction
    iso_view.Rotation = 0
    iso_view.Scale = SCALE * 0.5  # Smaller for reference
    page.addView(iso_view)
    views.append(iso_view)
    FreeCAD.Console.PrintMessage("✓ Created Isometric View\n")
    
    return views

def add_dimensions(doc, page, views):
    """Add dimensions to views (placeholder - may need manual setup)."""
    
    # Note: TechDraw dimensions require specific geometry references
    # This is a placeholder - actual dimension creation may need manual setup
    # or more complex geometry analysis
    
    FreeCAD.Console.PrintMessage("Note: Dimensions may need manual addition in TechDraw\n")
    FreeCAD.Console.PrintMessage("Recommended dimensions from Blueprint:\n")
    FreeCAD.Console.PrintMessage("  - Inner diameter: Ø22mm\n")
    FreeCAD.Console.PrintMessage("  - Outer diameter: Ø28mm\n")
    FreeCAD.Console.PrintMessage("  - Length: 80mm\n")
    FreeCAD.Console.PrintMessage("  - Wall thickness: 3mm\n")
    FreeCAD.Console.PrintMessage("  - Mounting hole spacing: 70mm\n")
    FreeCAD.Console.PrintMessage("  - Mounting hole diameter: M4 (Ø4mm)\n")

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_dxf_from_techdraw(page, filename):
    """Export TechDraw page to DXF format."""
    # Export directories already created at module load
    export_path = str(EXPORT_BASE_PATH / "DXF" / f"{filename}.dxf")
    
    try:
        # TechDraw DXF export - use correct method name
        # Method may vary by FreeCAD version: exportPageAsDXF or exportDXF
        if hasattr(page, 'exportPageAsDXF'):
            page.exportPageAsDXF(export_path)
        elif hasattr(page, 'exportDXF'):
            page.exportDXF(export_path)
        else:
            # Fallback: use FreeCAD's export function
            import TechDraw  # type: ignore
            TechDraw.writeDXF(page, export_path)
        
        FreeCAD.Console.PrintMessage(f"✓ Exported DXF to: {export_path}\n")
        return True
    except Exception as e:
        FreeCAD.Console.PrintError(f"✗ DXF export failed: {e}\n")
        FreeCAD.Console.PrintMessage("Try: Select page -> File -> Export -> DXF\n")
        return False

def export_pdf_from_techdraw(page, filename):
    """Export TechDraw page to PDF format."""
    # Export directories already created at module load
    export_path = str(EXPORT_BASE_PATH / "PDF" / f"{filename}.pdf")
    
    try:
        # TechDraw PDF export - use correct method name
        # Method may vary by FreeCAD version: exportPageAsPdf or exportPdf
        if hasattr(page, 'exportPageAsPdf'):
            page.exportPageAsPdf(export_path)
        elif hasattr(page, 'exportPdf'):
            page.exportPdf(export_path)
        else:
            # Fallback: use FreeCAD's export function
            import TechDraw  # type: ignore
            TechDraw.writePDF(page, export_path)
        
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
    FreeCAD.Console.PrintMessage("TechDraw Drawing Generation - Battery Holder 18650\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    
    # Get active document (should have 3D model from previous macro)
    doc = FreeCAD.ActiveDocument
    if doc is None:
        FreeCAD.Console.PrintError("✗ No active document. Run 3D model macro first.\n")
        return
    
    # Find holder object
    holder_obj = None
    
    for obj in doc.Objects:
        if "Holder" in obj.Label and "Cut" in obj.TypeId:
            holder_obj = obj
            break
    
    if holder_obj is None:
        FreeCAD.Console.PrintError("✗ Holder object not found. Run 3D model macro first.\n")
        return
    
    FreeCAD.Console.PrintMessage("✓ Found 3D model object\n")
    
    # Create TechDraw page
    page = create_techdraw_page(doc, PAPER_SIZE)
    
    # Create views
    views = create_views(doc, page, holder_obj)
    
    # Add dimensions (placeholder - may need manual setup)
    add_dimensions(doc, page, views)
    
    # Recompute
    doc.recompute()
    
    # Export
    FreeCAD.Console.PrintMessage("\n" + "=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Exporting...\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    
    export_dxf_from_techdraw(page, "battery_holder_18650")
    export_pdf_from_techdraw(page, "battery_holder_18650")
    
    FreeCAD.Console.PrintMessage("\n" + "=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("TechDraw generation complete\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")
    FreeCAD.Console.PrintMessage("Expected exports:\n")
    FreeCAD.Console.PrintMessage("  DXF: 05_Exports\\DXF\\battery_holder_18650.dxf\n")
    FreeCAD.Console.PrintMessage("  PDF: 05_Exports\\PDF\\battery_holder_18650.pdf\n")
    FreeCAD.Console.PrintMessage("\nNote: You may need to add dimensions manually in TechDraw GUI\n")
    FreeCAD.Console.PrintMessage("=" * 60 + "\n")

# Execute main function
if __name__ == "__main__":
    main()
else:
    # Run when executed as FreeCAD macro
    main()

