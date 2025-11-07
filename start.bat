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
set GITHUB_RELEASES_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/latest/download/pretrained_models.zip
set MAX_ZIP_PARTS=10

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
    if "!LATEST_VERSION!"=="unknown" (
        echo Note: Could not determine version, but download may still work.
        echo.
    ) else (
        echo Latest release version: !LATEST_VERSION!
        echo.
    )
) else if not "!CURRENT_VERSION!"=="" (
    echo Checking for updates...
    echo Current version: !CURRENT_VERSION!
    call :GetLatestVersion
    
    if "!LATEST_VERSION!"=="unknown" (
        echo Note: Could not check for updates. You can still download manually if needed.
        echo.
    ) else if not "!CURRENT_VERSION!"=="!LATEST_VERSION!" (
        set VERSION_MISMATCH=1
        echo Latest version: !LATEST_VERSION!
        echo.
        echo A different version of pretrained models is available.
        echo.
    ) else (
        echo Latest version: !LATEST_VERSION!
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
    echo No pretrained model files found in the pretrained_models directory.
    echo.
    
    if "!LATEST_VERSION!"=="unknown" (
        echo ERROR: Could not fetch latest release from GitHub.
        echo.
        echo You can try downloading manually from:
        echo https://github.com/%REPO_OWNER%/%REPO_NAME%/releases
        echo.
        set /p try_anyway="Try downloading anyway? (y/n): "
        if /i not "!try_anyway!"=="y" (
            pause
            exit /b 1
        )
    )
    
    echo Would you like to automatically download them from GitHub releases?
    if not "!LATEST_VERSION!"=="unknown" (
        echo Latest version: !LATEST_VERSION!
    )
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
    echo Current version: !CURRENT_VERSION!
    echo Latest version: !LATEST_VERSION!
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
python app\web_app.py --model_dir pretrained_models

REM Auto-open the web page in the default browser
start http://127.0.0.1:5000

pause
exit /b 0

:GetLatestVersion
REM Fetch latest release version from GitHub
REM We'll try to get the version info by downloading a small test request
set TEMP_REDIRECT=%TEMP%\github_redirect.txt

REM Use PowerShell to follow the redirect and get the final URL
powershell -Command "$response = Invoke-WebRequest -Uri 'https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/latest' -MaximumRedirection 1 -ErrorAction SilentlyContinue; if ($response) { $finalUrl = $response.BaseResponse.ResponseUri.AbsoluteUri; $tag = ($finalUrl -split '/')[-1]; Write-Output $tag } else { Write-Output 'unknown' }" > "%TEMP_REDIRECT%" 2>NUL

if errorlevel 1 (
    echo Warning: Could not fetch latest version from GitHub.
    set LATEST_VERSION=unknown
    set RELEASE_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/latest/download/pretrained_models.zip
    del /f /q "%TEMP_REDIRECT%" >NUL 2>&1
    exit /b 0
)

REM Read the version tag from temp file
for /f "tokens=*" %%a in ('type "%TEMP_REDIRECT%"') do set LATEST_VERSION=%%a

if "!LATEST_VERSION!"=="" (
    set LATEST_VERSION=unknown
    set RELEASE_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/latest/download/pretrained_models.zip
    del /f /q "%TEMP_REDIRECT%" >NUL 2>&1
    exit /b 0
)

del /f /q "%TEMP_REDIRECT%" >NUL 2>&1

if "!LATEST_VERSION!"=="" (
    set LATEST_VERSION=unknown
    set RELEASE_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/latest/download/pretrained_models.zip
    exit /b 0
)

REM Set the download URL for the latest version
set RELEASE_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/download/!LATEST_VERSION!/pretrained_models.zip

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
    echo Current version: !OLD_VERSION!
    echo Target version: !LATEST_VERSION!
    echo.
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

REM Try downloading split zip files (for releases split due to GitHub size limits)
echo Checking for model archives...
if not "!LATEST_VERSION!"=="unknown" (
    echo Target version: !LATEST_VERSION!
)
echo.

set ZIP_COUNT=0
set DOWNLOAD_SUCCESS=0

REM First, try the single zip file (backward compatibility)
set SINGLE_ZIP_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/download/!LATEST_VERSION!/pretrained_models.zip
if "!LATEST_VERSION!"=="unknown" (
    set SINGLE_ZIP_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/latest/download/pretrained_models.zip
)

echo Checking for single archive: pretrained_models.zip
powershell -Command "& {try { $response = Invoke-WebRequest -Uri '%SINGLE_ZIP_URL%' -Method Head -UseBasicParsing -ErrorAction Stop; exit 0 } catch { exit 1 }}" >NUL 2>&1

if not errorlevel 1 (
    echo Found: pretrained_models.zip
    echo.
    echo Downloading models from GitHub releases...
    echo.
    
    set TEMP_ZIP=%TEMP%\pretrained_models.zip
    
    powershell -Command "& {try { Write-Host 'Downloading...'; Invoke-WebRequest -Uri '%SINGLE_ZIP_URL%' -OutFile '%TEMP_ZIP%' -UseBasicParsing; exit 0 } catch { Write-Host 'Download failed:' $_.Exception.Message; exit 1 }}"
    
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
    set DOWNLOAD_SUCCESS=1
    goto :ExtractModels
)

REM If single zip not found, try split archives
echo Single archive not found. Checking for split archives...
echo.

REM Detect how many parts exist
set /a PART_NUM=1
:DetectParts
if !PART_NUM! GTR %MAX_ZIP_PARTS% goto :StartDownload

set PART_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/download/!LATEST_VERSION!/pretrained_models_!PART_NUM!.zip
if "!LATEST_VERSION!"=="unknown" (
    set PART_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/latest/download/pretrained_models_!PART_NUM!.zip
)

powershell -Command "& {try { $response = Invoke-WebRequest -Uri '%PART_URL%' -Method Head -UseBasicParsing -ErrorAction Stop; exit 0 } catch { exit 1 }}" >NUL 2>&1

if errorlevel 1 (
    set /a ZIP_COUNT=!PART_NUM!-1
    goto :StartDownload
)

set /a PART_NUM+=1
goto :DetectParts

:StartDownload
if %ZIP_COUNT%==0 (
    echo.
    echo ERROR: No model archives found.
    
    REM Restore backup if it exists
    if not "!OLD_VERSION!"=="" (
        echo Restoring backup...
        xcopy "!BACKUP_DIR!\*" "%MODELS_DIR%\" /E /I /Q /H /Y >NUL 2>&1
        rmdir /s /q "!BACKUP_DIR!" >NUL 2>&1
        echo Backup restored.
    )
    
    echo Please check that the release exists.
    echo Manual download URL: https://github.com/%REPO_OWNER%/%REPO_NAME%/releases
    exit /b 1
)

echo Found %ZIP_COUNT% split archive(s): pretrained_models_1.zip to pretrained_models_%ZIP_COUNT%.zip
echo.
echo Downloading %ZIP_COUNT% part(s)...
echo.

REM Download each part
set /a CURRENT_PART=1
:DownloadLoop
if !CURRENT_PART! GTR %ZIP_COUNT% goto :AllDownloaded

set PART_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/download/!LATEST_VERSION!/pretrained_models_!CURRENT_PART!.zip
if "!LATEST_VERSION!"=="unknown" (
    set PART_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%/releases/latest/download/pretrained_models_!CURRENT_PART!.zip
)

set TEMP_ZIP=%TEMP%\pretrained_models_!CURRENT_PART!.zip

echo [Part !CURRENT_PART!/%ZIP_COUNT%] Downloading pretrained_models_!CURRENT_PART!.zip...

powershell -Command "& {try { Invoke-WebRequest -Uri '%PART_URL%' -OutFile '%TEMP_ZIP%' -UseBasicParsing; exit 0 } catch { Write-Host 'Download failed:' $_.Exception.Message; exit 1 }}"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to download part !CURRENT_PART!.
    
    REM Clean up any downloaded parts
    set /a CLEANUP_PART=1
    :CleanupLoop
    if !CLEANUP_PART! GEQ !CURRENT_PART! goto :CleanupDone
    del /f /q "%TEMP%\pretrained_models_!CLEANUP_PART!.zip" >NUL 2>&1
    set /a CLEANUP_PART+=1
    goto :CleanupLoop
    
    :CleanupDone
    REM Restore backup if it exists
    if not "!OLD_VERSION!"=="" (
        echo Restoring backup...
        xcopy "!BACKUP_DIR!\*" "%MODELS_DIR%\" /E /I /Q /H /Y >NUL 2>&1
        rmdir /s /q "!BACKUP_DIR!" >NUL 2>&1
        echo Backup restored.
    )
    
    echo Please check your internet connection.
    echo Manual download URL: https://github.com/%REPO_OWNER%/%REPO_NAME%/releases
    exit /b 1
)

echo [Part !CURRENT_PART!/%ZIP_COUNT%] Download complete!
echo.

set /a CURRENT_PART+=1
goto :DownloadLoop

:AllDownloaded
echo All parts downloaded successfully!
echo.
set DOWNLOAD_SUCCESS=1

:ExtractModels

REM Extract all downloaded zip files
if %ZIP_COUNT% GTR 0 (
    echo Extracting %ZIP_COUNT% archive part(s)...
    echo.
) else (
    echo Extracting models...
    echo.
)

set TEMP_EXTRACT=%TEMP%\pretrained_models_extract

REM Clean up temp extract directory if it exists
if exist "%TEMP_EXTRACT%" rmdir /s /q "%TEMP_EXTRACT%"
mkdir "%TEMP_EXTRACT%"

if %ZIP_COUNT% GTR 0 (
    REM Extract split archives
    set /a EXTRACT_PART=1
    :ExtractLoop
    if !EXTRACT_PART! GTR %ZIP_COUNT% goto :ExtractionDone
    
    set TEMP_ZIP=%TEMP%\pretrained_models_!EXTRACT_PART!.zip
    
    echo [Part !EXTRACT_PART!/%ZIP_COUNT%] Extracting pretrained_models_!EXTRACT_PART!.zip...
    
    powershell -Command "& {try { Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%TEMP_EXTRACT%' -Force; exit 0 } catch { Write-Host 'Extraction failed:' $_.Exception.Message; exit 1 }}"
    
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to extract part !EXTRACT_PART!.
        
        REM Clean up downloaded parts
        set /a CLEANUP_PART=1
        :CleanupExtractLoop
        if !CLEANUP_PART! GTR %ZIP_COUNT% goto :CleanupExtractDone
        del /f /q "%TEMP%\pretrained_models_!CLEANUP_PART!.zip" >NUL 2>&1
        set /a CLEANUP_PART+=1
        goto :CleanupExtractLoop
        
        :CleanupExtractDone
        rmdir /s /q "%TEMP_EXTRACT%" >NUL 2>&1
        
        REM Restore backup if it exists
        if not "!OLD_VERSION!"=="" (
            echo Restoring backup...
            xcopy "!BACKUP_DIR!\*" "%MODELS_DIR%\" /E /I /Q /H /Y >NUL 2>&1
            rmdir /s /q "!BACKUP_DIR!" >NUL 2>&1
            echo Backup restored.
        )
        
        exit /b 1
    )
    
    echo [Part !EXTRACT_PART!/%ZIP_COUNT%] Extraction complete!
    echo.
    
    set /a EXTRACT_PART+=1
    goto :ExtractLoop
) else (
    REM Extract single archive
    set TEMP_ZIP=%TEMP%\pretrained_models.zip
    
    powershell -Command "& {try { Write-Host 'Extracting...'; Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%TEMP_EXTRACT%' -Force; exit 0 } catch { Write-Host 'Extraction failed:' $_.Exception.Message; exit 1 }}"
    
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
    
    echo Extraction complete!
    echo.
)

:ExtractionDone
REM Move extracted files to pretrained_models directory root
echo Moving files to pretrained_models directory...
xcopy "%TEMP_EXTRACT%\*" "%MODELS_DIR%\" /E /I /Q /H /Y >NUL 2>&1

REM Clean up temp files
if %ZIP_COUNT% GTR 0 (
    set /a CLEANUP_PART=1
    :FinalCleanupLoop
    if !CLEANUP_PART! GTR %ZIP_COUNT% goto :FinalCleanupDone
    del /f /q "%TEMP%\pretrained_models_!CLEANUP_PART!.zip" >NUL 2>&1
    set /a CLEANUP_PART+=1
    goto :FinalCleanupLoop
    :FinalCleanupDone
) else (
    del /f /q "%TEMP%\pretrained_models.zip" >NUL 2>&1
)

rmdir /s /q "%TEMP_EXTRACT%" >NUL 2>&1

echo Files moved successfully!
echo.

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
