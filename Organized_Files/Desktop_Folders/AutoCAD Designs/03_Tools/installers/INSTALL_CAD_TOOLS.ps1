# CAD Tools Installation Script
# This script PRINTS installation commands - it does NOT execute them automatically
# Run the printed commands in an elevated PowerShell terminal if needed

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  CAD Tools Installation Commands" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "NOTE: This script PRINTS commands only." -ForegroundColor Yellow
Write-Host "Copy and paste the commands below into an elevated PowerShell terminal." -ForegroundColor Yellow
Write-Host ""
Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  FreeCAD (3D Parametric Modeling)" -ForegroundColor Green
Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host ""
Write-Host "Command:" -ForegroundColor White
Write-Host "  winget install -e --id FreeCAD.FreeCAD" -ForegroundColor Yellow
Write-Host ""
Write-Host "What it does:" -ForegroundColor White
Write-Host "  - Installs FreeCAD (latest stable version)" -ForegroundColor Gray
Write-Host "  - Python macro API enabled by default" -ForegroundColor Gray
Write-Host "  - Automation templates in: 06_AutoCAD_Automation\freecad\" -ForegroundColor Gray
Write-Host ""
Write-Host "Verification:" -ForegroundColor White
Write-Host "  After install, verify: winget list FreeCAD.FreeCAD" -ForegroundColor Gray
Write-Host ""

Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  LibreCAD (2D Drafting - Fallback)" -ForegroundColor Green
Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host ""
Write-Host "Command:" -ForegroundColor White
Write-Host "  winget install -e --id LibreCAD.LibreCAD" -ForegroundColor Yellow
Write-Host ""
Write-Host "What it does:" -ForegroundColor White
Write-Host "  - Installs LibreCAD (2D drafting tool)" -ForegroundColor Gray
Write-Host "  - Limited automation support" -ForegroundColor Gray
Write-Host "  - Use as manual drafting fallback" -ForegroundColor Gray
Write-Host ""
Write-Host "Verification:" -ForegroundColor White
Write-Host "  After install, verify: winget list LibreCAD.LibreCAD" -ForegroundColor Gray
Write-Host ""

Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  QCAD (2D Drafting - Preferred for Scripting)" -ForegroundColor Green
Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installation Method: MANUAL (Windows MSI)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Steps:" -ForegroundColor White
Write-Host "  1. Visit: https://www.qcad.org/en/download" -ForegroundColor Gray
Write-Host "  2. Download Windows MSI installer" -ForegroundColor Gray
Write-Host "  3. Run installer with default settings" -ForegroundColor Gray
Write-Host "  4. ECMAScript API enabled by default" -ForegroundColor Gray
Write-Host ""
Write-Host "Why manual:" -ForegroundColor White
Write-Host "  QCAD does not have a winget package ID." -ForegroundColor Gray
Write-Host "  Official MSI installer is the recommended installation method." -ForegroundColor Gray
Write-Host ""
Write-Host "Automation templates in: 06_AutoCAD_Automation\qcad\" -ForegroundColor Gray
Write-Host ""

Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  Onshape (Cloud CAD - Optional)" -ForegroundColor Green
Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host ""
Write-Host "WARNING: Free plan documents are PUBLIC" -ForegroundColor Red
Write-Host ""
Write-Host "Installation:" -ForegroundColor White
Write-Host "  - Web-based: https://www.onshape.com" -ForegroundColor Gray
Write-Host "  - No local installation required" -ForegroundColor Gray
Write-Host "  - API documentation: 06_AutoCAD_Automation\onshape\api\" -ForegroundColor Gray
Write-Host ""
Write-Host "Important:" -ForegroundColor White
Write-Host "  Free plan documents are publicly accessible." -ForegroundColor Red
Write-Host "  Do NOT use for proprietary/confidential designs." -ForegroundColor Red
Write-Host ""

Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  Installation Notes" -ForegroundColor Green
Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host ""
Write-Host "Winget Behavior:" -ForegroundColor White
Write-Host "  - winget may prompt for package refinement" -ForegroundColor Gray
Write-Host "  - Use --accept-package-agreements if needed" -ForegroundColor Gray
Write-Host "  - Reference: https://learn.microsoft.com/en-us/windows/package-manager/winget/" -ForegroundColor Gray
Write-Host ""
Write-Host "Elevation:" -ForegroundColor White
Write-Host "  - Some installs may require Administrator privileges" -ForegroundColor Gray
Write-Host "  - Right-click PowerShell → Run as Administrator" -ForegroundColor Gray
Write-Host ""
Write-Host "Verification:" -ForegroundColor White
Write-Host "  After installation, verify tools are accessible:" -ForegroundColor Gray
Write-Host "    - FreeCAD: Start menu → FreeCAD" -ForegroundColor Gray
Write-Host "    - LibreCAD: Start menu → LibreCAD" -ForegroundColor Gray
Write-Host "    - QCAD: Start menu → QCAD" -ForegroundColor Gray
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Ready to Install" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Copy the commands above and run in an elevated PowerShell terminal." -ForegroundColor Yellow
Write-Host ""

