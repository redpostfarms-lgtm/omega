@echo off
REM Hands-Free Omega - Just talk, no buttons needed!
cd /d "%~dp0"

title Hands-Free Omega - Just Talk!

color 0B
echo.
echo ========================================
echo   HANDS-FREE OMEGA - JUST TALK!
echo ========================================
echo.
echo 🎤 COMPLETELY HANDS-FREE MODE
echo    • Just speak - I'll detect automatically
echo    • No buttons, no clicks, no presses
echo    • Natural conversation flow
echo.
echo 💡 How it works:
echo    • I listen continuously
echo    • When you speak, I detect it automatically
echo    • When you stop, I process and respond
echo    • Then I listen again for your next turn
echo.
echo 🔄 Improvement Cycle:
echo    • Every 3 conversations, I analyze and improve
echo    • Voice quality gets better automatically
echo.
echo 🛑 To exit: Say "goodbye" or "exit" or press Ctrl+C
echo.
pause

echo.
echo [Starting Hands-Free Omega...]
echo.

py -3.11 hands_free_omega.py

echo.
echo ========================================
echo   Conversation ended
echo ========================================
pause
