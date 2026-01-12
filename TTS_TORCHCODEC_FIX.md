# TTS torchcodec Fix Guide

## Current Issue
TTS loads successfully, but fails when generating audio due to torchcodec not being able to load FFmpeg DLLs.

## Status
- ✅ PyTorch downgraded to 2.5.1 (compatible)
- ✅ FFmpeg installed via winget
- ❌ torchcodec still can't load FFmpeg DLLs

## Error Message
```
Could not load this library: 
C:\Users\...\torchcodec\libtorchcodec_core8.dll
```

## Possible Solutions

### Option 1: Manual FFmpeg DLL Copy (Recommended)
1. Find FFmpeg installation location:
   - Usually: `C:\ffmpeg\bin\` or `C:\Program Files\ffmpeg\bin\`
   - Or check: `where ffmpeg` in command prompt

2. Copy FFmpeg DLLs to torchcodec directory:
   ```batch
   copy "C:\ffmpeg\bin\*.dll" "%LOCALAPPDATA%\Programs\Python\Python311\Lib\site-packages\torchcodec\"
   ```

3. Test TTS again: `py -3.11 SIMPLE_TEST.py`

### Option 2: Install FFmpeg Shared Build
torchcodec needs FFmpeg DLLs that are compatible. Try installing a "shared" build:

1. Download FFmpeg shared build from: https://ffmpeg.org/download.html
2. Extract to a location (e.g., `C:\ffmpeg\`)
3. Add to PATH: `C:\ffmpeg\bin`
4. Copy DLLs as in Option 1

### Option 3: Use Alternative TTS Backend
If torchcodec continues to fail, TTS might work with alternative backends or we can disable torchcodec usage.

### Option 4: Wait for torchcodec Update
This might be a compatibility issue that requires a torchcodec update.

## Current Workaround
The TTS model loads successfully, but audio generation fails. The code is ready - once torchcodec DLLs are fixed, TTS will work immediately.

## Next Steps
1. Try Option 1 (copy FFmpeg DLLs)
2. If that doesn't work, try Option 2 (install shared FFmpeg build)
3. Test with: `py -3.11 SIMPLE_TEST.py`
