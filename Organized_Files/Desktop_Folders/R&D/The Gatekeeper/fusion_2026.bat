@echo off
REM GATEKEEPER FUSION 2026
REM Grok + Cursor + DeepSeek + Llama → ONE BRAIN
REM Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved

echo ============================================================
echo GATEKEEPER FUSION 2026
echo Grok + Cursor + DeepSeek + Llama → ONE BRAIN
echo ============================================================
echo.

cd /d "%~dp0"
set GATEKEEPER_DIR=%~dp0

echo [1/5] Creating fusion models directory...
if not exist "%GATEKEEPER_DIR%models" mkdir "%GATEKEEPER_DIR%models"
if not exist "%GATEKEEPER_DIR%models\fusion" mkdir "%GATEKEEPER_DIR%models\fusion"
echo ✅ Directory created

echo.
echo [2/5] Downloading Grok-style model (Llama-3.2-8B)...
echo   Fast + sarcastic reasoning
if not exist "%GATEKEEPER_DIR%models\fusion\grok.gguf" (
    echo   Downloading from HuggingFace...
    echo   URL: https://huggingface.co/TheBloke/Llama-3.2-8B-Instruct-GGUF/resolve/main/Llama-3.2-8B-Instruct-Q5_K_M.gguf
    python -c "import urllib.request; print('Downloading...'); urllib.request.urlretrieve('https://huggingface.co/TheBloke/Llama-3.2-8B-Instruct-GGUF/resolve/main/Llama-3.2-8B-Instruct-Q5_K_M.gguf', r'%GATEKEEPER_DIR%models\fusion\grok.gguf'); print('Download complete')" 2>&1
    if exist "%GATEKEEPER_DIR%models\fusion\grok.gguf" (
        echo   ✅ Grok model downloaded (~5GB)
    ) else (
        echo   ⚠️  Automatic download failed (large file)
        echo   Manual download required:
        echo   URL: https://huggingface.co/TheBloke/Llama-3.2-8B-Instruct-GGUF/resolve/main/Llama-3.2-8B-Instruct-Q5_K_M.gguf
        echo   Save as: %GATEKEEPER_DIR%models\fusion\grok.gguf
    )
) else (
    echo   ✅ Grok model already exists
)

echo.
echo [3/5] Downloading Cursor-style model (Phi-3-mini)...
echo   Tiny + blazing fast code brain
if not exist "%GATEKEEPER_DIR%models\fusion\cursor.gguf" (
    echo   Downloading from HuggingFace...
    echo   URL: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
    python -c "import urllib.request; print('Downloading...'); urllib.request.urlretrieve('https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf', r'%GATEKEEPER_DIR%models\fusion\cursor.gguf'); print('Download complete')" 2>&1
    if exist "%GATEKEEPER_DIR%models\fusion\cursor.gguf" (
        echo   ✅ Cursor model downloaded (~2.3GB)
    ) else (
        echo   ⚠️  Automatic download failed
        echo   Manual download required:
        echo   URL: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
        echo   Save as: %GATEKEEPER_DIR%models\fusion\cursor.gguf
    )
) else (
    echo   ✅ Cursor model already exists
)

echo.
echo [4/5] Downloading DeepSeek model...
echo   Math + long context specialist
if not exist "%GATEKEEPER_DIR%models\fusion\deepseek.gguf" (
    echo   Downloading from HuggingFace...
    echo   URL: https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct-gguf/resolve/main/deepseek-coder-v2-lite-instruct-q5_k_m.gguf
    python -c "import urllib.request; print('Downloading...'); urllib.request.urlretrieve('https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct-gguf/resolve/main/deepseek-coder-v2-lite-instruct-q5_k_m.gguf', r'%GATEKEEPER_DIR%models\fusion\deepseek.gguf'); print('Download complete')" 2>&1
    if exist "%GATEKEEPER_DIR%models\fusion\deepseek.gguf" (
        echo   ✅ DeepSeek model downloaded (~4GB)
    ) else (
        echo   ⚠️  Automatic download failed (large file)
        echo   Manual download required:
        echo   URL: https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct-gguf/resolve/main/deepseek-coder-v2-lite-instruct-q5_k_m.gguf
        echo   Save as: %GATEKEEPER_DIR%models\fusion\deepseek.gguf
    )
) else (
    echo   ✅ DeepSeek model already exists
)

echo.
echo [5/5] Checking llama.cpp installation...
where llama-server.exe >nul 2>&1
if errorlevel 1 (
    echo   ⚠️  llama.cpp server not found in PATH
    echo   Install: https://github.com/ggerganov/llama.cpp
    echo   Or use: pip install llama-cpp-python
) else (
    echo   ✅ llama.cpp server found
)

echo.
echo ============================================================
echo FUSION COMPLETE
echo ============================================================
echo.
echo Gatekeeper now speaks with 4 voices at once:
echo   - Grok: Fast + sarcastic reasoning
echo   - Cursor: Code writing (file-aware)
echo   - DeepSeek: Math + long context
echo   - Llama: Review + compliance
echo.
echo Usage:
echo   "Hey, Gatekeeper, write a quantum-safe BMS in Rust"
echo   "Hey, Gatekeeper, build a 10k-line solar controller"
echo   "Hey, Gatekeeper, code a MPPT algorithm"
echo.
echo All models run locally, in parallel, zero cost, zero cloud.
echo.
pause

