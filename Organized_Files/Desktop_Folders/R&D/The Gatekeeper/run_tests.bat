@echo off
REM Run Gatekeeper Test Suite

echo ============================================================
echo GATEKEEPER TEST SUITE
echo ============================================================

cd /d "%~dp0"

echo.
echo [1/3] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ⚠️  Some dependencies may be missing
)

echo.
echo [2/3] Running quality checker...
python "The Gatekeeper\quality_improvements.py"
if errorlevel 1 (
    echo ⚠️  Quality check had issues
)

echo.
echo [3/3] Running test suite...
python "The Gatekeeper\test_suite.py"
if errorlevel 1 (
    echo ⚠️  Some tests failed
    exit /b 1
)

echo.
echo ============================================================
echo ✅ ALL TESTS PASSED
echo ============================================================
pause

