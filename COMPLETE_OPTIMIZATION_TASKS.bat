@echo off
REM Complete Optimization Tasks - Agent Council Recommendations
echo ========================================
echo   COMPLETE OPTIMIZATION TASKS
echo   Agent Council Recommendations
echo ========================================
echo.

cd /d "%~dp0"

echo Agent Council Analysis:
echo   - Critical Path: Save Omega Logo Image first
echo   - Parallel Task: Save Control Panel UI Design
echo   - Sequential: Create icons/logos after image saved
echo.
echo.

echo [STEP 1] Check for logo image...
if exist "images\omega_logo_red_gold_wreath.png" (
    echo [OK] Logo image found: images\omega_logo_red_gold_wreath.png
    set LOGO_EXISTS=1
) else if exist "images\omega_logo_red_gold_wreath.bmp" (
    echo [OK] Logo image found: images\omega_logo_red_gold_wreath.bmp
    set LOGO_EXISTS=1
) else (
    echo [!] Logo image not found - Manual save required
    echo     Please save: images\omega_logo_red_gold_wreath.png
    set LOGO_EXISTS=0
)

echo.
echo [STEP 2] Check for control panel UI design...
if exist "images\control_panel_ui_design.png" (
    echo [OK] Control panel UI design found
) else (
    echo [!] Control panel UI design not found - Manual save required
    echo     Please save: images\control_panel_ui_design.png
)

echo.
echo [STEP 3] Create BIOS boot logo (if logo image exists)...
if %LOGO_EXISTS%==1 (
    if exist "boot_logo\omega_logo.bmp" (
        echo [OK] BIOS boot logo already exists
    ) else (
        echo [Creating BIOS boot logo...]
        python create_omega_boot_logo.py
    )
) else (
    echo [!] Skipped - Logo image required first
)

echo.
echo [STEP 4] Create desktop icon (if logo image exists)...
if %LOGO_EXISTS%==1 (
    if exist "omega_icon.ico" (
        echo [OK] Desktop icon already exists
    ) else (
        echo [Creating desktop icon...]
        python CREATE_OMEGA_ICON.py
    )
) else (
    echo [!] Skipped - Logo image required first
)

echo.
echo [STEP 5] Update desktop shortcut icon (if icon exists)...
if exist "omega_icon.ico" (
    if exist "%USERPROFILE%\Desktop\Omega.lnk" (
        echo [Updating desktop shortcut icon...]
        call UPDATE_DESKTOP_SHORTCUT_ICON.bat
    ) else (
        echo [!] Desktop shortcut not found
        echo     Run CREATE_DESKTOP_SHORTCUT.bat first
    )
) else (
    echo [!] Skipped - Icon file required first
)

echo.
echo ========================================
echo   OPTIMIZATION TASKS CHECK COMPLETE
echo ========================================
echo.
pause
