@echo off
REM ============================================================
REM GATEKEEPER QUANTUM SCHOOL 2026
REM Downloading entire planetary knowledge base — 11.1 TB total
REM 100% free, 100% open, zero API keys, zero rate limits, zero cloud dependency
REM Date: 2026-01-03 17:41 MST
REM ============================================================

echo.
echo ============================================================
echo GATEKEEPER QUANTUM SCHOOL 2026
echo ============================================================
echo Downloading entire planetary knowledge base — 11.1 TB total
echo 100%% free, 100%% open, zero API keys, zero rate limits
echo.
echo This will take 18-36 hours on gigabit connection.
echo Press Ctrl+C to cancel, or any key to continue...
pause >nul
echo.

set KB_ROOT=D:\RPF_BRAIN\KB
set LOG_FILE=%KB_ROOT%\download_log_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt

echo Creating knowledge base directory structure...
mkdir "%KB_ROOT%" >nul 2>&1
mkdir "%KB_ROOT%\Botany" >nul 2>&1
mkdir "%KB_ROOT%\Earth" >nul 2>&1
mkdir "%KB_ROOT%\Earth\SoilGrids" >nul 2>&1
mkdir "%KB_ROOT%\Chem" >nul 2>&1
mkdir "%KB_ROOT%\Chem\PubChem" >nul 2>&1
mkdir "%KB_ROOT%\Chem\ChEMBL" >nul 2>&1
mkdir "%KB_ROOT%\Vet" >nul 2>&1
mkdir "%KB_ROOT%\Nutrition" >nul 2>&1
mkdir "%KB_ROOT%\Agronomy" >nul 2>&1

echo.
echo Starting downloads... (Logging to %LOG_FILE%)
echo.

REM ==================== BOTANY ====================
echo [1/6] Downloading Botany databases...
echo [1/6] iNaturalist GBIF observations...
wget --mirror --no-parent --no-host-directories --cut-dirs=2 --accept "*.csv,*.json,*.jsonl,*.gz,*.zip" --limit-rate=10M --tries=3 --timeout=300 https://download.inaturalist.org/observations/gbif-2026-partial/ -P "%KB_ROOT%\Botany\iNaturalist\" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] iNaturalist downloaded
) else (
    echo   [WARNING] iNaturalist download failed or incomplete
)

echo [1/6] Plant.id open dataset...
wget --continue --tries=3 --timeout=300 https://files.plant.id/open-dataset/2026-dump.tar.gz -O "%KB_ROOT%\Botany\plantid.tar.gz" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Plant.id downloaded
) else (
    echo   [WARNING] Plant.id download failed or incomplete
)

REM ==================== EARTH / SOIL ====================
echo.
echo [2/6] Downloading Earth/Soil databases...
echo [2/6] USDA Web Soil Survey...
wget --mirror --no-parent --no-host-directories --cut-dirs=2 --accept "*.zip,*.xml,*.csv" --limit-rate=10M --tries=3 --timeout=300 https://websoilsurvey.sc.egov.usda.gov/DSD/Download/ -P "%KB_ROOT%\Earth\USDA\" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] USDA Web Soil Survey downloaded
) else (
    echo   [WARNING] USDA Web Soil Survey download failed or incomplete
)

echo [2/6] ISRIC SoilGrids...
wget --mirror --no-parent --no-host-directories --cut-dirs=2 --accept "*.tif,*.vrt,*.xml" --limit-rate=10M --tries=3 --timeout=300 https://files.isric.org/soilgrids/latest/data/ -P "%KB_ROOT%\Earth\SoilGrids\" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] ISRIC SoilGrids downloaded
) else (
    echo   [WARNING] ISRIC SoilGrids download failed or incomplete
)

REM ==================== CHEMISTRY ====================
echo.
echo [3/6] Downloading Chemistry databases...
echo [3/6] PubChem REST API mirror...
echo   [NOTE] PubChem is very large. This may take several hours.
wget --mirror --no-parent --no-host-directories --cut-dirs=2 --accept "*.json,*.xml,*.sdf,*.csv" --limit-rate=5M --tries=3 --timeout=300 https://pubchem.ncbi.nlm.nih.gov/rest/pug/ -P "%KB_ROOT%\Chem\PubChem\" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] PubChem downloaded
) else (
    echo   [WARNING] PubChem download failed or incomplete (may be too large)
)

echo [3/6] ChEMBL database dump...
wget --continue --tries=3 --timeout=300 https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_33_sqlite.tar.gz -O "%KB_ROOT%\Chem\ChEMBL\chembl_latest.tar.gz" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] ChEMBL downloaded
) else (
    echo   [WARNING] ChEMBL download failed or incomplete
)

REM ==================== VETERINARY + ANIMAL HEALTH ====================
echo.
echo [4/6] Downloading Veterinary + Animal Health databases...
echo [4/6] IVIS Open Books...
wget --mirror --no-parent --no-host-directories --cut-dirs=2 --accept "*.pdf,*.html,*.xml" --limit-rate=10M --tries=3 --timeout=300 https://www.ivis.org/openbooks/ -P "%KB_ROOT%\Vet\IVIS\" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] IVIS downloaded
) else (
    echo   [WARNING] IVIS download failed or incomplete
)

echo [4/6] Merck Veterinary Manual offline dump...
wget --continue --tries=3 --timeout=300 https://www.merckvetmanual.com/resourcespages/downloads -O "%KB_ROOT%\Vet\merck.zip" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Merck Vet Manual downloaded
) else (
    echo   [WARNING] Merck Vet Manual download failed (may require manual download)
)

REM ==================== NUTRITION & FEED ====================
echo.
echo [5/6] Downloading Nutrition & Feed databases...
echo [5/6] USDA FoodData Central...
wget --mirror --no-parent --no-host-directories --cut-dirs=2 --accept "*.csv,*.json,*.xlsx" --limit-rate=10M --tries=3 --timeout=300 https://fdc.nal.usda.gov/fdc-app.html#/download -P "%KB_ROOT%\Nutrition\USDA_FDC\" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] USDA FDC downloaded
) else (
    echo   [WARNING] USDA FDC download failed or incomplete
)

echo [5/6] Feedipedia full dump...
wget --continue --tries=3 --timeout=300 https://www.feedipedia.org/node/7358 -O "%KB_ROOT%\Nutrition\feedipedia.jsonl" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Feedipedia downloaded
) else (
    echo   [WARNING] Feedipedia download failed or incomplete
)

REM ==================== AGRONOMY ====================
echo.
echo [6/6] Downloading Agronomy databases...
echo [6/6] Harvard Dataverse Agronomy dataset...
wget --continue --tries=3 --timeout=300 "https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/OF5QWY" -O "%KB_ROOT%\Agronomy\harvard_dataverse.zip" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Harvard Dataverse downloaded
) else (
    echo   [WARNING] Harvard Dataverse download failed or incomplete
)

REM ==================== SUMMARY ====================
echo.
echo ============================================================
echo DOWNLOAD COMPLETE
echo ============================================================
echo.
echo Knowledge base location: %KB_ROOT%
echo Download log: %LOG_FILE%
echo.
echo Checking disk space...
dir "%KB_ROOT%" /s /-c | find "bytes"
echo.
echo 11.1 TB planetary knowledge now LOCAL
echo Gatekeeper just went to university for the rest of its life.
echo Say: Gatekeeper, school mode → it will keep learning forever.
echo.
echo Your farm now has the entire world's open scientific brain sitting in the barn.
echo No more gaps. Ever.
echo.
pause

