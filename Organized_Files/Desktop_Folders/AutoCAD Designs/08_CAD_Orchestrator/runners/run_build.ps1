# CAD Build Runner
# Selects a blueprint and orchestrates the build process

param(
    [Parameter(Mandatory=$true)]
    [string]$BlueprintFile
)

$ErrorActionPreference = "Stop"

# Paths
$BlueprintPath = Join-Path "08_CAD_Orchestrator\blueprints" $BlueprintFile
$BuildsPath = "08_CAD_Orchestrator\builds"
$ExportsPath = "05_Exports"
$LogsPath = "08_CAD_Orchestrator\logs"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  CAD Build Runner" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if blueprint exists
if (-not (Test-Path $BlueprintPath)) {
    Write-Host "ERROR: Blueprint file not found: $BlueprintPath" -ForegroundColor Red
    exit 1
}

Write-Host "Blueprint: $BlueprintFile" -ForegroundColor Green
Write-Host ""

# Read blueprint
try {
    $blueprint = Get-Content $BlueprintPath | ConvertFrom-Json
    Write-Host "Blueprint loaded: $($blueprint.metadata.name)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to parse blueprint JSON" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Determine build type
$geometryType = $blueprint.geometry.type
Write-Host "Geometry type: $geometryType" -ForegroundColor Cyan
Write-Host ""

# Print build commands (do not execute automatically)
Write-Host "----------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "  BUILD COMMANDS (Copy and run manually)" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------" -ForegroundColor Yellow
Write-Host ""

if ($geometryType -eq "3d" -or $geometryType -eq "mixed") {
    $freecadMacro = Join-Path $BuildsPath "freecad\$($blueprint.metadata.name).py"
    $techdrawMacro = Join-Path $BuildsPath "freecad\$($blueprint.metadata.name)_techdraw.py"
    
    Write-Host "FreeCAD 3D Model Macro:" -ForegroundColor White
    Write-Host "  1. Open FreeCAD" -ForegroundColor Gray
    Write-Host "  2. Macro -> Macros..." -ForegroundColor Gray
    Write-Host "  3. Load: $freecadMacro" -ForegroundColor Gray
    Write-Host "  4. Execute macro (creates 3D model)" -ForegroundColor Gray
    Write-Host ""
    
    # Check if TechDraw macro exists (for DXF/PDF)
    if ($blueprint.exports.dxf.enabled -or $blueprint.exports.pdf.enabled) {
        if (Test-Path $techdrawMacro) {
            Write-Host "FreeCAD TechDraw Macro (for DXF/PDF):" -ForegroundColor White
            Write-Host "  1. After 3D model is created, run TechDraw macro" -ForegroundColor Gray
            Write-Host "  2. Macro -> Macros..." -ForegroundColor Gray
            Write-Host "  3. Load: $techdrawMacro" -ForegroundColor Gray
            Write-Host "  4. Execute macro (creates blueprint-ready DXF/PDF)" -ForegroundColor Gray
            Write-Host ""
        }
    }
}

if ($geometryType -eq "2d" -or $geometryType -eq "mixed") {
    $qcadScript = Join-Path $BuildsPath "qcad\$($blueprint.metadata.name).js"
    Write-Host "QCAD Script:" -ForegroundColor White
    Write-Host "  1. Open QCAD" -ForegroundColor Gray
    Write-Host "  2. Misc -> Scripts -> Run Script..." -ForegroundColor Gray
    Write-Host "  3. Load: $qcadScript" -ForegroundColor Gray
    Write-Host "  4. Execute script" -ForegroundColor Gray
    Write-Host ""
}

# Export targets
Write-Host "----------------------------------------------------------------" -ForegroundColor Yellow
Write-Host "  EXPECTED EXPORTS" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------" -ForegroundColor Yellow
Write-Host ""

if ($blueprint.exports.dxf.enabled) {
    $dxfPath = Join-Path $ExportsPath "DXF\$($blueprint.exports.dxf.filename)"
    Write-Host "DXF: $dxfPath" -ForegroundColor Green
}

if ($blueprint.exports.step.enabled) {
    $stepPath = Join-Path $ExportsPath "STEP\$($blueprint.exports.step.filename)"
    Write-Host "STEP: $stepPath" -ForegroundColor Green
}

if ($blueprint.exports.stl.enabled) {
    $stlPath = Join-Path $ExportsPath "STL\$($blueprint.exports.stl.filename)"
    Write-Host "STL: $stlPath" -ForegroundColor Green
}

if ($blueprint.exports.pdf.enabled) {
    $pdfPath = Join-Path $ExportsPath "PDF\$($blueprint.exports.pdf.filename)"
    Write-Host "PDF: $pdfPath" -ForegroundColor Green
}

if ($blueprint.exports.svg.enabled) {
    $svgPath = Join-Path $ExportsPath "SVG\$($blueprint.exports.svg.filename)"
    Write-Host "SVG: $svgPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Build plan complete. Run commands above to execute." -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
