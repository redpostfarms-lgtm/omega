@echo off
echo ============================================================
echo FARMHUB 2026 - QUANTUM MODULE TEST
echo ============================================================
echo.

REM Test quantum optimizer directly
echo [1/2] Testing quantum optimizer...
python test_quantum_quick.py

echo.
echo [2/2] Starting FarmHub (type 'quantum' to test, 'quit' to exit)
echo ============================================================
echo.

python "The Gatekeeper\FarmHub\FarmHub_2026_Final.py"
