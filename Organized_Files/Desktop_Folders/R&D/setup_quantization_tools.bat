@echo off
REM Setup script for model quantization and fine-tuning tools
REM This script installs and configures llama.cpp and Unsloth

echo ============================================================
echo Setting up Model Quantization and Fine-tuning Tools
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python first.
    pause
    exit /b 1
)
echo [OK] Python found

REM Install Unsloth
echo.
echo [1/3] Installing Unsloth...
python -m pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
if errorlevel 1 (
    echo WARNING: Unsloth installation had issues (may need dependencies)
) else (
    echo [OK] Unsloth installed
)

REM Check for llama.cpp
echo.
echo [2/3] Checking llama.cpp installation...
if exist ".\llama.cpp\quantize.exe" (
    echo [OK] llama.cpp quantize.exe found
    goto :check_model
)
if exist ".\llama.cpp\quantize" (
    echo [OK] llama.cpp quantize found
    goto :check_model
)

echo.
echo llama.cpp tools not found. Options:
echo   1. Clone and build llama.cpp manually:
echo      git clone https://github.com/ggerganov/llama.cpp
echo      cd llama.cpp
echo      mkdir build
echo      cd build
echo      cmake ..
echo      cmake --build . --config Release
echo.
echo   2. Download pre-built binaries from:
echo      https://github.com/ggerganov/llama.cpp/releases
echo.
echo   3. Use llama-cpp-python for quantization (alternative method)
echo.
set /p BUILD_NOW="Build llama.cpp now? (requires Git and CMake) [y/N]: "
if /i "%BUILD_NOW%"=="y" (
    echo.
    echo Cloning llama.cpp...
    git clone https://github.com/ggerganov/llama.cpp
    if errorlevel 1 (
        echo ERROR: Failed to clone llama.cpp
        goto :check_model
    )
    echo Building llama.cpp (this may take a while)...
    cd llama.cpp
    if exist "CMakeLists.txt" (
        mkdir build 2>nul
        cd build
        cmake .. -DCMAKE_BUILD_TYPE=Release
        cmake --build . --config Release
        if errorlevel 1 (
            echo WARNING: Build may have failed. Check build output.
        ) else (
            echo [OK] llama.cpp built successfully
        )
        cd ..\..
    ) else (
        echo ERROR: CMakeLists.txt not found. Manual build required.
        cd ..
    )
)

:check_model
echo.
echo [3/3] Checking model files...
if exist ".\models\Llama-3.2-70B-Instruct-Q4_K_M.gguf" (
    echo [OK] Input model found: .\models\Llama-3.2-70B-Instruct-Q4_K_M.gguf
) else (
    echo [WARNING] Input model not found: .\models\Llama-3.2-70B-Instruct-Q4_K_M.gguf
    echo Please place your model file in the models directory.
)

echo.
echo ============================================================
echo Setup complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Ensure llama.cpp quantize tool is available
echo   2. Place your input model at: .\models\Llama-3.2-70B-Instruct-Q4_K_M.gguf
echo   3. Prepare your dataset: your_farm_dataset.jsonl
echo   4. Run: quantize_and_finetune.bat
echo.
pause
