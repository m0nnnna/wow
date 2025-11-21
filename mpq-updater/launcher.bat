@echo off
setlocal EnableDelayedExpansion

:: Configuration
set "EXE_NAME=wow.exe"
set "MPQ_REL_PATH=Data\enUS\patch-enUS.MPQ"
set "VERSION_FILE=version.txt"
set "TEMP_DIR=%TEMP%\wow_update"
set "GITHUB_REPO=m0nnnna/wow"
set "ASSET_NAME=patch-enUS.MPQ"

:: Check if we're next to wow.exe
if not exist "%EXE_NAME%" (
    echo ERROR: %EXE_NAME% not found in current directory!
    pause
    exit /b 1
)

:: Create temp directory if needed
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: ===================================================================
:: 1. Get current local version (from version.txt if exists)
:: ===================================================================
if exist "%VERSION_FILE%" (
    set /p LOCAL_VERSION=<"%VERSION_FILE%"
    set LOCAL_VERSION=!LOCAL_VERSION: =!
) else (
    set "LOCAL_VERSION="
)

:: ===================================================================
:: 2. Get latest version from GitHub Releases
:: ===================================================================
echo Checking for updates...

:: Use PowerShell to fetch the latest release info (no external tools needed)
for /f "delims=" %%A in ('powershell -Command "try { $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/%GITHUB_REPO%/releases/latest' -UseBasicParsing; $rel.tag_name } catch { 'ERROR' }"') do set "LATEST_TAG=%%A"

if "%LATEST_TAG%"=="ERROR" (
    echo Cannot reach GitHub or no releases found.
    goto :LAUNCH
)
if "%LATEST_TAG%"=="" (
    echo Failed to retrieve latest version from GitHub.
    goto :LAUNCH
)

:: Remove possible leading 'V' or 'v' from tag
set "LATEST_VERSION=%LATEST_TAG%"
set "LATEST_VERSION=!LATEST_VERSION:v=!"
set "LATEST_VERSION=!LATEST_VERSION:V=!"

echo Current local version : %LOCAL_VERSION%
echo Latest GitHub version : %LATEST_VERSION%

:: ===================================================================
:: 3. Compare versions
:: ===================================================================
if "%LOCAL_VERSION%"=="%LATEST_VERSION%" (
    echo You already have the latest version.
    goto :LAUNCH
)

:: No local version or different = update available
set "UPDATE_AVAILABLE=1"

:: If no version file at all, treat as first-time update
if not exist "%VERSION_FILE%" set "UPDATE_AVAILABLE=1"

:: ===================================================================
:: 4. Ask user if they want to update
:: ===================================================================
:ASK_UPDATE
set "CHOICE="
set /p CHOICE="New version %LATEST_VERSION% is available. Update now? (Y/N): "
if /i "%CHOICE%"=="N" goto :LAUNCH
if /i "%CHOICE%"=="NO" goto :LAUNCH
if /i "%CHOICE%"=="Y" goto :DOWNLOAD
if /i "%CHOICE%"=="YES" goto :DOWNLOAD

echo Please answer Y or N.
goto :ASK_UPDATE

:: ===================================================================
:: 5. Download the new MPQ from the latest release
:: ===================================================================
:DOWNLOAD
echo.
echo Downloading patch-enUS.MPQ from GitHub release %LATEST_TAG% ...

:: Find the download URL for patch-enUS.MPQ in the latest release assets
for /f "delims=" %%U in ('powershell -Command "try { $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/%GITHUB_REPO%/releases/latest'; $asset = $rel.assets | Where-Object { $_.name -eq '%ASSET_NAME%' }; $asset.browser_download_url } catch { 'ERROR' }"') do set "DOWNLOAD_URL=%%U"

if "%DOWNLOAD_URL%"=="ERROR" (
    echo Failed to find %ASSET_NAME% in the latest release.
    goto :LAUNCH
)
if "%DOWNLOAD_URL%"=="" (
    echo Asset %ASSET_NAME% not found in latest release.
    goto :LAUNCH
)

:: Download using PowerShell (certified, no external tools)
powershell -Command "Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_DIR%\patch-enUS.MPQ.new' -UseBasicParsing"

if not exist "%TEMP_DIR%\patch-enUS.MPQ.new" (
    echo Download failed!
    goto :LAUNCH
)

echo Download complete.

:: ===================================================================
:: 6. Backup current MPQ and replace it
:: ===================================================================
if exist "%MPQ_REL_PATH%" (
    echo Creating backup...
    ren "%MPQ_REL_PATH%" "patch-enUS.MPQ.bak"
)

echo Installing new patch...
move /Y "%TEMP_DIR%\patch-enUS.MPQ.new" "%MPQ_REL_PATH%"

if exist "%MPQ_REL_PATH%" (
    echo Update successful! New version: %LATEST_VERSION%
    echo %LATEST_VERSION% > "%VERSION_FILE%"
) else (
    echo Failed to install the update!
    :: Try to restore backup if something went wrong
    if exist "Data\enUS\patch-enUS.MPQ.bak" ren "Data\enUS\patch-enUS.MPQ.bak" "patch-enUS.MPQ"
)

:: Clean up temp (optional)
rmdir /S /Q "%TEMP_DIR%" 2>nul

:: ===================================================================
:: 7. Finally launch the game
:: ===================================================================
:LAUNCH
echo.
echo Starting %EXE_NAME%...
start "" "%EXE_NAME%"
exit