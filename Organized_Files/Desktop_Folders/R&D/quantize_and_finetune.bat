@echo off
REM Model Quantization and Fine-tuning Script
REM This script performs the following steps:
REM 1. Convert model to lower quantization (Q3_K_S)
REM 2. Fine-tune with 4-bit LoRA using Unsloth
REM 3. Merge and re-quantize the fine-tuned model

echo ============================================================
echo Model Quantization and Fine-tuning Pipeline
echo ============================================================
echo.

REM Set paths (adjust if needed)
set LLAMA_CPP_DIR=.\llama.cpp
set MODELS_DIR=.\models
set INPUT_MODEL=%MODELS_DIR%\Llama-3.2-70B-Instruct-Q4_K_M.gguf
set OUTPUT_MODEL_Q3=%MODELS_DIR%\omega-70b-q3ks.gguf

REM Step 1: Convert to lower quant
echo [Step 1/3] Converting model to Q3_K_S quantization...

REM Check for quantize tool in various locations
set QUANTIZE_TOOL=
if exist "%LLAMA_CPP_DIR%\build\bin\Release\quantize.exe" (
    set QUANTIZE_TOOL=%LLAMA_CPP_DIR%\build\bin\Release\quantize.exe
) else if exist "%LLAMA_CPP_DIR%\build\Release\quantize.exe" (
    set QUANTIZE_TOOL=%LLAMA_CPP_DIR%\build\Release\quantize.exe
) else if exist "%LLAMA_CPP_DIR%\quantize.exe" (
    set QUANTIZE_TOOL=%LLAMA_CPP_DIR%\quantize.exe
) else if exist "%LLAMA_CPP_DIR%\quantize" (
    set QUANTIZE_TOOL=%LLAMA_CPP_DIR%\quantize
) else (
    where quantize.exe >nul 2>&1
    if not errorlevel 1 (
        set QUANTIZE_TOOL=quantize.exe
    )
)

if "%QUANTIZE_TOOL%"=="" (
    echo ERROR: llama.cpp quantize tool not found!
    echo.
    echo Please ensure llama.cpp is built and quantize tool is available.
    echo Checked locations:
    echo   %LLAMA_CPP_DIR%\build\bin\Release\quantize.exe
    echo   %LLAMA_CPP_DIR%\build\Release\quantize.exe
    echo   %LLAMA_CPP_DIR%\quantize.exe
    echo   %LLAMA_CPP_DIR%\quantize
    echo   (or in PATH as quantize.exe)
    echo.
    echo Run setup_quantization_tools.bat to install and build llama.cpp
    pause
    exit /b 1
)

echo Using quantize tool: %QUANTIZE_TOOL%
if not exist "%INPUT_MODEL%" (
    echo ERROR: Input model not found: %INPUT_MODEL%
    pause
    exit /b 1
)

"%QUANTIZE_TOOL%" "%INPUT_MODEL%" "%OUTPUT_MODEL_Q3%" Q3_K_S

if errorlevel 1 (
    echo ERROR: Quantization failed!
    pause
    exit /b 1
)

echo.
echo [Step 2/3] Fine-tuning with 4-bit LoRA using Unsloth...
unsloth-train --model omega-70b-q3ks.gguf --lora-r 16 --quant 4bit --data your_farm_dataset.jsonl

if errorlevel 1 (
    echo ERROR: Fine-tuning failed!
    pause
    exit /b 1
)

echo.
echo [Step 3/3] Merging and re-quantizing...
set MERGED_MODEL=omega-70b-lora-merged.gguf
set FINAL_MODEL=omega-final-q3ks.gguf

if not exist "%MERGED_MODEL%" (
    echo ERROR: Merged model not found: %MERGED_MODEL%
    echo This should be created by the fine-tuning step.
    pause
    exit /b 1
)

"%QUANTIZE_TOOL%" "%MERGED_MODEL%" "%FINAL_MODEL%" Q3_K_S

if errorlevel 1 (
    echo ERROR: Final quantization failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Pipeline completed successfully!
echo ============================================================
pause
