@echo off
setlocal enabledelayedexpansion
REM Quick start script for the draw2pix Web Application

echo ========================================
echo   draw2pix Web Application
echo ========================================
echo.

REM Configuration
set REPO_OWNER=Cosmic-Infinity
set REPO_NAME=draw2pix
set MODELS_DIR=pretrained_models
set VERSION_FILE=%MODELS_DIR%\version.txt
set GITHUB_API_URL=https://api.github.com/repos/%REPO_OWNER%/%REPO_NAME%/releases/latest

REM Check if Flask is installed
python -c "import flask" 2>NUL
if errorlevel 1 (
    echo Flask is not installed. Installing now...
    pip install flask
    if errorlevel 1 (
        echo ERROR: Failed to install Flask
        echo Please install manually: pip install flask
        pause
        exit /b 1
    )
)

REM Check if pretrained_models directory exists
if not exist "%MODELS_DIR%" (
    echo Creating pretrained_models directory...
    mkdir "%MODELS_DIR%"
)

REM Check version and model files
set MODELS_MISSING=0
set VERSION_MISMATCH=0
set CURRENT_VERSION=
set LATEST_VERSION=

echo Checking for .pth model files in pretrained_models folder...
dir /b %MODELS_DIR%\*.pth >NUL 2>&1
if errorlevel 1 (
    set MODELS_MISSING=1
) else (
    echo Found model files:
    dir /b %MODELS_DIR%\*.pth
    echo.
)

REM Check local version file
if exist "%VERSION_FILE%" (
    set /p CURRENT_VERSION=<%VERSION_FILE%
    echo Current model version: !CURRENT_VERSION!
) else (
    if %MODELS_MISSING%==0 (
        echo WARNING: No version.txt found in pretrained_models directory.
        echo Cannot check for updates without version information.
        echo.
    )
)

REM Fetch latest version from GitHub if we have a current version or models are missing
if %MODELS_MISSING%==1 (
    echo Fetching latest release information from GitHub...
    call :GetLatestVersion
) else if not "!CURRENT_VERSION!"=="" (
    echo Checking for updates...
    call :GetLatestVersion
    
    if not "!CURRENT_VERSION!"=="!LATEST_VERSION!" (
        if not "!LATEST_VERSION!"=="unknown" (
            set VERSION_MISMATCH=1
            echo Latest model version: !LATEST_VERSION!
            echo A different version of pretrained models is available.
            echo.
        )
    ) else (
        echo Models are up to date.
        echo.
    )
)

REM Handle missing models or version mismatch
if %MODELS_MISSING%==1 (
    echo.
    echo ========================================
    echo   Pretrained Models Not Found
    echo ========================================
    echo No pretrained model files (.pth) found in the pretrained_models directory.
    echo.
    
    if "!LATEST_VERSION!"=="unknown" (
        echo ERROR: Could not fetch latest release from GitHub.
        echo Please download manually from:
        echo https://github.com/%REPO_OWNER%/%REPO_NAME%/releases
        pause
        exit /b 1
    )
    
    echo Would you like to automatically download them from GitHub releases?
    echo Latest version: !LATEST_VERSION!
    echo.
    set /p download_choice="Download models now? (y/n): "
    
    if /i "!download_choice!"=="y" (
        call :DownloadAndExtractModels ""
        if errorlevel 1 (
            echo.
            echo ERROR: Failed to download or extract models.
            echo Please download manually from:
            echo https://github.com/%REPO_OWNER%/%REPO_NAME%/releases
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Cannot start without pretrained models.
        echo Please download them manually from:
        echo https://github.com/%REPO_OWNER%/%REPO_NAME%/releases
        pause
        exit /b 1
    )
) else if %VERSION_MISMATCH%==1 (
    echo.
    set /p update_choice="Would you like to download the latest version? (y/n): "
    
    if /i "!update_choice!"=="y" (
        call :DownloadAndExtractModels "!CURRENT_VERSION!"
        if errorlevel 1 (
            echo.
            echo ERROR: Failed to download or extract models.
            pause
            exit /b 1
        )
    )
)

echo.
echo Starting web application...
echo All .pth models in the pretrained_models directory will be loaded.
echo.
echo The application will open at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the web application (loads all .pth files in pretrained_models directory)
python web_app.py --model_dir pretrained_models

pause
exit /b 0

:GetLatestVersion
REM Fetch latest release version from GitHub API
set TEMP_JSON=%TEMP%\github_release.json

powershell -Command "& {try { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%GITHUB_API_URL%' -OutFile '%TEMP_JSON%' -UseBasicParsing; exit 0 } catch { exit 1 }}" >NUL 2>&1

if errorlevel 1 (
    set LATEST_VERSION=unknown
    exit /b 1
)

REM Parse JSON to get tag_name and download URL
for /f "tokens=*" %%a in ('powershell -Command "& {$json = Get-Content '%TEMP_JSON%' -Raw | ConvertFrom-Json; Write-Output $json.tag_name}"') do set LATEST_VERSION=%%a
for /f "tokens=*" %%a in ('powershell -Command "& {$json = Get-Content '%TEMP_JSON%' -Raw | ConvertFrom-Json; $asset = $json.assets | Where-Object {$_.name -eq 'pretrained_models.zip'}; if ($asset) {Write-Output $asset.browser_download_url}}"') do set RELEASE_URL=%%a

del /f /q "%TEMP_JSON%" >NUL 2>&1

if "!RELEASE_URL!"=="" (
    set LATEST_VERSION=unknown
    exit /b 1
)

exit /b 0

:DownloadAndExtractModels
set OLD_VERSION=%~1
echo.
echo ========================================
echo   Downloading Pretrained Models
echo ========================================
echo.

REM Check for PowerShell (required for download)
where powershell >NUL 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is required for automatic download.
    echo Please download manually from:
    echo https://github.com/%REPO_OWNER%/%REPO_NAME%/releases
    exit /b 1
)

REM Backup existing models if version exists
if not "!OLD_VERSION!"=="" (
    set BACKUP_DIR=pretrained_models_old_!OLD_VERSION!
    echo Backing up current models to !BACKUP_DIR!...
    
    if exist "!BACKUP_DIR!" (
        echo Warning: Backup directory !BACKUP_DIR! already exists.
        set /p overwrite="Overwrite existing backup? (y/n): "
        if /i not "!overwrite!"=="y" (
            echo Backup cancelled. Aborting update.
            exit /b 1
        )
        rmdir /s /q "!BACKUP_DIR!"
    )
    
    REM Create backup directory and move all files
    mkdir "!BACKUP_DIR!"
    
    REM Move all files from pretrained_models to backup
    xcopy "%MODELS_DIR%\*" "!BACKUP_DIR!\" /E /I /Q /H /Y >NUL 2>&1
    
    REM Clean the pretrained_models directory
    del /f /q %MODELS_DIR%\* >NUL 2>&1
    for /d %%p in (%MODELS_DIR%\*) do rmdir "%%p" /s /q >NUL 2>&1
    
    echo Backup completed: !BACKUP_DIR!\
    echo.
)

REM Download the zip file
echo Downloading models from GitHub releases...
echo Version: !LATEST_VERSION!
echo URL: !RELEASE_URL!
echo.

set TEMP_ZIP=%TEMP%\pretrained_models.zip

powershell -Command "& {try { $ProgressPreference = 'SilentlyContinue'; Write-Host 'Downloading...'; Invoke-WebRequest -Uri '%RELEASE_URL%' -OutFile '%TEMP_ZIP%' -UseBasicParsing; exit 0 } catch { Write-Host 'Download failed:' $_.Exception.Message; exit 1 }}"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to download models.
    
    REM Restore backup if it exists
    if not "!OLD_VERSION!"=="" (
        echo Restoring backup...
        xcopy "!BACKUP_DIR!\*" "%MODELS_DIR%\" /E /I /Q /H /Y >NUL 2>&1
        rmdir /s /q "!BACKUP_DIR!" >NUL 2>&1
        echo Backup restored.
    )
    
    echo Please check your internet connection and ensure the release exists.
    echo Manual download URL: https://github.com/%REPO_OWNER%/%REPO_NAME%/releases
    exit /b 1
)

echo Download complete!
echo.

REM Extract the zip file directly to pretrained_models root
echo Extracting models to pretrained_models directory...
set TEMP_EXTRACT=%TEMP%\pretrained_models_extract

REM Clean up temp extract directory if it exists
if exist "%TEMP_EXTRACT%" rmdir /s /q "%TEMP_EXTRACT%"
mkdir "%TEMP_EXTRACT%"

powershell -Command "& {try { Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%TEMP_EXTRACT%' -Force; exit 0 } catch { Write-Host 'Extraction failed:' $_.Exception.Message; exit 1 }}"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to extract models.
    del /f /q "%TEMP_ZIP%" >NUL 2>&1
    
    REM Restore backup if it exists
    if not "!OLD_VERSION!"=="" (
        echo Restoring backup...
        xcopy "!BACKUP_DIR!\*" "%MODELS_DIR%\" /E /I /Q /H /Y >NUL 2>&1
        rmdir /s /q "!BACKUP_DIR!" >NUL 2>&1
        echo Backup restored.
    )
    
    exit /b 1
)

REM Move extracted files to pretrained_models directory root
echo Moving files to pretrained_models directory...
xcopy "%TEMP_EXTRACT%\*" "%MODELS_DIR%\" /E /I /Q /H /Y >NUL 2>&1

REM Clean up temp files
del /f /q "%TEMP_ZIP%" >NUL 2>&1
rmdir /s /q "%TEMP_EXTRACT%" >NUL 2>&1

REM Verify extraction
dir /b %MODELS_DIR%\*.pth >NUL 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: No .pth files found after extraction.
    echo The zip file structure may be different than expected.
    
    REM Restore backup if it exists
    if not "!OLD_VERSION!"=="" (
        echo Restoring backup...
        del /f /q %MODELS_DIR%\* >NUL 2>&1
        for /d %%p in (%MODELS_DIR%\*) do rmdir "%%p" /s /q >NUL 2>&1
        xcopy "!BACKUP_DIR!\*" "%MODELS_DIR%\" /E /I /Q /H /Y >NUL 2>&1
        rmdir /s /q "!BACKUP_DIR!" >NUL 2>&1
        echo Backup restored.
    )
    
    exit /b 1
)

REM Verify version.txt exists
if not exist "%VERSION_FILE%" (
    echo.
    echo WARNING: version.txt not found in extracted files.
    echo Creating version.txt with downloaded version...
    echo !LATEST_VERSION! > "%VERSION_FILE%"
)

echo.
echo ========================================
echo   Models Downloaded Successfully!
echo ========================================
echo.
echo Installed models:
dir /b %MODELS_DIR%\*.pth
echo.

REM Read and display version
set /p INSTALLED_VERSION=<%VERSION_FILE%
echo Version: !INSTALLED_VERSION!

if not "!OLD_VERSION!"=="" (
    echo.
    echo Old version backed up to: pretrained_models_old_!OLD_VERSION!\
    echo.
    echo The old models are probably not needed anymore.
    set /p delete_backup="Would you like to delete the backup to save space? (y/n): "
    
    if /i "!delete_backup!"=="y" (
        rmdir /s /q "!BACKUP_DIR!" >NUL 2>&1
        echo Backup deleted.
    ) else (
        echo Backup kept at: !BACKUP_DIR!\
    )
)

echo.

exit /b 0
