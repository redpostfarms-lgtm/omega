@echo off
REM Save UI Images - Instructions
echo ========================================
echo   SAVE UI IMAGES FOR UI USE
echo ========================================
echo.

echo Please save the following images:
echo.

echo 1. Omega Logo (Red Omega with Gold Wreath):
echo    - File: omega_logo_red_gold_wreath.png
echo    - Location: images\ folder
echo    - Usage: BIOS boot logo, desktop icon, control panel header
echo.

echo 2. Control Panel UI Design:
echo    - File: control_panel_ui_design.png
echo    - Location: images\ or ui_designs\ folder
echo    - Usage: Control panel UI layout reference
echo    - NOTE: Blue outline shows central section (THIS IS BEING USED)
echo.

echo 3. Development Environment Screenshot:
echo    - File: development_environment_screenshot.png
echo    - Location: docs\ or images\ folder
echo    - Usage: Documentation and UI reference
echo    - NOTE: Marked areas show what is being used
echo.

echo ========================================
echo   IMAGE LOCATIONS
echo ========================================
echo.

if not exist "images" (
    echo Creating images folder...
    mkdir images
)

if not exist "ui_designs" (
    echo Creating ui_designs folder...
    mkdir ui_designs
)

if not exist "docs" (
    echo Creating docs folder...
    mkdir docs
)

echo.
echo Folders created: images\, ui_designs\, docs\
echo.
echo Please save the images to:
echo   1. images\omega_logo_red_gold_wreath.png
echo   2. images\control_panel_ui_design.png (or ui_designs\)
echo   3. docs\development_environment_screenshot.png (or images\)
echo.

pause
