@echo off
REM Offline Wikipedia + arXiv Mirror
REM Run once → 120 GB compressed → always works when internet dies

echo ============================================================
echo Installing Offline Knowledge Base
echo ============================================================

REM Install Kiwix
echo Installing Kiwix...
winget install kiwix.kiwix-desktop

REM Download knowledge bases (Phase 5 enhancement)
echo.
echo Downloading knowledge bases (this will take a while)...
echo This will download ~120 GB of compressed knowledge bases.
echo.

REM Create download directory
set WIKI_DIR=D:\RPF_BRAIN\Archived\offline_wiki
if not exist "%WIKI_DIR%" mkdir "%WIKI_DIR%"

REM Kiwix ZIM file URLs (Phase 5: Complete URLs)
echo [1/4] Downloading English Wikipedia...
curl -L -o "%WIKI_DIR%\wikipedia_en_all_nopic_2023-10.zim" "https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_nopic_2023-10.zim"
if errorlevel 1 (
    echo [WARNING] Wikipedia download failed. You can download manually from:
    echo https://download.kiwix.org/zim/wikipedia/
)

echo.
echo [2/4] Downloading arXiv papers...
curl -L -o "%WIKI_DIR%\arxiv_en_all_2023-10.zim" "https://download.kiwix.org/zim/other/arxiv_en_all_2023-10.zim"
if errorlevel 1 (
    echo [WARNING] arXiv download failed. You can download manually from:
    echo https://download.kiwix.org/zim/other/
)

echo.
echo [3/4] Downloading Stack Overflow...
curl -L -o "%WIKI_DIR%\stackoverflow_en_all_2023-10.zim" "https://download.kiwix.org/zim/stack_exchange/stackoverflow_en_all_2023-10.zim"
if errorlevel 1 (
    echo [WARNING] Stack Overflow download failed.
)

echo.
echo [4/4] Downloading Gutenberg books...
curl -L -o "%WIKI_DIR%\gutenberg_en_all_2023-10.zim" "https://download.kiwix.org/zim/gutenberg/gutenberg_en_all_2023-10.zim"
if errorlevel 1 (
    echo [WARNING] Gutenberg download failed.
)

echo.
echo Verifying downloads...
dir "%WIKI_DIR%\*.zim"

echo.
echo ============================================================
echo Offline knowledge base installation complete.
echo ============================================================
echo.
echo Total size: ~120 GB compressed
echo Location: %WIKI_DIR%
echo.
echo To use:
echo 1. Open Kiwix Desktop
echo 2. File ^> Open ^> Select .zim files from %WIKI_DIR%
echo 3. All content available offline!
echo.
pause

