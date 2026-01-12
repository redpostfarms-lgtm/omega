@echo off
echo ================================================================================
echo Omega Scan Integration System
echo ================================================================================
echo.
echo Running full scan integration pipeline:
echo   1. Scan - Look for errors and red flags
echo   2. Optimize - Optimize based on findings
echo   3. Quantum Web Scrape - Research improvements
echo   4. Integrate - Integrate findings
echo   5. Repeat Scan - Verify integration
echo   6. Finish Up - Complete and report
echo.
echo ================================================================================
echo.

python omega_scan_integration.py --root "." --output "SCAN_INTEGRATION_REPORT.md"

echo.
echo ================================================================================
echo Scan Integration Complete!
echo Check SCAN_INTEGRATION_REPORT.md for detailed results
echo ================================================================================
pause
