# Model Quantization and Fine-tuning Setup Guide

This guide will help you set up the tools needed to run the quantization and fine-tuning pipeline.

## Quick Start

The main script to run is: `quantize_and_finetune.bat`

## Prerequisites

### 1. llama.cpp quantize tool

You have three options:

#### Option A: Download Pre-built Binaries (Easiest)

1. Go to: https://github.com/ggerganov/llama.cpp/releases
2. Download the latest Windows release (e.g., `llama-bXXXX-bin-win-avx2-x64.zip`)
3. Extract the zip file
4. Copy `quantize.exe` to `.\llama.cpp\quantize.exe` in this directory

#### Option B: Build with CMake (Requires CMake)

1. Install CMake: https://cmake.org/download/
2. Install Visual Studio with C++ build tools (or use MinGW)
3. Run:
```cmd
cd llama.cpp
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```
4. The `quantize.exe` will be in `llama.cpp\build\bin\Release\` or `llama.cpp\build\Release\`

#### Option C: Use Visual Studio (If you have VS)

1. Open `llama.cpp\CMakeLists.txt` in Visual Studio
2. Let VS configure CMake
3. Build the `quantize` target
4. Find `quantize.exe` in the build output directory

### 2. Unsloth Installation

Unsloth installation encountered a Windows Long Path issue. To resolve:

#### Enable Windows Long Path Support:

1. Open PowerShell as Administrator
2. Run:
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```
3. Restart your computer
4. Then install Unsloth:
```cmd
python -m pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```

**OR** use an alternative installation location with shorter paths, or install Unsloth in WSL.

### 3. Model File

Place your input model at:
```
.\models\Llama-3.2-70B-Instruct-Q4_K_M.gguf
```

### 4. Dataset File

Prepare your fine-tuning dataset as JSONL format:
```
your_farm_dataset.jsonl
```

Format example:
```jsonl
{"instruction": "...", "input": "...", "output": "..."}
{"instruction": "...", "input": "...", "output": "..."}
```

## Running the Pipeline

Once all prerequisites are met:

```cmd
quantize_and_finetune.bat
```

This will:
1. Convert `Llama-3.2-70B-Instruct-Q4_K_M.gguf` to `omega-70b-q3ks.gguf` (Q3_K_S quantization)
2. Fine-tune with 4-bit LoRA using Unsloth
3. Merge and re-quantize to `omega-final-q3ks.gguf`

## Troubleshooting

### quantize tool not found
- Check that `quantize.exe` exists in one of the expected locations
- Run `python quantize_helper.py` to check for tools
- Use `setup_quantization_tools.bat` for guided setup

### Unsloth installation fails
- Enable Windows Long Path support (see above)
- Or install in WSL/Linux environment
- Or use a shorter installation path

### Model file not found
- Ensure the model is at `.\models\Llama-3.2-70B-Instruct-Q4_K_M.gguf`
- Check file permissions

### Fine-tuning fails
- Verify Unsloth is installed: `python -c "import unsloth; print('OK')"`
- Check dataset format is valid JSONL
- Ensure sufficient disk space (fine-tuning creates temporary files)

## Manual Command Execution

If you prefer to run commands manually:

### Step 1: Quantization
```cmd
.\llama.cpp\quantize.exe .\models\Llama-3.2-70B-Instruct-Q4_K_M.gguf .\models\omega-70b-q3ks.gguf Q3_K_S
```

### Step 2: Fine-tuning
```cmd
unsloth-train --model omega-70b-q3ks.gguf --lora-r 16 --quant 4bit --data your_farm_dataset.jsonl
```

### Step 3: Merge and re-quantize
```cmd
.\llama.cpp\quantize.exe omega-70b-lora-merged.gguf omega-final-q3ks.gguf Q3_K_S
```

## Files Created

- `quantize_and_finetune.bat` - Main pipeline script
- `setup_quantization_tools.bat` - Setup helper script
- `quantize_helper.py` - Python helper to check tools
- `QUANTIZATION_SETUP_GUIDE.md` - This guide

## Next Steps

1. Download or build `quantize.exe` (see Option A above - easiest)
2. Fix Unsloth installation (enable Long Path support)
3. Place your model file in `.\models\`
4. Prepare your dataset file
5. Run `quantize_and_finetune.bat`
