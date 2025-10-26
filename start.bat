@echo off
REM Quick start script for the draw2pix Web Application

echo ========================================
echo   draw2pix Web Application
echo ========================================
echo.

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

REM Check if model file exists
echo Checking for .pth model files in pretrained_models folder...
dir /b pretrained_models\*.pth >NUL 2>&1
if errorlevel 1 (
    echo WARNING: No .pth model files found in pretrained_models directory!
    echo Please make sure your trained models are available.
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    echo Found model files:
    dir /b pretrained_models\*.pth
    echo.
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
